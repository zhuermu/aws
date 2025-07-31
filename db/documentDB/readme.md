# DocumentDB 连接测试

本项目演示如何使用Python连接到Amazon DocumentDB，实现读写分离，并使用IAM角色进行安全认证。

## 功能特点

- 使用IAM角色获取DocumentDB密钥，而不是硬编码密钥
- 实现读写分离，提高性能和可用性
- 使用SSL/TLS加密连接
- 完整的错误处理和日志记录

## 前提条件

- AWS账户和DocumentDB集群
- Python 3.6+
- pymongo库
- boto3库
- AWS CLI配置（用于IAM角色认证）

## 安装依赖

```bash
pip install pymongo boto3
```

## 下载SSL证书

使用提供的脚本下载DocumentDB的SSL证书：

```bash
./download_cert.sh
```

或者手动下载：

```bash
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -O rds-combined-ca-bundle.pem
```

## IAM角色配置

本项目使用名为`DocumentDBAccessRole`的IAM角色来获取DocumentDB密钥。该角色需要以下权限：

- `SecretsManagerReadWrite`：用于访问存储在AWS Secrets Manager中的DocumentDB凭证
- `AmazonDocDBFullAccess`：用于访问DocumentDB资源

如果您需要创建此角色，可以使用以下AWS CLI命令：

```bash
# 创建IAM角色
aws iam create-role --role-name DocumentDBAccessRole \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --description "Role for accessing DocumentDB secrets and resources"

# 附加必要的策略
aws iam attach-role-policy --role-name DocumentDBAccessRole --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
aws iam attach-role-policy --role-name DocumentDBAccessRole --policy-arn arn:aws:iam::aws:policy/AmazonDocDBFullAccess
```

## 代码逻辑说明

`test_mongo_connection.py`文件实现了以下功能：

1. **获取密钥**：使用IAM角色从AWS Secrets Manager获取DocumentDB凭证
   ```python
   def get_secret(secret_name, region_name="us-east-1"):
       session = boto3.session.Session()
       client = session.client(service_name='secretsmanager', region_name=region_name)
       get_secret_value_response = client.get_secret_value(SecretId=secret_name)
       secret = get_secret_value_response['SecretString']
       return json.loads(secret)
   ```

2. **获取集群信息**：获取DocumentDB集群的端点信息
   ```python
   def get_cluster_info(cluster_id=None, region_name="us-east-1"):
       session = boto3.session.Session()
       docdb_client = session.client(service_name='docdb', region_name=region_name)
       # 获取集群详细信息
       cluster_info = docdb_client.describe_db_clusters(DBClusterIdentifier=cluster_id)['DBClusters'][0]
       return cluster_info
   ```

3. **读写分离**：使用不同的端点进行读写操作
   ```python
   # 创建写入连接（使用主端点）
   write_conn_str = get_connection_string(username, password, cluster_endpoint)
   write_client = MongoClient(write_conn_str, ssl=True, tlsCAFile='rds-combined-ca-bundle.pem')
   
   # 创建读取连接（使用读取端点）
   read_conn_str = get_connection_string(username, password, reader_endpoint)
   read_client = MongoClient(read_conn_str, ssl=True, tlsCAFile='rds-combined-ca-bundle.pem')
   ```

4. **测试连接**：分别测试读写连接
   ```python
   # 使用写入连接插入数据
   doc_id = write_collection.insert_one({"test": "document", "timestamp": time.time()}).inserted_id
   
   # 使用读取连接查询数据
   doc = read_collection.find_one({"_id": doc_id})
   ```

## 使用方法

直接运行Python脚本：

```bash
python test_mongo_connection.py
```

## 注意事项

- 确保您的EC2实例或运行环境已附加`DocumentDBAccessRole`角色
- 如果在本地运行，请确保已配置AWS凭证
- 确保您的安全组和网络ACL允许与DocumentDB集群的连接
- 读写分离功能需要DocumentDB集群配置为具有多个实例