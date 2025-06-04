#!/usr/bin/env python3
"""
测试MongoDB连接
使用IAM角色获取密钥并实现读写分离
"""
import boto3
import json
import sys
import time
import urllib.parse
from pymongo import MongoClient

def get_secret(secret_name, region_name="us-east-1"):
    """从AWS Secrets Manager获取密钥"""
    # 创建Secrets Manager客户端
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    
    try:
        # 获取密钥值
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"获取密钥失败: {e}")
        raise e

def get_cluster_info(cluster_id=None, region_name="us-east-1"):
    """获取DocumentDB集群信息"""
    session = boto3.session.Session()
    docdb_client = session.client(service_name='docdb', region_name=region_name)
    
    try:
        # 如果没有提供集群ID，则获取第一个可用的集群
        if not cluster_id:
            clusters = docdb_client.describe_db_clusters()
            if not clusters['DBClusters']:
                raise Exception("无法找到DocumentDB集群")
            cluster_id = clusters['DBClusters'][0]['DBClusterIdentifier']
            
        # 获取集群详细信息
        cluster_info = docdb_client.describe_db_clusters(DBClusterIdentifier=cluster_id)['DBClusters'][0]
        return cluster_info
    except Exception as e:
        print(f"获取集群信息失败: {e}")
        raise e

def get_connection_string(username, password, endpoint, port=27017, ssl=True):
    """构建MongoDB连接字符串"""
    # 对用户名和密码进行URL编码
    username_encoded = urllib.parse.quote_plus(username)
    password_encoded = urllib.parse.quote_plus(password)
    
    # 构建连接字符串
    conn_str = f"mongodb://{username_encoded}:{password_encoded}@{endpoint}:{port}/?ssl={str(ssl).lower()}&retryWrites=false"
    return conn_str

def test_connection():
    """测试MongoDB连接，使用读写分离"""
    # 获取DocumentDB密钥名称
    secret_name = "your-secret-name"
    region_name = "us-east-1"
    
    try:
        # 获取密钥
        secret_dict = get_secret(secret_name, region_name)
        
        # 获取连接信息
        username = secret_dict.get('username')
        password = secret_dict.get('password')
        
        print(f"使用用户名: {username}")
        
        # 获取集群ID
        cluster_id = secret_dict.get('dbClusterIdentifier')
        if not cluster_id:
            # 如果密钥中没有集群ID，则获取第一个可用的集群
            cluster_info = get_cluster_info(region_name=region_name)
            cluster_id = cluster_info['DBClusterIdentifier']
        else:
            # 获取指定集群的信息
            cluster_info = get_cluster_info(cluster_id, region_name)
        
        print(f"使用集群ID: {cluster_id}")
        
        # 获取集群端点信息
        cluster_endpoint = cluster_info['Endpoint']  # 主端点，用于写操作
        reader_endpoint = cluster_info.get('ReaderEndpoint')  # 读取端点，用于读操作
        
        print(f"主端点(写): {cluster_endpoint}")
        print(f"读取端点(读): {reader_endpoint}")
        
        # 创建写入连接
        write_conn_str = get_connection_string(username, password, cluster_endpoint)
        write_client = MongoClient(
            write_conn_str,
            ssl=True,
            tlsCAFile='rds-combined-ca-bundle.pem',
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # 创建读取连接
        read_conn_str = get_connection_string(username, password, reader_endpoint)
        read_client = MongoClient(
            read_conn_str,
            ssl=True,
            tlsCAFile='rds-combined-ca-bundle.pem',
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # 测试写入连接
        print("测试写入连接...")
        write_server_info = write_client.server_info()
        print(f"写入连接成功! 服务器信息: {write_server_info}")
        
        # 测试读取连接
        print("测试读取连接...")
        read_server_info = read_client.server_info()
        print(f"读取连接成功! 服务器信息: {read_server_info}")
        
        # 使用写入连接插入数据
        write_db = write_client.test_db
        write_collection = write_db.test_collection
        
        # 插入一个文档
        doc_id = write_collection.insert_one({"test": "document", "timestamp": time.time()}).inserted_id
        print(f"成功插入文档，ID: {doc_id}")
        
        # 使用读取连接查询数据
        read_db = read_client.test_db
        read_collection = read_db.test_collection
        
        # 查询文档
        doc = read_collection.find_one({"_id": doc_id})
        print(f"通过读取连接查询文档: {doc}")
        
        # 关闭连接
        write_client.close()
        read_client.close()
        print("连接测试完成")
        return True
        
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False

if __name__ == "__main__":
    test_connection()
