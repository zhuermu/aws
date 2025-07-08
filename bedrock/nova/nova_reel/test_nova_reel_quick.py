#!/usr/bin/env python3

import base64
import io
import random
from PIL import Image
import boto3
from botocore.exceptions import ClientError

def quick_test():
    """快速测试 Nova Reel 配置"""
    print("🎬 快速测试 Nova Reel 配置")
    
    try:
        bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        # 创建简单测试图片
        img = Image.new('RGB', (1280, 720), color='orange')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        image_data = buffer.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 配置请求
        seed = random.randint(0, 2147483646)
        prompt = "A beautiful orange sunset with gentle movements"
        
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
        
        output_config = {"s3OutputDataConfig": {"s3Uri": "s3://nova-reel-20250701132554/test-output"}}
        
        print(f"🚀 启动测试作业...")
        response = bedrock_runtime.start_async_invoke(
            modelId="amazon.nova-reel-v1:0",
            modelInput=model_input,
            outputDataConfig=output_config
        )
        
        invocation_arn = response["invocationArn"]
        print(f"✅ 作业启动成功!")
        print(f"ARN: {invocation_arn}")
        
        # 检查状态
        job_status = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)
        print(f"状态: {job_status['status']}")
        
        return True
        
    except ClientError as e:
        print(f"❌ 测试失败: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 配置成功! 现在可以使用 Web 应用了")
        print("🌐 访问: http://localhost:8000")
    else:
        print("\n❌ 配置仍有问题")
