import os
import base64
import json
import uuid
import asyncio
import logging
import traceback
import io
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import aiofiles
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nova Reel Video Generator", description="使用 Amazon Bedrock Nova Reel 生成视频")

# 配置目录
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"

# 创建必要的目录
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, STATIC_FOLDER, TEMPLATE_FOLDER]:
    Path(folder).mkdir(exist_ok=True)

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")
templates = Jinja2Templates(directory=TEMPLATE_FOLDER)

# 初始化 Bedrock 客户端
try:
    bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
    logger.info("Bedrock 客户端初始化成功")
except Exception as e:
    logger.error(f"Bedrock 客户端初始化失败: {str(e)}")
    bedrock_client = None

# 支持的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def validate_file_extension(filename: str) -> bool:
    """验证文件扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def resize_image(image_path: str, target_width: int = 1280, target_height: int = 720) -> str:
    """
    异步调整图片尺寸到指定大小
    """
    try:
        def _resize():
            with Image.open(image_path) as img:
                # 转换为RGB模式（如果是RGBA或其他模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整尺寸，保持纵横比
                img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # 保存调整后的图片
                resized_path = image_path.replace('.', '_resized.')
                img_resized.save(resized_path, 'JPEG', quality=95)
                
                return resized_path
        
        # 在线程池中执行图片处理
        loop = asyncio.get_event_loop()
        resized_path = await loop.run_in_executor(None, _resize)
        return resized_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片调整尺寸失败: {str(e)}")

async def image_to_base64(image_path: str) -> str:
    """
    异步将图片转换为base64编码，确保格式正确
    """
    try:
        # 使用 PIL 重新保存图片确保格式正确
        def _process_image():
            with Image.open(image_path) as img:
                # 确保是 RGB 模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 保存为 JPEG 格式到内存
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                buffer.seek(0)
                
                # 读取二进制数据并编码为 base64
                image_data = buffer.read()
                return base64.b64encode(image_data).decode('utf-8')
        
        loop = asyncio.get_event_loop()
        base64_data = await loop.run_in_executor(None, _process_image)
        
        logger.info(f"图片转换为 base64 成功，长度: {len(base64_data)}")
        return base64_data
        
    except Exception as e:
        logger.error(f"图片转base64失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"图片转base64失败: {str(e)}")

async def generate_video_with_nova_reel(image_base64: str, prompt: str, duration: int = 7) -> dict:
    """
    使用 Nova Reel 生成视频 - 支持图片+文本输入
    基于 AWS 官方异步作业示例
    """
    if bedrock_client is None:
        raise HTTPException(status_code=500, detail="Bedrock 客户端未初始化")
    
    # 在函数开始就定义 bucket_name，确保在错误处理中可以访问
    bucket_name = os.environ.get("BEDROCK_VIDEO_BUCKET", "bedrock-video-generation")
    
    # 确保桶名称是唯一的，可以添加账户ID或随机字符串
    import uuid
    bucket_suffix = str(uuid.uuid4())[:8]
    bucket_name = f"{bucket_name}-{bucket_suffix}"
    
    try:
        logger.info(f"开始调用 Nova Reel 异步作业，提示词长度: {len(prompt)}, 时长: {duration}秒")
        
        def _start_async_job():
            import random
            
            # 生成随机种子，确保视频生成结果的唯一性
            seed = random.randint(0, 2147483646)
            
            # 使用预定义的 bedrock 视频生成桶
            output_s3_uri = f"s3://{bucket_name}/nova-reel-outputs"
            
            logger.info(f"使用 Bedrock 视频生成桶: {bucket_name}")
            
            # 构建模型输入 - 包含图片和文本
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
                    "durationSeconds": duration,
                    "dimension": "1280x720",
                    "seed": seed,
                }
            }
            
            # 配置输出到 S3
            output_config = {"s3OutputDataConfig": {"s3Uri": output_s3_uri}}
            
            logger.info(f"启动异步作业: seed={seed}, duration={duration}, s3_uri={output_s3_uri}")
            
            # 启动异步调用
            response = bedrock_client.start_async_invoke(
                modelId="amazon.nova-reel-v1:0",
                modelInput=model_input,
                outputDataConfig=output_config
            )
            
            response["s3_uri"] = output_s3_uri
            response["bucket_name"] = bucket_name
            return response
        
        # 在线程池中执行异步作业启动
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _start_async_job)
        
        invocation_arn = response.get("invocationArn")
        s3_uri = response.get("s3_uri")
        bucket_name = response.get("bucket_name")
        
        logger.info(f"Nova Reel 异步作业启动成功，ARN: {invocation_arn}, S3: {s3_uri}")
        
        return {
            "invocation_arn": invocation_arn,
            "status": "started",
            "prompt": prompt,
            "duration": duration,
            "s3_uri": s3_uri,
            "bucket_name": bucket_name,
            "message": "图片+文本视频生成作业已启动，请等待完成"
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Bedrock 异步作业启动失败: {error_code} - {error_message}")
        
        if "AccessDeniedException" in error_code:
            raise HTTPException(
                status_code=500,
                detail="访问被拒绝，请检查 IAM 权限是否包含 Bedrock 和 S3 访问权限"
            )
        elif "ValidationException" in error_code:
            if "Output Config" in error_message or "Credentials" in error_message:
                # 提供更详细的错误信息和解决方案
                raise HTTPException(
                    status_code=500,
                    detail=f"S3 输出配置错误: {error_message}. 当前使用桶: {bucket_name}. 请确保该桶存在且有访问权限。"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"请求验证失败: {error_message}"
                )
        else:
            raise HTTPException(status_code=500, detail=f"Bedrock API 调用失败: {error_code} - {error_message}")
    except Exception as e:
        logger.error(f"视频生成失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"视频生成失败: {str(e)}")

async def check_video_job_status(invocation_arn: str) -> dict:
    """
    检查视频生成作业状态
    """
    if bedrock_client is None:
        raise HTTPException(status_code=500, detail="Bedrock 客户端未初始化")
    
    try:
        def _check_status():
            response = bedrock_client.get_async_invoke(invocationArn=invocation_arn)
            return response
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _check_status)
        
        status = response.get("status")
        logger.info(f"作业状态检查: {invocation_arn} -> {status}")
        
        return response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"检查作业状态失败: {error_code} - {error_message}")
        raise HTTPException(status_code=500, detail=f"检查作业状态失败: {error_message}")
    except Exception as e:
        logger.error(f"检查作业状态异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检查作业状态异常: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_video")
async def generate_video(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    duration: int = Form(default=7)
):
    """生成视频的API端点"""
    
    logger.info(f"收到视频生成请求: 文件名={image.filename}, 提示词长度={len(prompt)}, 时长={duration}")
    
    # 验证文件
    if not image.filename:
        raise HTTPException(status_code=400, detail="请选择图片文件")
    
    if not validate_file_extension(image.filename):
        raise HTTPException(
            status_code=400, 
            detail="不支持的文件格式，请上传 PNG, JPG, JPEG, GIF 或 BMP 文件"
        )
    
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="请输入提示词")
    
    if duration < 5 or duration > 10:
        raise HTTPException(status_code=400, detail="视频时长必须在5-10秒之间")
    
    file_path = None
    try:
        # 检查文件大小
        contents = await image.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过16MB限制")
        
        logger.info(f"文件大小: {len(contents)} bytes")
        
        # 保存上传的文件
        unique_filename = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        logger.info(f"文件保存成功: {file_path}")
        
        # 检查并调整图片尺寸
        def check_image_size():
            with Image.open(file_path) as img:
                return img.size
        
        loop = asyncio.get_event_loop()
        width, height = await loop.run_in_executor(None, check_image_size)
        
        logger.info(f"原始图片尺寸: {width}x{height}")
        
        if width != 1280 or height != 720:
            logger.info(f"图片尺寸 {width}x{height} 不符合要求，正在调整为 1280x720")
            resized_path = await resize_image(file_path)
            # 删除原始文件，使用调整后的文件
            os.remove(file_path)
            file_path = resized_path
            logger.info(f"图片尺寸调整完成: {file_path}")
        
        # 将图片转换为base64
        logger.info("开始转换图片为base64")
        image_base64 = await image_to_base64(file_path)
        logger.info(f"图片转换完成，base64长度: {len(image_base64)}")
        
        # 生成视频（异步作业）
        logger.info(f"开始生成视频，提示词: {prompt[:100]}..., 时长: {duration}秒")
        
        response = await generate_video_with_nova_reel(image_base64, prompt, duration)
        
        logger.info("视频生成作业启动完成")
        
        # 保存作业信息
        job_filename = f"job_{uuid.uuid4()}.json"
        job_path = os.path.join(OUTPUT_FOLDER, job_filename)
        
        job_data = {
            "invocation_arn": response.get("invocation_arn"),
            "prompt": prompt,
            "duration": duration,
            "status": response.get("status"),
            "timestamp": str(uuid.uuid4()),
            "message": response.get("message"),
            "note": "这是一个异步视频生成作业，请使用 invocation_arn 检查状态"
        }
        
        async with aiofiles.open(job_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(job_data, indent=2, ensure_ascii=False))
        
        logger.info(f"作业信息保存完成: {job_path}")
        
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("临时文件清理完成")
        
        return JSONResponse({
            "success": True,
            "message": "视频生成作业已启动",
            "invocation_arn": response.get("invocation_arn"),
            "job_info_url": f"/download/{job_filename}",
            "status_check_url": f"/check_job/{response.get('invocation_arn')}",
            "prompt": prompt,
            "duration": duration,
            "note": "这是一个异步作业，请使用 status_check_url 检查进度"
        })
        
    except HTTPException:
        # 清理临时文件
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        # 清理临时文件
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        logger.error(f"处理请求时发生未预期的错误: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

@app.get("/download/{filename}")
async def download_video(filename: str):
    """下载生成的结果文件"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        # 根据文件扩展名确定媒体类型
        if filename.endswith('.json'):
            media_type = 'application/json'
        elif filename.endswith('.mp4'):
            media_type = 'video/mp4'
        elif filename.endswith('.avi'):
            media_type = 'video/x-msvideo'
        elif filename.endswith('.mov'):
            media_type = 'video/quicktime'
        else:
            media_type = 'application/octet-stream'
            
        return FileResponse(
            file_path, 
            media_type=media_type,
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        raise HTTPException(status_code=404, detail="文件不存在")

@app.get("/check_job/{invocation_arn:path}")
async def check_job_status(invocation_arn: str):
    """检查视频生成作业状态"""
    try:
        logger.info(f"检查作业状态: {invocation_arn}")
        
        response = await check_video_job_status(invocation_arn)
        status = response.get("status")
        
        result = {
            "invocation_arn": invocation_arn,
            "status": status,
            "response": response
        }
        
        if status == "Completed":
            # 作业完成，获取 S3 位置
            output_config = response.get("outputDataConfig", {})
            s3_config = output_config.get("s3OutputDataConfig", {})
            s3_uri = s3_config.get("s3Uri", "")
            
            result.update({
                "message": "视频生成完成",
                "s3_uri": s3_uri,
                "video_url": f"{s3_uri}/output.mp4" if s3_uri else None
            })
            
        elif status == "Failed":
            result.update({
                "message": "视频生成失败",
                "error": response.get("failureMessage", "未知错误")
            })
            
        elif status == "InProgress":
            result.update({
                "message": "视频生成进行中，请稍后再次检查"
            })
        
        return JSONResponse(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查作业状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检查作业状态失败: {str(e)}")

@app.get("/config_check")
async def config_check():
    """检查应用配置状态"""
    try:
        # 检查 S3 配置
        s3_configured = True
        s3_uri = "s3://your-nova-reel-bucket"  # 这应该与实际配置一致
        
        if "your-nova-reel-bucket" in s3_uri:
            s3_configured = False
        
        # 检查 Bedrock 客户端
        bedrock_available = bedrock_client is not None
        
        # 检查 AWS 凭证
        credentials_available = True
        try:
            # 尝试获取调用者身份
            sts_client = boto3.client('sts', region_name='us-east-1')
            sts_client.get_caller_identity()
        except Exception:
            credentials_available = False
        
        return JSONResponse({
            "bedrock_client": bedrock_available,
            "aws_credentials": credentials_available,
            "s3_configured": s3_configured,
            "s3_uri": s3_uri if s3_configured else "需要配置",
            "recommendations": [
                "配置有效的 S3 桶 URI" if not s3_configured else None,
                "检查 AWS 凭证配置" if not credentials_available else None,
                "检查 Bedrock 客户端初始化" if not bedrock_available else None
            ]
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"配置检查失败: {str(e)}",
            "bedrock_client": False,
            "aws_credentials": False,
            "s3_configured": False
        })

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "Nova Reel Video Generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
