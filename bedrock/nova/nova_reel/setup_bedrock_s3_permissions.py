#!/usr/bin/env python3
"""
配置 Bedrock 和 S3 权限的脚本
解决 "Invalid Output Config/Credentials" 错误
"""

import boto3
import json
from botocore.exceptions import ClientError

def create_bedrock_service_role():
    """创建 Bedrock 服务角色"""
    print("🔐 创建 Bedrock 服务角色...")
    
    iam_client = boto3.client('iam')
    
    # 信任策略 - 允许 Bedrock 服务承担此角色
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # S3 访问策略
    s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::bedrock-video-generation-*",
                    "arn:aws:s3:::bedrock-video-generation-*/*",
                    "arn:aws:s3:::nova-reel-*",
                    "arn:aws:s3:::nova-reel-*/*"
                ]
            }
        ]
    }
    
    role_name = "BedrockNovaReelExecutionRole"
    policy_name = "BedrockS3AccessPolicy"
    
    try:
        # 创建角色
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Service role for Bedrock Nova Reel to access S3"
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ 角色创建成功: {role_arn}")
        
        # 创建并附加策略
        policy_response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(s3_policy),
            Description="Policy for Bedrock to access S3 buckets"
        )
        
        policy_arn = policy_response['Policy']['Arn']
        print(f"✅ 策略创建成功: {policy_arn}")
        
        # 将策略附加到角色
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        
        print(f"✅ 策略附加成功")
        return role_arn
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("⚠️ 角色或策略已存在，获取现有角色...")
            try:
                role_response = iam_client.get_role(RoleName=role_name)
                role_arn = role_response['Role']['Arn']
                print(f"✅ 使用现有角色: {role_arn}")
                return role_arn
            except:
                print("❌ 无法获取现有角色")
                return None
        else:
            print(f"❌ 创建角色失败: {e}")
            return None

def setup_s3_bucket_policy():
    """设置 S3 桶策略"""
    print("\n📦 配置 S3 桶策略...")
    
    s3_client = boto3.client('s3')
    bucket_name = "bedrock-video-generation-us-east-1-pi8hu9"
    
    # 桶策略 - 允许 Bedrock 服务访问
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowBedrockAccess",
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            },
            {
                "Sid": "AllowBedrockListBucket",
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "s3:ListBucket",
                "Resource": f"arn:aws:s3:::{bucket_name}"
            }
        ]
    }
    
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print(f"✅ S3 桶策略配置成功: {bucket_name}")
        return True
        
    except ClientError as e:
        print(f"❌ S3 桶策略配置失败: {e}")
        return False

def create_dedicated_bucket():
    """创建专用的 Nova Reel 桶"""
    print("\n🪣 创建专用 Nova Reel 桶...")
    
    s3_client = boto3.client('s3')
    
    import time
    bucket_name = f"nova-reel-videos-{int(time.time())}"
    
    try:
        # 创建桶
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"✅ 桶创建成功: {bucket_name}")
        
        # 配置桶策略
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowBedrockAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
        
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print(f"✅ 桶策略配置成功")
        return bucket_name
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyExists':
            print("⚠️ 桶名已存在，尝试其他名称...")
            bucket_name = f"nova-reel-{int(time.time())}-backup"
            try:
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✅ 备用桶创建成功: {bucket_name}")
                return bucket_name
            except:
                print("❌ 备用桶创建也失败")
                return None
        else:
            print(f"❌ 桶创建失败: {e}")
            return None

def test_bedrock_with_new_config(bucket_name):
    """使用新配置测试 Bedrock"""
    print(f"\n🧪 测试新配置...")
    
    try:
        import base64
        import io
        import random
        from PIL import Image
        
        bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        # 创建测试图片
        img = Image.new('RGB', (1280, 720), color='green')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        image_data = buffer.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 配置请求
        seed = random.randint(0, 2147483646)
        prompt = "A peaceful green landscape with gentle movements"
        
        model_input = {
            "taskType": "TEXT_VIDEO",
            "textToVideoParams": {
                "text": prompt,
                "images": [
                    {
                        "format": "jpeg",
                        "source": {
                            "bytes": image_base64
                        }
                    }
                ]
            },
            "videoGenerationConfig": {
                "fps": 24,
                "durationSeconds": 6,
                "dimension": "1280x720",
                "seed": seed,
            }
        }
        
        output_config = {"s3OutputDataConfig": {"s3Uri": f"s3://{bucket_name}/test-output"}}
        
        print(f"🚀 启动测试作业...")
        response = bedrock_runtime.start_async_invoke(
            modelId="amazon.nova-reel-v1:0",
            modelInput=model_input,
            outputDataConfig=output_config
        )
        
        invocation_arn = response["invocationArn"]
        print(f"✅ 测试作业启动成功!")
        print(f"   - ARN: {invocation_arn}")
        print(f"   - 输出桶: {bucket_name}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ 测试失败: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def main():
    """主配置函数"""
    print("🔧 配置 Bedrock Nova Reel S3 权限")
    print("=" * 60)
    
    # 步骤1: 创建服务角色
    role_arn = create_bedrock_service_role()
    
    # 步骤2: 配置现有桶策略
    bucket_policy_success = setup_s3_bucket_policy()
    
    # 步骤3: 创建专用桶（如果现有桶配置失败）
    new_bucket = None
    if not bucket_policy_success:
        new_bucket = create_dedicated_bucket()
    
    # 步骤4: 测试配置
    test_bucket = new_bucket if new_bucket else "bedrock-video-generation-us-east-1-pi8hu9"
    test_success = test_bedrock_with_new_config(test_bucket)
    
    print("\n" + "=" * 60)
    print("📊 配置结果总结:")
    print(f"   - 服务角色: {'✅ 成功' if role_arn else '❌ 失败'}")
    print(f"   - 桶策略: {'✅ 成功' if bucket_policy_success else '❌ 失败'}")
    print(f"   - 专用桶: {'✅ 创建' if new_bucket else '⏭️ 跳过'}")
    print(f"   - 测试: {'✅ 通过' if test_success else '❌ 失败'}")
    
    if test_success:
        print(f"\n🎉 配置成功!")
        print(f"📦 使用桶: {test_bucket}")
        print(f"🔗 服务角色: {role_arn}")
        print(f"\n💡 现在你可以更新 app.py 中的桶名为: {test_bucket}")
    else:
        print(f"\n⚠️ 配置可能不完整，请检查:")
        print("   - IAM 权限")
        print("   - S3 桶访问权限")
        print("   - 网络连接")

if __name__ == "__main__":
    main()
