#!/usr/bin/env python3

import boto3
import json
from botocore.exceptions import ClientError

def configure_bucket_for_bedrock():
    """为新桶配置 Bedrock 访问权限"""
    
    bucket_name = "nova-reel-20250701132554"
    s3_client = boto3.client('s3')
    
    print(f"🔧 配置桶 {bucket_name} 的 Bedrock 访问权限...")
    
    # 桶策略 - 允许 Bedrock 服务和当前用户访问
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowBedrockServiceAccess",
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
            },
            {
                "Sid": "AllowCurrentUserAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::767828766472:user/dev"
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
    
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("✅ 桶策略配置成功")
        
        # 测试桶访问
        print("🧪 测试桶访问...")
        s3_client.put_object(
            Bucket=bucket_name,
            Key="test.txt",
            Body=b"Test file for Nova Reel"
        )
        print("✅ 桶写入测试成功")
        
        # 清理测试文件
        s3_client.delete_object(Bucket=bucket_name, Key="test.txt")
        print("✅ 桶清理成功")
        
        return True
        
    except ClientError as e:
        print(f"❌ 桶策略配置失败: {e}")
        return False

def test_nova_reel_with_new_bucket():
    """使用新桶测试 Nova Reel"""
    print("\n🎬 使用新桶测试 Nova Reel...")
    
    try:
        import base64
        import io
        import random
        from PIL import Image
        
        bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
        bucket_name = "nova-reel-20250701132554"
        
        # 创建测试图片
        img = Image.new('RGB', (1280, 720), color='purple')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        image_data = buffer.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 配置请求
        seed = random.randint(0, 2147483646)
        prompt = "Transform this purple image into a magical video with sparkles and smooth transitions"
        
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
        print(f"   - 桶: {bucket_name}")
        print(f"   - 提示词: {prompt}")
        
        response = bedrock_runtime.start_async_invoke(
            modelId="amazon.nova-reel-v1:0",
            modelInput=model_input,
            outputDataConfig=output_config
        )
        
        invocation_arn = response["invocationArn"]
        print(f"✅ 测试作业启动成功!")
        print(f"   - ARN: {invocation_arn}")
        
        # 检查状态
        job_status = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)
        status = job_status["status"]
        print(f"📊 当前状态: {status}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ 测试失败: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 配置新的 Nova Reel 桶")
    print("=" * 50)
    
    # 配置桶策略
    bucket_success = configure_bucket_for_bedrock()
    
    if bucket_success:
        # 测试 Nova Reel
        test_success = test_nova_reel_with_new_bucket()
        
        if test_success:
            print("\n🎉 配置和测试都成功!")
            print("💡 现在你可以使用 Web 应用生成视频了")
            print("🌐 访问: http://localhost:8000")
        else:
            print("\n⚠️ 桶配置成功但 Nova Reel 测试失败")
    else:
        print("\n❌ 桶配置失败")
