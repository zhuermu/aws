const { ipcRenderer } = require('electron');

let currentConnection = null;
let currentBucket = null;
let currentPrefix = '';
let selectedFiles = new Set();
let isEditing = false;

// Loading indicators
function showLoading(message = 'Loading...') {
  document.getElementById('loadingOverlay').style.display = 'flex';
  document.getElementById('loadingOverlay').querySelector('.loading-text').textContent = message;
}

function hideLoading() {
  document.getElementById('loadingOverlay').style.display = 'none';
}

function showButtonLoading(buttonId) {
  const button = document.getElementById(buttonId);
  button.disabled = true;
  button.querySelector('.button-spinner').style.display = 'block';
}

function hideButtonLoading(buttonId) {
  const button = document.getElementById(buttonId);
  button.disabled = false;
  button.querySelector('.button-spinner').style.display = 'none';
}

// Connection Management
async function loadConnections() {
  showLoading('Loading connections...');
  try {
    const connections = await ipcRenderer.invoke('get-connections');
    const connectionList = document.getElementById('connectionList');
    connectionList.innerHTML = '';
    
    connections.forEach(conn => {
      const div = document.createElement('div');
      div.className = 'connection-item';
      
      const nameDiv = document.createElement('div');
      nameDiv.className = 'connection-name';
      nameDiv.textContent = conn.name;
      nameDiv.onclick = () => selectConnection(conn);
      
      const actionsDiv = document.createElement('div');
      actionsDiv.className = 'connection-actions';
      
      const editButton = document.createElement('button');
      editButton.className = 'action-button';
      editButton.innerHTML = 'Edit';
      editButton.onclick = (e) => {
        e.stopPropagation();
        editConnection(conn);
      };
      
      const deleteButton = document.createElement('button');
      deleteButton.className = 'action-button';
      deleteButton.innerHTML = 'Delete';
      deleteButton.onclick = async (e) => {
        e.stopPropagation();
        if (confirm('Are you sure you want to delete this connection?')) {
          await ipcRenderer.invoke('delete-connection', conn.id);
          loadConnections();
        }
      };
      
      actionsDiv.appendChild(editButton);
      actionsDiv.appendChild(deleteButton);
      
      div.appendChild(nameDiv);
      div.appendChild(actionsDiv);
      connectionList.appendChild(div);
    });
  } finally {
    hideLoading();
  }
}

function showNewConnectionModal() {
  isEditing = false;
  document.getElementById('connectionModalTitle').textContent = 'New S3 Connection';
  document.getElementById('connectionForm').reset();
  document.getElementById('connectionModal').style.display = 'block';
}

function hideConnectionModal() {
  document.getElementById('connectionModal').style.display = 'none';
  document.getElementById('connectionForm').reset();
}

function editConnection(connection) {
  isEditing = true;
  document.getElementById('connectionModalTitle').textContent = 'Edit S3 Connection';
  const form = document.getElementById('connectionForm');
  form.elements.id.value = connection.id;
  form.elements.name.value = connection.name;
  form.elements.endpoint.value = connection.endpoint;
  form.elements.region.value = connection.region;
  form.elements.accessKey.value = connection.accessKey;
  form.elements.secretKey.value = connection.secretKey;
  form.elements.bucket.value = connection.bucket || '';
  form.elements.prefix.value = connection.prefix || '';
  document.getElementById('connectionModal').style.display = 'block';
}

document.getElementById('connectionForm').onsubmit = async (e) => {
  e.preventDefault();
  showButtonLoading('saveConnectionButton');
  
  try {
    const formData = new FormData(e.target);
    const connection = {
      id: formData.get('id') || Date.now().toString(),
      name: formData.get('name'),
      endpoint: formData.get('endpoint'),
      region: formData.get('region'),
      accessKey: formData.get('accessKey'),
      secretKey: formData.get('secretKey'),
      bucket: formData.get('bucket') || null,
      prefix: formData.get('prefix') || ''
    };

    if (isEditing) {
      const connections = await ipcRenderer.invoke('get-connections');
      const updatedConnections = connections.map(conn => 
        conn.id === connection.id ? connection : conn
      );
      await ipcRenderer.invoke('save-connections', updatedConnections);
    } else {
      await ipcRenderer.invoke('save-connection', connection);
    }

    hideConnectionModal();
    loadConnections();
  } finally {
    hideButtonLoading('saveConnectionButton');
  }
};

