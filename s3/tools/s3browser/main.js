const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const Store = require('electron-store');
const { 
  S3Client, 
  ListBucketsCommand,
  ListObjectsV2Command,
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  DeleteObjectsCommand
} = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');

const store = new Store();

// Set application ID for Windows
if (process.platform === 'win32') {
  app.setAppUserModelId('com.s3browser.app');
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.resolve(__dirname, process.platform === 'darwin' ? 's3icon.icns' : process.platform === 'win32' ? 's3icon.ico' : 's3icon.png'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      devTools: true // Allow DevTools but don't open by default
    }
  });

  mainWindow.loadFile('index.html');

  // Create the application menu
  const template = [
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'delete' },
        { type: 'separator' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', accelerator: 'CmdOrCtrl+R' },
        { role: 'forceReload', accelerator: 'CmdOrCtrl+Shift+R' },
        { type: 'separator' },
        { role: 'toggleDevTools', accelerator: 'CmdOrCtrl+Shift+I' }
      ]
    }
  ];

  // Add macOS specific menu items
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Log errors
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    const levels = ['debug', 'info', 'warning', 'error'];
    console.log(`[${levels[level] || 'info'}] ${message}`);
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// S3 Connection Management
// Connection Management
ipcMain.handle('save-connection', async (event, connection) => {
  const connections = store.get('connections', []);
  connections.push(connection);
  store.set('connections', connections);
  return connections;
});

ipcMain.handle('save-connections', async (event, connections) => {
  store.set('connections', connections);
  return connections;
});

ipcMain.handle('get-connections', async () => {
  return store.get('connections', []);
});

ipcMain.handle('delete-connection', async (event, id) => {
  const connections = store.get('connections', []);
  const updatedConnections = connections.filter(conn => conn.id !== id);
  store.set('connections', updatedConnections);
  return updatedConnections;
});

// File Dialog Operations
ipcMain.handle('show-save-dialog', async () => {
  const result = await dialog.showSaveDialog({
    properties: ['createDirectory']
  });
  return result.filePath;
});

ipcMain.handle('show-open-dialog', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile', 'multiSelections']
  });
  return result.filePaths;
});

// S3 Operations
ipcMain.handle('list-buckets', async (event, connectionId) => {
  const connection = store.get('connections', []).find(conn => conn.id === connectionId);
  if (!connection) throw new Error('Connection not found');

  const client = new S3Client({
    endpoint: connection.endpoint,
    region: connection.region,
    credentials: {
      accessKeyId: connection.accessKey,
      secretAccessKey: connection.secretKey
    }
  });

  try {
    const response = await client.send(new ListBucketsCommand({}));
    return response.Buckets || [];
  } catch (error) {
    console.error('Error listing buckets:', error);
    throw error;
  }
});

ipcMain.handle('list-objects', async (event, connectionId, bucket = null, prefix = '') => {
  const connection = store.get('connections', []).find(conn => conn.id === connectionId);
  if (!connection) throw new Error('Connection not found');

  const client = new S3Client({
    endpoint: connection.endpoint,
    region: connection.region,
    credentials: {
      accessKeyId: connection.accessKey,
      secretAccessKey: connection.secretKey
    }
  });

  // If no bucket is specified, use the connection's default bucket if available
  const targetBucket = bucket || connection.bucket;
  if (!targetBucket) {
    return { type: 'buckets', data: await client.send(new ListBucketsCommand({})).then(res => res.Buckets || []) };
  }

  const command = new ListObjectsV2Command({
    Bucket: targetBucket,
    Prefix: prefix,
    Delimiter: '/'
  });

  try {
    const response = await client.send(command);
    
    // Process folders (CommonPrefixes)
    const folders = (response.CommonPrefixes || []).map(prefix => ({
      Key: prefix.Prefix,
      isFolder: true,
      LastModified: null,
      Size: 0
    }));

    // Process files with additional metadata
    const files = (response.Contents || []).map(obj => ({
      ...obj,
      isFolder: false,
      ContentType: obj.Key.split('.').pop() || 'unknown',
      StorageClass: obj.StorageClass || 'STANDARD'
    }));

    return { 
      type: 'objects', 
      data: [...folders, ...files].filter(item => item.Key !== prefix) // Remove current prefix from list
    };
  } catch (error) {
    console.error('Error listing objects:', error);
    throw error;
  }
});

ipcMain.handle('upload-object', async (event, connectionId, filePath, key, bucket) => {
  const connection = store.get('connections', []).find(conn => conn.id === connectionId);
  if (!connection) throw new Error('Connection not found');

  const fs = require('fs');

  const client = new S3Client({
    endpoint: connection.endpoint,
    region: connection.region,
    credentials: {
      accessKeyId: connection.accessKey,
      secretAccessKey: connection.secretKey
    }
  });

  try {
    const fileStream = fs.createReadStream(filePath);
    const command = new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: fileStream
    });

    await client.send(command);
    return { success: true };
  } catch (error) {
    console.error('Error uploading object:', error);
    throw error;
  }
});

