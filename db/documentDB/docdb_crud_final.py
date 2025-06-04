#!/usr/bin/env python3
"""
DocumentDB CRUD 操作类 - 最终版本
支持读写分离和安全凭证管理
"""
import boto3
import json
import sys
import time
import urllib.parse
from pymongo import MongoClient, ReadPreference
from bson.objectid import ObjectId

class DocumentDBCRUD:
    """DocumentDB CRUD操作类，支持读写分离"""
    
    def __init__(self, secret_name, region_name="us-east-1"):
        """
        初始化DocumentDB CRUD操作类
        
        Args:
            secret_name: AWS Secrets Manager中存储的密钥名称
            region_name: AWS区域
        """
        self.secret_name = secret_name
        self.region_name = region_name
        self.credentials = self._get_secret()
        self.writer_client = None
        self.reader_client = None
        self.db_writer = None
        self.db_reader = None
        self.collection_writer = None
        self.collection_reader = None
        self.read_preference = ReadPreference.SECONDARY_PREFERRED
        
    def _get_secret(self):
        """从AWS Secrets Manager获取DocumentDB凭证"""
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=self.region_name)
        
        try:
            # 获取密钥
            get_secret_value_response = client.get_secret_value(SecretId=self.secret_name)
            secret = get_secret_value_response['SecretString']
            secret_dict = json.loads(secret)
            
            # 获取DocumentDB集群信息
            docdb_client = session.client(service_name='docdb', region_name=self.region_name)
            
            # 适配不同的密钥格式
            credentials = {}
            
            # 获取集群ID
            if 'dbClusterIdentifier' in secret_dict:
                cluster_id = secret_dict.get('dbClusterIdentifier')
            else:
                # 尝试从主机名推断集群ID
                host = secret_dict.get('host', '')
                if '.' in host and 'cluster-' in host:
                    cluster_id = host.split('.')[0]
                else:
                    # 获取所有DocumentDB集群
                    clusters = docdb_client.describe_db_clusters()
                    if clusters['DBClusters']:
                        cluster_id = clusters['DBClusters'][0]['DBClusterIdentifier']
                    else:
                        raise Exception("无法确定DocumentDB集群ID")
            
            # 获取集群详细信息
            cluster_info = docdb_client.describe_db_clusters(DBClusterIdentifier=cluster_id)['DBClusters'][0]
            
            # 获取主用户名
            credentials['username'] = secret_dict.get('username')
            
            # 获取密码
            if 'password' in secret_dict:
                credentials['password'] = secret_dict.get('password')
            else:
                raise Exception("密钥中未包含密码")
            
            # 获取端点信息
            credentials['clusterEndpoint'] = cluster_info['Endpoint']
            credentials['readerEndpoint'] = cluster_info['ReaderEndpoint']
            
            return credentials
            
        except Exception as e:
            print(f"获取凭证失败: {e}")
            sys.exit(1)
    
    def connect(self, database_name, collection_name):
        """
        连接到DocumentDB集群
        
        Args:
            database_name: 数据库名称
            collection_name: 集合名称
        """
        try:
            # 从凭证中获取连接信息
            username = self.credentials.get('username')
            password = self.credentials.get('password')
            cluster_endpoint = self.credentials.get('clusterEndpoint')
            reader_endpoint = self.credentials.get('readerEndpoint')
            
            print(f"连接到DocumentDB集群: {cluster_endpoint}")
            print(f"读取端点: {reader_endpoint}")
            print(f"用户名: {username}")
            
            # 对用户名和密码进行URL编码
            username_encoded = urllib.parse.quote_plus(username)
            password_encoded = urllib.parse.quote_plus(password)
            
            # 构建连接字符串 - 简化版本
            conn_str_writer = f"mongodb://{username_encoded}:{password_encoded}@{cluster_endpoint}:27017/?ssl=true&retryWrites=false"
            conn_str_reader = f"mongodb://{username_encoded}:{password_encoded}@{reader_endpoint}:27017/?ssl=true&retryWrites=false"
            
            # 连接到写入端点
            self.writer_client = MongoClient(
                conn_str_writer,
                ssl=True,
                tlsCAFile='rds-combined-ca-bundle.pem',
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # 连接到读取端点
            self.reader_client = MongoClient(
                conn_str_reader,
                ssl=True,
                tlsCAFile='rds-combined-ca-bundle.pem',
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                read_preference=self.read_preference
            )
            
            # 测试连接
            self.writer_client.admin.command('ping')
            self.reader_client.admin.command('ping')
            
            # 设置数据库和集合
            self.db_writer = self.writer_client[database_name]
            self.db_reader = self.reader_client[database_name]
            self.collection_writer = self.db_writer[collection_name]
            self.collection_reader = self.db_reader[collection_name]
            
            print(f"成功连接到DocumentDB集群")
            return True
        except Exception as e:
            print(f"连接DocumentDB失败: {e}")
            return False
    
    def set_read_preference(self, preference):
        """
        设置读取偏好
        
        Args:
            preference: pymongo.ReadPreference 枚举值
                - PRIMARY: 总是从主节点读取
                - PRIMARY_PREFERRED: 优先从主节点读取，如果不可用则从从节点读取
                - SECONDARY: 总是从从节点读取
                - SECONDARY_PREFERRED: 优先从从节点读取，如果不可用则从主节点读取
                - NEAREST: 从网络延迟最低的节点读取
        """
        self.read_preference = preference
        if self.reader_client:
            # 如果已经连接，则需要重新连接以应用新的读取偏好
            current_db = self.db_reader.name if self.db_reader else None
            current_collection = self.collection_reader.name if self.collection_reader else None
            
            if current_db and current_collection:
                self.connect(current_db, current_collection)
    
    def create_document(self, document):
        """
        创建新文档
        
        Args:
            document: 要创建的文档(字典)
        
        Returns:
            新创建文档的ID
        """
        try:
            # 使用写入端点进行创建操作
            result = self.collection_writer.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"创建文档失败: {e}")
            return None
    
    def read_document(self, document_id=None, query=None):
        """
        读取文档
        
        Args:
            document_id: 文档ID (可选)
            query: 查询条件 (可选)
            
        Returns:
            查询到的文档或文档列表
        """
        try:
            # 使用读取端点进行读取操作
            if document_id:
                result = self.collection_reader.find_one({"_id": ObjectId(document_id)})
                return result
            elif query:
                results = list(self.collection_reader.find(query))
                return results
            else:
                results = list(self.collection_reader.find())
                return results
        except Exception as e:
            print(f"读取文档失败: {e}")
            return None
    
    def update_document(self, document_id, update_data):
        """
        更新文档
        
        Args:
            document_id: 要更新的文档ID
            update_data: 更新的数据(字典)
            
        Returns:
            更新的文档数量
        """
        try:
            # 使用写入端点进行更新操作
            result = self.collection_writer.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            return result.modified_count
        except Exception as e:
            print(f"更新文档失败: {e}")
            return 0
    
    def delete_document(self, document_id):
        """
        删除文档
        
        Args:
            document_id: 要删除的文档ID
            
        Returns:
            删除的文档数量
        """
        try:
            # 使用写入端点进行删除操作
            result = self.collection_writer.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count
        except Exception as e:
            print(f"删除文档失败: {e}")
            return 0
    
    def bulk_create_documents(self, documents):
        """
        批量创建文档
        
        Args:
            documents: 要创建的文档列表
            
        Returns:
            创建的文档ID列表
        """
        try:
            # 使用写入端点进行批量创建操作
            result = self.collection_writer.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            print(f"批量创建文档失败: {e}")
            return []
    
    def bulk_update_documents(self, query, update_data):
        """
        批量更新文档
        
        Args:
            query: 查询条件
            update_data: 更新的数据(字典)
            
        Returns:
            更新的文档数量
        """
        try:
            # 使用写入端点进行批量更新操作
            result = self.collection_writer.update_many(
                query,
                {"$set": update_data}
            )
            return result.modified_count
        except Exception as e:
            print(f"批量更新文档失败: {e}")
            return 0
    
    def bulk_delete_documents(self, query):
        """
        批量删除文档
        
        Args:
            query: 查询条件
            
        Returns:
            删除的文档数量
        """
        try:
            # 使用写入端点进行批量删除操作
            result = self.collection_writer.delete_many(query)
            return result.deleted_count
        except Exception as e:
            print(f"批量删除文档失败: {e}")
            return 0
    
    def close(self):
        """关闭数据库连接"""
        if self.writer_client:
            self.writer_client.close()
        if self.reader_client:
            self.reader_client.close()
        print("数据库连接已关闭")