// File Management
async function selectConnection(connection) {
  currentConnection = connection;
  currentBucket = connection.bucket;
  currentPrefix = connection.prefix || '';
  updateBreadcrumb();
  await loadFiles();
}

function updateBreadcrumb() {
  const breadcrumb = document.getElementById('pathBreadcrumb');
  const parts = currentPrefix.split('/').filter(p => p);
  let html = `<span class="path-segment" onclick="navigateTo('')">${currentBucket || 'Buckets'}</span>`;
  
  let path = '';
  parts.forEach((part, i) => {
    path += part + '/';
    html += ` / <span class="path-segment" onclick="navigateTo('${path}')">${part}</span>`;
  });
  
  breadcrumb.innerHTML = html;
}

async function navigateTo(prefix) {
  showLoading('Loading...');
  try {
    // If prefix is empty, we're going to root
    if (prefix === '') {
      currentPrefix = '';
    } else {
      // Ensure prefix ends with '/'
      currentPrefix = prefix.endsWith('/') ? prefix : prefix + '/';
    }
    console.log('Navigating to:', currentPrefix);
    updateBreadcrumb();
    await loadFiles();
  } catch (error) {
    console.error('Error navigating:', error);
    alert('Failed to navigate to folder: ' + error.message);
  } finally {
    hideLoading();
  }
}

function getFileIcon(item) {
  if (item.isFolder) return '[DIR]';
  
  const ext = item.Key.split('.').pop().toLowerCase();
  switch (ext) {
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
      return '[IMG]';
    case 'pdf':
      return '[PDF]';
    case 'txt':
    case 'md':
    case 'json':
      return '[TXT]';
    case 'mp3':
    case 'wav':
      return '[AUD]';
    case 'mp4':
    case 'mov':
      return '[VID]';
    default:
      return '[FILE]';
  }
}

async function loadFiles() {
  if (!currentConnection) return;

  showLoading('Loading files...');
  try {
    const result = await ipcRenderer.invoke('list-objects', currentConnection.id, currentBucket, currentPrefix);
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    selectedFiles.clear();

    if (result.type === 'buckets') {
      result.data.forEach(bucket => {
        const div = document.createElement('div');
        div.className = 'file-item folder';
        
        const details = document.createElement('div');
        details.className = 'file-details';
        details.innerHTML = `
          <span class="file-name">[Bucket] ${bucket.Name}</span>
          <span>-</span>
          <span>${new Date(bucket.CreationDate).toLocaleString()}</span>
          <span>Bucket</span>
          <span>-</span>
          <span>-</span>
        `;
        
        const handleBucketClick = async (e) => {
          if (e) e.stopPropagation();
          try {
            showLoading('Loading bucket contents...');
            currentBucket = bucket.Name;
            currentPrefix = '';
            console.log('Selected bucket:', currentBucket);
            updateBreadcrumb();
            await loadFiles();
          } catch (error) {
            console.error('Error accessing bucket:', error);
            alert('Failed to access bucket: ' + error.message);
          } finally {
            hideLoading();
          }
        };

        div.onclick = handleBucketClick;
        details.onclick = handleBucketClick;
        
        div.appendChild(details);
        fileList.appendChild(div);
      });
    } else {
      result.data.forEach(item => {
        const div = document.createElement('div');
        div.className = `file-item${item.isFolder ? ' folder' : ''}`;
        
        // Create checkbox container to prevent click propagation
        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'checkbox-container';
        checkboxContainer.style.width = '20px';
        checkboxContainer.onclick = (e) => e.stopPropagation();
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'file-checkbox';
        checkbox.onclick = (e) => {
          e.stopPropagation();
          toggleFileSelection(item.Key, item.isFolder);
        };
        checkboxContainer.appendChild(checkbox);
        div.appendChild(checkboxContainer);

        const icon = document.createElement('div');
        icon.className = 'file-icon';
        icon.textContent = getFileIcon(item);
        div.appendChild(icon);
        
        const details = document.createElement('div');
        details.className = 'file-details';
        
        const fileName = item.isFolder ? item.Key.split('/').slice(-2)[0] : item.Key.split('/').pop();
        
        details.innerHTML = `
          <span class="file-name">${fileName || ''}</span>
          <span>${item.isFolder ? '-' : formatSize(item.Size)}</span>
          <span>${item.LastModified ? new Date(item.LastModified).toLocaleString() : '-'}</span>
          <span>${item.ContentType || (item.isFolder ? 'Folder' : 'Unknown')}</span>
          <span>${item.StorageClass || '-'}</span>
          <span>${item.Owner?.DisplayName || '-'}</span>
        `;

        // Add preview button for supported file types
        const ext = item.Key.split('.').pop()?.toLowerCase();
        const supportedPreview = !item.isFolder && (
          // Video formats
          ext === 'mp4' || 
          // Image formats
          ext === 'jpg' || 
          ext === 'jpeg' || 
          ext === 'png' || 
          ext === 'gif' || 
          ext === 'webp' ||
          ext === 'svg' ||
          ext === 'bmp' ||
          ext === 'ico' ||
          ext === 'tiff' ||
          ext === 'avif' ||
          // Web formats
          ext === 'html' ||
          // Microsoft Office formats
          ext === 'doc' ||
          ext === 'docx' ||
          ext === 'xls' ||
          ext === 'xlsx' ||
          ext === 'ppt' ||
          ext === 'pptx' ||
          // Document formats
          ext === 'pdf' ||
          // Text formats
          ext === 'txt' ||
          ext === 'md' ||
          ext === 'markdown' ||
          ext === 'json' ||
          ext === 'xml' ||
          ext === 'yaml' ||
          ext === 'yml' ||
          ext === 'ini' ||
          ext === 'csv' ||
          ext === 'log'
        );

        if (supportedPreview) {
          const previewButton = document.createElement('button');
          previewButton.className = 'action-button';
          previewButton.innerHTML = 'Preview';
          previewButton.onclick = (e) => {
            e.stopPropagation();
            previewFile(item);
          };
          details.appendChild(previewButton);
        }

        // Handle folder click for navigation
        if (item.isFolder) {
          const handleFolderClick = (e) => {
            // Only navigate if the click is not on the checkbox
            if (!e.target.matches('input[type="checkbox"]')) {
              navigateTo(item.Key);
            }
          };
          div.onclick = handleFolderClick;
          details.onclick = handleFolderClick;
          icon.onclick = handleFolderClick;
        }
        
        div.appendChild(details);
        fileList.appendChild(div);
      });
    }
  } catch (error) {
    console.error('Error loading files:', error);
    alert('Failed to load files. Please check your connection settings.');
  } finally {
    hideLoading();
  }
}

