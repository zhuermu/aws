#!/usr/bin/env python3

import boto3
import json
from botocore.exceptions import ClientError

def check_bedrock_service_linked_role():
    """检查 Bedrock 服务链接角色"""
    print("🔗 检查 Bedrock 服务链接角色...")
    
    iam_client = boto3.client('iam')
    
    try:
        # 列出服务链接角色
        response = iam_client.list_roles(PathPrefix='/aws-service-role/')
        roles = response.get('Roles', [])
        
        bedrock_roles = [role for role in roles if 'bedrock' in role['RoleName'].lower()]
        
        if bedrock_roles:
            print("✅ 找到 Bedrock 服务链接角色:")
            for role in bedrock_roles:
                print(f"   - {role['RoleName']}: {role['Arn']}")
        else:
            print("⚠️ 未找到 Bedrock 服务链接角色")
            print("💡 可能需要创建服务链接角色")
        
        return len(bedrock_roles) > 0
        
    except ClientError as e:
        print(f"❌ 检查服务链接角色失败: {e}")
        return False

def create_bedrock_service_linked_role():
    """创建 Bedrock 服务链接角色"""
    print("\n🔗 创建 Bedrock 服务链接角色...")
    
    iam_client = boto3.client('iam')
    
    try:
        response = iam_client.create_service_linked_role(
            AWSServiceName='bedrock.amazonaws.com',
            Description='Service-linked role for Amazon Bedrock'
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ 服务链接角色创建成功: {role_arn}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidInput':
            print("⚠️ 服务链接角色已存在或不需要创建")
            return True
        else:
            print(f"❌ 创建服务链接角色失败: {e}")
            return False

def check_bedrock_model_access():
    """检查 Bedrock 模型访问权限"""
    print("\n🧠 检查 Bedrock 模型访问...")
    
    bedrock_client = boto3.client('bedrock', region_name='us-east-1')
    
    try:
        # 检查模型访问
        response = bedrock_client.get_foundation_model(modelIdentifier='amazon.nova-reel-v1:0')
        
        model_details = response.get('modelDetails', {})
        print("✅ Nova Reel 模型访问正常")
        print(f"   - 模型ID: {model_details.get('modelId')}")
        print(f"   - 状态: {model_details.get('modelLifecycle', {}).get('status')}")
        
        return True
        
    except ClientError as e:
        print(f"❌ 模型访问检查失败: {e}")
        return False

def test_simple_bedrock_call():
    """测试简单的 Bedrock 调用"""
    print("\n🧪 测试简单的 Bedrock 调用...")
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    try:
        # 尝试一个简单的文本生成调用
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
        
        print("✅ 简单 Bedrock 调用成功")
        return True
        
    except ClientError as e:
        print(f"❌ 简单 Bedrock 调用失败: {e}")
        return False

def check_account_limits():
    """检查账户限制"""
    print("\n📊 检查账户限制...")
    
    try:
        # 检查当前用户信息
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        
        print(f"✅ 账户信息:")
        print(f"   - 账户ID: {identity.get('Account')}")
        print(f"   - 用户ARN: {identity.get('Arn')}")
        
        # 检查区域
        session = boto3.Session()
        region = session.region_name or 'us-east-1'
        print(f"   - 当前区域: {region}")
        
        return True
        
    except Exception as e:
        print(f"❌ 账户信息检查失败: {e}")
        return False

def test_alternative_s3_config():
    """测试替代的 S3 配置"""
    print("\n🪣 测试替代的 S3 配置...")
    
    try:
        import base64
        import io
        import random
        from PIL import Image
        
        bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        # 尝试不同的 S3 URI 格式
        test_configs = [
            "s3://nova-reel-20250701132554",
            "s3://nova-reel-20250701132554/",
            "s3://nova-reel-20250701132554/outputs",
        ]
        
        # 创建简单的测试图片
        img = Image.new('RGB', (1280, 720), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        image_data = buffer.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        for i, s3_uri in enumerate(test_configs):
            print(f"🧪 测试配置 {i+1}: {s3_uri}")
            
            try:
                seed = random.randint(0, 2147483646)
                
                model_input = {
                    "taskType": "TEXT_VIDEO",
                    "textToVideoParams": {
                        "text": "A simple test video",
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
                        "durationSeconds": 5,
                        "dimension": "1280x720",
                        "seed": seed,
                    }
                }
                
                output_config = {"s3OutputDataConfig": {"s3Uri": s3_uri}}
                
                response = bedrock_runtime.start_async_invoke(
                    modelId="amazon.nova-reel-v1:0",
                    modelInput=model_input,
                    outputDataConfig=output_config
                )
                
                print(f"✅ 配置 {i+1} 成功! ARN: {response['invocationArn']}")
                return True
                
            except ClientError as e:
                print(f"❌ 配置 {i+1} 失败: {e.response['Error']['Code']}")
                continue
        
        print("❌ 所有 S3 配置都失败了")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def main():
    """主诊断函数"""
    print("🔍 详细的 Bedrock 权限诊断")
    print("=" * 60)
    
    results = []
    
    # 检查各项配置
    results.append(("账户限制", check_account_limits()))
    results.append(("服务链接角色", check_bedrock_service_linked_role()))
    results.append(("模型访问", check_bedrock_model_access()))
    results.append(("简单调用", test_simple_bedrock_call()))
    
    # 如果没有服务链接角色，尝试创建
    if not results[1][1]:
        create_success = create_bedrock_service_linked_role()
        results[1] = ("服务链接角色", create_success)
    
    # 测试替代配置
    results.append(("替代S3配置", test_alternative_s3_config()))
    
    print("\n" + "=" * 60)
    print("📊 诊断结果总结:")
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   - {name}: {status}")
    
    if results[-1][1]:  # 如果替代S3配置成功
        print("\n🎉 找到了可用的配置!")
        print("💡 Nova Reel 应该可以正常工作了")
    else:
        print("\n⚠️ 仍然存在问题，可能的原因:")
        print("   - Bedrock Nova Reel 在当前区域不可用")
        print("   - 需要特殊的账户权限或配额")
        print("   - AWS 服务暂时不可用")

if __name__ == "__main__":
    main()