# 使用示例
if __name__ == "__main__":
    # 替换为您的Secret名称和区域
    secret_name = "rds!cluster-01626a18-8cc9-4bb4-9a92-5fb1b2eef724"
    region_name = "us-east-1"
    
    # 初始化CRUD操作类
    docdb = DocumentDBCRUD(secret_name, region_name)
    
    # 连接到数据库和集合
    if not docdb.connect("sample_db", "users"):
        sys.exit(1)
    
    try:
        # 创建文档
        user = {
            "name": "张三",
            "email": "zhangsan@example.com",
            "age": 30,
            "created_at": time.time()
        }
        user_id = docdb.create_document(user)
        if user_id:
            print(f"创建的用户ID: {user_id}")
            
            # 读取文档
            user = docdb.read_document(user_id)
            print(f"读取的用户: {user}")
            
            # 更新文档
            update_result = docdb.update_document(user_id, {"age": 31})
            print(f"更新的文档数: {update_result}")
            
            # 再次读取文档
            user = docdb.read_document(user_id)
            print(f"更新后的用户: {user}")
            
            # 查询所有用户
            all_users = docdb.read_document()
            print(f"所有用户数量: {len(all_users)}")
            
            # 删除文档
            delete_result = docdb.delete_document(user_id)
            print(f"删除的文档数: {delete_result}")
    except Exception as e:
        print(f"操作过程中出错: {e}")
    finally:
        # 关闭连接
        docdb.close()