function toggleFileSelection(key, isFolder) {
  // Ensure folder keys end with '/'
  const selectionKey = isFolder ? (key.endsWith('/') ? key : key + '/') : key;
  if (selectedFiles.has(selectionKey)) {
    selectedFiles.delete(selectionKey);
  } else {
    selectedFiles.add(selectionKey);
  }
}

function createFolder() {
  if (!currentConnection || !currentBucket) {
    alert('Please select a connection and bucket first');
    return;
  }
  document.getElementById('folderModal').style.display = 'block';
}

function hideFolderModal() {
  document.getElementById('folderModal').style.display = 'none';
  document.getElementById('folderForm').reset();
}

document.getElementById('folderForm').onsubmit = async (e) => {
  e.preventDefault();
  showButtonLoading('createFolderButton');
  
  try {
    const formData = new FormData(e.target);
    const folderName = formData.get('folderName');
    const folderPath = currentPrefix + folderName + '/';
    
    await ipcRenderer.invoke('create-folder', currentConnection.id, currentBucket, folderPath);
    hideFolderModal();
    loadFiles();
  } catch (error) {
    console.error('Error creating folder:', error);
    alert('Failed to create folder');
  } finally {
    hideButtonLoading('createFolderButton');
  }
};

async function uploadFile() {
  if (!currentConnection) {
    alert('Please select a connection first');
    return;
  }

  if (!currentBucket) {
    alert('Please select a bucket first');
    return;
  }

  const input = document.createElement('input');
  input.type = 'file';
  input.multiple = true;
  
  input.onchange = async (e) => {
    showButtonLoading('uploadButton');
    try {
      const files = Array.from(e.target.files);
      for (const file of files) {
        try {
          const key = currentPrefix + file.name;
          await ipcRenderer.invoke('upload-object', currentConnection.id, file.path, key, currentBucket);
        } catch (error) {
          console.error('Error uploading file:', error);
          alert(`Failed to upload ${file.name}`);
        }
      }
      loadFiles();
    } finally {
      hideButtonLoading('uploadButton');
    }
  };
  
  input.click();
}

