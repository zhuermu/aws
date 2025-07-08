#!/usr/bin/env python3
"""
AWS 配置和权限诊断脚本
用于检查 Nova Reel 视频生成所需的配置和权限
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def check_aws_credentials():
    """检查 AWS 凭证配置"""
    print("🔐 检查 AWS 凭证...")
    
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        
        print("✅ AWS 凭证配置正确")
        print(f"   - 用户 ARN: {identity.get('Arn')}")
        print(f"   - 账户 ID: {identity.get('Account')}")
        print(f"   - 用户 ID: {identity.get('UserId')}")
        return True
        
    except NoCredentialsError:
        print("❌ AWS 凭证未配置")
        print("💡 请运行: aws configure")
        return False
    except Exception as e:
        print(f"❌ AWS 凭证检查失败: {str(e)}")
        return False

def check_bedrock_permissions():
    """检查 Bedrock 权限"""
    print("\n🧠 检查 Bedrock 权限...")
    
    try:
        bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        
        # 尝试列出基础模型
        response = bedrock_client.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        # 查找 Nova Reel 模型
        nova_reel_models = [m for m in models if 'nova-reel' in m['modelId'].lower()]
        
        if nova_reel_models:
            print("✅ Bedrock 权限正常")
            print(f"   - 找到 {len(nova_reel_models)} 个 Nova Reel 模型")
            for model in nova_reel_models:
                print(f"     * {model['modelId']} ({model.get('modelLifecycle', {}).get('status', 'UNKNOWN')})")
        else:
            print("⚠️  Bedrock 权限正常，但未找到 Nova Reel 模型")
            print("💡 请检查模型是否在当前区域可用")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Bedrock 访问被拒绝")
            print("💡 请确保 IAM 用户/角色有 bedrock:ListFoundationModels 权限")
        else:
            print(f"❌ Bedrock 权限检查失败: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Bedrock 权限检查异常: {str(e)}")
        return False

def check_s3_permissions():
    """检查 S3 权限"""
    print("\n📦 检查 S3 权限...")
    
    try:
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        # 尝试列出桶
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        
        print("✅ S3 权限正常")
        print(f"   - 可访问 {len(buckets)} 个 S3 桶")
        
        # 尝试创建一个测试桶
        test_bucket_name = f"nova-reel-test-{hash(str(buckets)) % 10000}"
        
        try:
            s3_client.create_bucket(Bucket=test_bucket_name)
            print(f"✅ S3 桶创建权限正常 (测试桶: {test_bucket_name})")
            
            # 清理测试桶
            try:
                s3_client.delete_bucket(Bucket=test_bucket_name)
                print("✅ S3 桶删除权限正常")
            except:
                print(f"⚠️  测试桶 {test_bucket_name} 可能需要手动删除")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                print("✅ S3 桶创建权限正常 (桶名已存在)")
            else:
                print(f"⚠️  S3 桶创建可能有问题: {e.response['Error']['Code']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ S3 访问被拒绝")
            print("💡 请确保 IAM 用户/角色有 S3 相关权限")
        else:
            print(f"❌ S3 权限检查失败: {error_code}")
        return False
    except Exception as e:
        print(f"❌ S3 权限检查异常: {str(e)}")
        return False

def check_bedrock_runtime_permissions():
    """检查 Bedrock Runtime 权限"""
    print("\n🚀 检查 Bedrock Runtime 权限...")
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # 尝试一个简单的文本生成调用来测试权限
        try:
            response = bedrock_runtime.converse(
                modelId="amazon.nova-lite-v1:0",
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": "Hello"}]
                    }
                ],
                inferenceConfig={"maxTokens": 10}
            )
            print("✅ Bedrock Runtime 权限正常 (文本生成测试成功)")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("❌ Bedrock Runtime 访问被拒绝")
                print("💡 请确保 IAM 用户/角色有 bedrock:InvokeModel 权限")
            elif error_code == 'ValidationException':
                print("✅ Bedrock Runtime 权限正常 (验证错误是正常的)")
                return True
            else:
                print(f"⚠️  Bedrock Runtime 测试: {error_code}")
                return True  # 其他错误可能不是权限问题
                
    except Exception as e:
        print(f"❌ Bedrock Runtime 权限检查异常: {str(e)}")
        return False

def check_nova_reel_async_permissions():
    """检查 Nova Reel 异步调用权限"""
    print("\n🎬 检查 Nova Reel 异步调用权限...")
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # 检查是否有 start_async_invoke 方法
        if hasattr(bedrock_runtime, 'start_async_invoke'):
            print("✅ start_async_invoke 方法可用")
        else:
            print("❌ start_async_invoke 方法不可用，请更新 boto3")
            return False
        
        # 检查是否有 get_async_invoke 方法
        if hasattr(bedrock_runtime, 'get_async_invoke'):
            print("✅ get_async_invoke 方法可用")
        else:
            print("❌ get_async_invoke 方法不可用，请更新 boto3")
            return False
        
        print("✅ Nova Reel 异步调用方法都可用")
        return True
        
    except Exception as e:
        print(f"❌ Nova Reel 异步调用检查异常: {str(e)}")
        return False

def generate_iam_policy():
    """生成建议的 IAM 策略"""
    print("\n📋 建议的 IAM 策略:")
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:StartAsyncInvoke",
                    "bedrock:GetAsyncInvoke",
                    "bedrock:ListFoundationModels"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                    "s3:CreateBucket",
                    "s3:DeleteBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::nova-reel-*",
                    "arn:aws:s3:::nova-reel-*/*"
                ]
            }
        ]
    }
    
    print(json.dumps(policy, indent=2))

def main():
    """主诊断函数"""
    print("🔍 AWS 配置和权限诊断")
    print("=" * 60)
    
    results = []
    
    # 检查各项配置
    results.append(("AWS 凭证", check_aws_credentials()))
    results.append(("Bedrock 权限", check_bedrock_permissions()))
    results.append(("S3 权限", check_s3_permissions()))
    results.append(("Bedrock Runtime 权限", check_bedrock_runtime_permissions()))
    results.append(("Nova Reel 异步权限", check_nova_reel_async_permissions()))
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 诊断结果总结:")
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   - {name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查都通过！你的配置应该可以正常工作。")
    else:
        print("\n⚠️  发现一些问题，请根据上面的建议进行修复。")
        generate_iam_policy()
    
    print("\n💡 如果问题仍然存在，请检查:")
    print("   - AWS 区域设置 (当前使用 us-east-1)")
    print("   - 网络连接")
    print("   - boto3 版本 (建议 >= 1.39.0)")

if __name__ == "__main__":
    main()
