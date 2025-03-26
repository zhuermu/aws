/**
 * AWS S3 Client Implementation
 */

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
const StorageClientInterface = require('./StorageClientInterface');

class AWSS3Client extends StorageClientInterface {
  constructor() {
    super();
    this.client = null;
  }

  /**
   * Initialize the S3 client with connection details
   * @param {Object} config - S3 connection configuration
   * @returns {AWSS3Client} This instance
   */
  initialize(config) {
    this.client = new S3Client({
      endpoint: config.endpoint,
      region: config.region,
      credentials: {
        accessKeyId: config.accessKey,
        secretAccessKey: config.secretKey
      }
    });
    
    return this;
  }

  /**
   * List all buckets in the account
   * @returns {Promise<Array>} List of buckets
   */
  async listBuckets() {
    const response = await this.client.send(new ListBucketsCommand({}));
    return response.Buckets || [];
  }

  /**
   * List objects in a bucket with optional prefix
   * @param {string} bucket - Bucket name
   * @param {string} prefix - Optional prefix (folder path)
   * @returns {Promise<Object>} Object containing folders and files
   */
  async listObjects(bucket, prefix = '') {
    const command = new ListObjectsV2Command({
      Bucket: bucket,
      Prefix: prefix,
      Delimiter: '/'
    });

    const response = await this.client.send(command);
    
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
  }

  /**
   * Upload an object to S3
   * @param {string} bucket - Bucket name
   * @param {string} key - Object key
   * @param {Buffer|Readable} body - Object content
   * @returns {Promise<Object>} Result of the upload operation
   */
  async uploadObject(bucket, key, body) {
    const command = new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: body
    });

    const response = await this.client.send(command);
    return { success: true, response };
  }

  /**
   * Download an object from S3
   * @param {string} bucket - Bucket name
   * @param {string} key - Object key
   * @returns {Promise<Object>} Object containing the content and metadata
   */
  async getObject(bucket, key) {
    const command = new GetObjectCommand({
      Bucket: bucket,
      Key: key
    });

    return await this.client.send(command);
  }

  /**
   * Generate a signed URL for temporary access to an object
   * @param {string} bucket - Bucket name
   * @param {string} key - Object key
   * @param {number} expiresIn - URL expiration time in seconds
   * @returns {Promise<string>} Signed URL
   */
  async getSignedUrl(bucket, key, expiresIn = 3600) {
    const command = new GetObjectCommand({
      Bucket: bucket,
      Key: key
    });

    return await getSignedUrl(this.client, command, { expiresIn });
  }

  /**
   * Delete an object from S3
   * @param {string} bucket - Bucket name
   * @param {string} key - Object key
   * @returns {Promise<Object>} Result of the delete operation
   */
  async deleteObject(bucket, key) {
    const command = new DeleteObjectCommand({
      Bucket: bucket,
      Key: key
    });

    const response = await this.client.send(command);
    return { success: true, response };
  }

  /**
   * Delete multiple objects from S3
   * @param {string} bucket - Bucket name
   * @param {Array<string>} keys - Array of object keys
   * @returns {Promise<Object>} Result of the batch delete operation
   */
  async deleteObjects(bucket, keys) {
    const command = new DeleteObjectsCommand({
      Bucket: bucket,
      Delete: {
        Objects: keys.map(key => ({ Key: key })),
        Quiet: false
      }
    });

    const response = await this.client.send(command);
    return {
      success: true,
      deleted: response.Deleted || [],
      errors: response.Errors || []
    };
  }

  /**
   * Create a folder in S3 (empty object with trailing slash)
   * @param {string} bucket - Bucket name
   * @param {string} folderPath - Folder path to create
   * @returns {Promise<Object>} Result of the folder creation
   */
  async createFolder(bucket, folderPath) {
    // Ensure the folder path ends with a slash
    const normalizedPath = folderPath.endsWith('/') ? folderPath : `${folderPath}/`;
    
    const command = new PutObjectCommand({
      Bucket: bucket,
      Key: normalizedPath,
      Body: ''
    });

    const response = await this.client.send(command);
    return { success: true, response };
  }
}

module.exports = AWSS3Client; 