async function downloadSelected() {
  if (!currentBucket) {
    alert('Please select a bucket first');
    return;
  }

  if (selectedFiles.size === 0) {
    alert('Please select files to download');
    return;
  }

  showButtonLoading('downloadButton');
  try {
    for (const key of selectedFiles) {
      try {
        const result = await ipcRenderer.invoke('download-object', currentConnection.id, key, currentBucket);
        if (result.cancelled) continue;
      } catch (error) {
        console.error('Error downloading file:', error);
        alert(`Failed to download ${key}`);
      }
    }
  } finally {
    hideButtonLoading('downloadButton');
  }
}

async function deleteSelected() {
  if (!currentBucket) {
    alert('Please select a bucket first');
    return;
  }

  if (selectedFiles.size === 0) {
    alert('Please select files or folders to delete');
    return;
  }

  // Check if any folders are selected
  const hasFolder = Array.from(selectedFiles).some(key => key.endsWith('/'));
  const selectedCount = selectedFiles.size;

  if (hasFolder) {
    // Create and show folder deletion confirmation modal
    const folderConfirmModal = document.createElement('div');
    folderConfirmModal.className = 'modal';
    folderConfirmModal.style.display = 'flex';
    folderConfirmModal.innerHTML = `
      <div class="modal-content">
        <h2>⚠️ Warning: Folder Deletion</h2>
        <p>You are about to delete ${selectedCount} item(s) including folders. This action cannot be undone.</p>
        <p>To confirm deletion, please type "DELETE" below:</p>
        <input type="text" id="folderDeleteConfirm" placeholder="Type DELETE here" autofocus>
        <div class="modal-buttons">
          <button id="cancelFolderDelete">Cancel</button>
          <button id="confirmFolderDelete" disabled>Delete</button>
        </div>
      </div>
    `;
    document.body.appendChild(folderConfirmModal);

    // Add input validation
    const input = folderConfirmModal.querySelector('#folderDeleteConfirm');
    const confirmButton = folderConfirmModal.querySelector('#confirmFolderDelete');
    const cancelButton = folderConfirmModal.querySelector('#cancelFolderDelete');
    
    // Focus the input field after a short delay to ensure it's ready
    setTimeout(() => {
      input.focus();
    }, 100);

    input.addEventListener('input', () => {
      confirmButton.disabled = input.value !== 'DELETE';
    });

    // Handle confirmation
    try {
      await new Promise((resolve, reject) => {
        confirmButton.onclick = async () => {
          try {
            showButtonLoading('deleteButton');
            for (const key of selectedFiles) {
              try {
                const isFolder = key.endsWith('/');
                const result = await ipcRenderer.invoke('delete-object', currentConnection.id, key, currentBucket, isFolder);
                if (result.message) {
                  console.log(result.message);
                }
              } catch (error) {
                console.error('Error deleting item:', error);
                alert(`Failed to delete ${key}`);
              }
            }
            resolve();
          } catch (error) {
            reject(error);
          } finally {
            folderConfirmModal.remove();
            hideButtonLoading('deleteButton');
          }
        };

        // Handle cancel
        cancelButton.onclick = () => {
          folderConfirmModal.remove();
          resolve();
        };
      });
    } finally {
      await loadFiles();
    }
  } else {
    // Regular file deletion confirmation
    const confirmed = confirm('Are you sure you want to delete the selected files?');
    if (!confirmed) return;

    showButtonLoading('deleteButton');
    try {
      for (const key of selectedFiles) {
        try {
          await ipcRenderer.invoke('delete-object', currentConnection.id, key, currentBucket, false);
        } catch (error) {
          console.error('Error deleting file:', error);
          alert(`Failed to delete ${key}`);
        }
      }
      loadFiles();
    } finally {
      hideButtonLoading('deleteButton');
    }
  }
}

// Handle drag events
document.addEventListener('dragstart', (e) => {
  e.preventDefault();
  e.stopPropagation();
});

document.addEventListener('dragover', (e) => {
  e.preventDefault();
  e.stopPropagation();
});

document.addEventListener('drop', (e) => {
  e.preventDefault();
  e.stopPropagation();
});