ipcMain.handle('create-folder', async (event, connectionId, bucket, folderPath) => {
  const connection = store.get('connections', []).find(conn => conn.id === connectionId);
  if (!connection) throw new Error('Connection not found');

  const client = new S3Client({
    endpoint: connection.endpoint,
    region: connection.region,
    credentials: {
      accessKeyId: connection.accessKey,
      secretAccessKey: connection.secretKey
    }
  });

  try {
    // Create empty object with trailing slash to represent folder
    const command = new PutObjectCommand({
      Bucket: bucket,
      Key: folderPath.endsWith('/') ? folderPath : `${folderPath}/`,
      Body: ''
    });

    await client.send(command);
    return { success: true };
  } catch (error) {
    console.error('Error creating folder:', error);
    throw error;
  }
});

ipcMain.handle('preview-object', async (event, connectionId, bucket, key) => {
  const connection = store.get('connections', []).find(conn => conn.id === connectionId);
  if (!connection) throw new Error('Connection not found');

  const client = new S3Client({
    endpoint: connection.endpoint,
    region: connection.region,
    credentials: {
      accessKeyId: connection.accessKey,
      secretAccessKey: connection.secretKey
    }
  });

  try {
    const command = new GetObjectCommand({
      Bucket: bucket,
      Key: key
    });

    const ext = key.split('.').pop()?.toLowerCase();

    // For text files, fetch and return content directly
    if (ext.match(/^(txt|json|js|css|xml|md|markdown|yaml|yml|ini|csv|log)$/)) {
      const response = await client.send(command);
      const text = await response.Body.transformToString();
      return { type: 'text', content: text };
    }

    // For all other files, generate a signed URL that expires in 1 hour
    const signedUrl = await getSignedUrl(client, command, { expiresIn: 3600 });
    return { type: ext, content: signedUrl };
  } catch (error) {
    console.error('Error previewing object:', error);
    throw error;
  }
});

ipcMain.handle('download-object', async (event, connectionId, key, bucket) => {
  const connection = store.get('connections', []).find(conn => conn.id === connectionId);
  if (!connection) throw new Error('Connection not found');

  const fs = require('fs');
  const path = require('path');

  const client = new S3Client({
    endpoint: connection.endpoint,
    region: connection.region,
    credentials: {
      accessKeyId: connection.accessKey,
      secretAccessKey: connection.secretKey
    }
  });

  try {
    const command = new GetObjectCommand({
      Bucket: bucket,
      Key: key
    });

    const response = await client.send(command);
    
    // Show save dialog with default filename
    const defaultPath = path.basename(key);
    const { filePath } = await dialog.showSaveDialog({
      defaultPath: defaultPath,
      properties: ['createDirectory']
    });

    if (!filePath) return { success: false, cancelled: true };

    const writeStream = fs.createWriteStream(filePath);
    
    await new Promise((resolve, reject) => {
      response.Body.pipe(writeStream)
        .on('finish', resolve)
        .on('error', reject);
    });

    return { success: true, path: filePath };
  } catch (error) {
    console.error('Error downloading object:', error);
    throw error;
  }
});

ipcMain.handle('delete-object', async (event, connectionId, key, bucket, isFolder = false) => {
  const connection = store.get('connections', []).find(conn => conn.id === connectionId);
  if (!connection) throw new Error('Connection not found');

  const client = new S3Client({
    endpoint: connection.endpoint,
    region: connection.region,
    credentials: {
      accessKeyId: connection.accessKey,
      secretAccessKey: connection.secretKey
    }
  });

  try {
    if (isFolder) {
      let count = 0;
      
      // Ensure the folder key ends with '/'
      const folderKey = key.endsWith('/') ? key : key + '/';
      console.log('Deleting folder:', folderKey);

      // Recursive function to handle pagination
      async function recursiveDelete(token) {
        // List all objects in the folder
        const listCommand = new ListObjectsV2Command({
          Bucket: bucket,
          Prefix: folderKey,
          ContinuationToken: token
        });

        const list = await client.send(listCommand);
        console.log('Found objects:', list.Contents?.length || 0);
        
        if (list.Contents && list.Contents.length > 0) {
          // Delete all objects in this batch
          const deleteCommand = new DeleteObjectsCommand({
            Bucket: bucket,
            Delete: {
              Objects: list.Contents.map((item) => ({ Key: item.Key })),
              Quiet: false
            }
          });

          const deleted = await client.send(deleteCommand);
          count += deleted.Deleted.length;
          console.log(`Deleted ${deleted.Deleted.length} objects in this batch`);

          // Log any errors
          if (deleted.Errors && deleted.Errors.length > 0) {
            deleted.Errors.forEach(error => {
              console.error(`${error.Key} could not be deleted - ${error.Code}`);
            });
          }

          // Continue if there are more files
          if (list.NextContinuationToken) {
            await recursiveDelete(list.NextContinuationToken);
          }
        }
        return count;
      }

      // Start the recursive deletion
      const deletedCount = await recursiveDelete();
      console.log(`Deleted ${deletedCount} files from folder ${folderKey}`);

      // Delete the folder marker itself
      const folderMarkerCommand = new DeleteObjectCommand({
        Bucket: bucket,
        Key: folderKey
      });
      await client.send(folderMarkerCommand);
      console.log(`Deleted folder marker ${folderKey}`);

      return { success: true, message: `${deletedCount} files and folder deleted.` };
    } else {
      const command = new DeleteObjectCommand({
        Bucket: bucket,
        Key: key
      });
      await client.send(command);
      return { success: true, message: 'File deleted.' };
    }
  } catch (error) {
    console.error('Error deleting object:', error);
    throw error;
  }
});