async function previewFile(file) {
  showLoading('Loading preview...');
  try {
    const result = await ipcRenderer.invoke('preview-object', currentConnection.id, currentBucket, file.Key);
    const previewModal = document.getElementById('previewModal');
    const previewContent = document.getElementById('previewContent');
    
    if (result.type === 'text') {
      // For text files, add syntax highlighting based on file type
      let content = result.content;
      let language = '';
      
      // Add basic syntax highlighting for markdown
      if (['md', 'markdown'].includes(result.type)) {
        // Simple markdown highlighting
        content = content
          // Headers
          .replace(/^(#{1,6})\s(.+)$/gm, '<span style="color: #0d6efd;">$1</span> <span style="color: #0d6efd; font-weight: bold;">$2</span>')
          // Bold
          .replace(/\*\*(.+?)\*\*/g, '<span style="font-weight: bold;">$1</span>')
          // Italic
          .replace(/\*(.+?)\*/g, '<span style="font-style: italic;">$1</span>')
          // Code blocks
          .replace(/```[\s\S]+?```/g, match => `<span style="color: #d63384;">${match}</span>`)
          // Inline code
          .replace(/`(.+?)`/g, '<span style="color: #d63384; background: #f8f9fa; padding: 0 4px; border-radius: 3px;">$1</span>')
          // Links
          .replace(/\[(.+?)\]\((.+?)\)/g, '<span style="color: #0d6efd;">[$1]($2)</span>')
          // Lists
          .replace(/^(\s*[-*+]|\d+\.)\s/gm, '<span style="color: #198754;">$1 </span>');
      }
      
      previewContent.innerHTML = `
        <div style="height: 100%; overflow: auto; background: white;">
          <pre style="white-space: pre-wrap; word-wrap: break-word; padding: 20px; margin: 0; font-size: 14px; line-height: 1.5; font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;">${content}</pre>
        </div>
      `;
    } else if (result.type === 'pdf') {
      // For PDF files, use Google Docs Viewer
      const encodedUrl = encodeURIComponent(result.content);
      previewContent.innerHTML = `
        <iframe src="https://docs.google.com/viewer?url=${encodedUrl}&embedded=true" 
                style="width: 100%; height: 100%; border: none;">
        </iframe>
      `;
    } else if (result.type === 'mp4') {
      previewContent.innerHTML = `
        <div style="text-align: center;">
          <video controls style="max-width: 100%; max-height: 80vh;">
            <source src="${result.content}" type="video/mp4">
            Your browser does not support the video tag.
          </video>
        </div>
      `;
    } else if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico', 'tiff', 'avif'].includes(result.type)) {
      // For SVG files, set Content-Type to image/svg+xml
      const contentType = result.type === 'svg' ? 'image/svg+xml' : '';
      previewContent.innerHTML = `
        <div style="text-align: center;">
          <img class="preview-image" src="${result.content}" alt="${file.Key}" ${contentType ? `type="${contentType}"` : ''}>
        </div>
      `;
    } else if (result.type === 'html') {
      previewContent.innerHTML = `
        <iframe src="${result.content}" style="width: 100%; height: 80vh; border: none;"></iframe>
      `;
    } else if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(result.type)) {
      // Use Microsoft Office Online Viewer for Office documents
      const encodedUrl = encodeURIComponent(result.content);
      previewContent.innerHTML = `
        <iframe src="https://view.officeapps.live.com/op/embed.aspx?src=${encodedUrl}" 
                style="width: 100%; height: 80vh; border: none;">
        </iframe>
      `;
    } else {
      alert('Preview is only available for text files, images, MP4 videos, HTML files, and Microsoft Office documents');
      return;
    }
    
    previewModal.style.display = 'block';
  } catch (error) {
    console.error('Error previewing file:', error);
    alert('Failed to preview file');
  } finally {
    hideLoading();
  }
}

async function downloadFile(key) {
  showLoading('Downloading file...');
  try {
    await ipcRenderer.invoke('download-object', currentConnection.id, key, currentBucket);
  } catch (error) {
    console.error('Error downloading file:', error);
    alert('Failed to download file');
  } finally {
    hideLoading();
  }
}

function hidePreview() {
  document.getElementById('previewModal').style.display = 'none';
  document.getElementById('previewContent').innerHTML = '';
}

function filterFiles(searchTerm) {
  const fileItems = document.querySelectorAll('.file-item');
  fileItems.forEach(item => {
    const fileName = item.querySelector('.file-name').textContent.toLowerCase();
    if (fileName.includes(searchTerm.toLowerCase())) {
      item.style.display = '';
    } else {
      item.style.display = 'none';
    }
  });
}

function formatSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Initialize
loadConnections();
