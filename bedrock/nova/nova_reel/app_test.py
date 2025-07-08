import os
import base64
import json
import uuid
import asyncio
import logging
import traceback
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

app = FastAPI(title="Nova Reel Video Generator (Test)", description="测试版本 - 使用 Nova Lite 模拟视频生成")

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
    """异步调整图片尺寸到指定大小"""
    try:
        def _resize():
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                resized_path = image_path.replace('.', '_resized.')
                img_resized.save(resized_path, 'JPEG', quality=95)
                return resized_path
        
        loop = asyncio.get_event_loop()
        resized_path = await loop.run_in_executor(None, _resize)
        return resized_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片调整尺寸失败: {str(e)}")

async def image_to_base64(image_path: str) -> str:
    """异步将图片转换为base64编码"""
    try:
        async with aiofiles.open(image_path, 'rb') as image_file:
            image_data = await image_file.read()
            return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片转base64失败: {str(e)}")

async def simulate_video_generation(image_base64: str, prompt: str, duration: int = 7) -> dict:
    """
    模拟视频生成 - 使用 Nova Lite 来测试流程
    """
    if bedrock_client is None:
        raise HTTPException(status_code=500, detail="Bedrock 客户端未初始化")
    
    try:
        logger.info(f"开始模拟视频生成，提示词长度: {len(prompt)}, 时长: {duration}秒")
        
        def _call_bedrock():
            # 使用 Nova Lite 来测试 API 调用
            response = bedrock_client.converse(
                modelId="amazon.nova-lite-v1:0",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": f"Describe a {duration}-second video that could be created from this image with the following description: {prompt}. Please provide a detailed description of what the video would look like."
                            },
                            {
                                "image": {
                                    "format": "jpeg",
                                    "source": {
                                        "bytes": image_base64
                                    }
                                }
                            }
                        ]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 1000,
                    "temperature": 0.7
                }
            )
            return response
        
        # 在线程池中执行 Bedrock 调用
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call_bedrock)
        
        logger.info("模拟视频生成 API 调用成功")
        
        # 模拟视频生成结果
        video_description = ""
        if 'output' in response and 'message' in response['output']:
            content = response['output']['message'].get('content', [])
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    video_description = item['text']
                    break
        
        return {
            "success": True,
            "video_description": video_description,
            "prompt": prompt,
            "duration": duration,
            "model_used": "amazon.nova-lite-v1:0 (模拟)",
            "note": "这是一个模拟响应，实际的 Nova Reel 视频生成功能正在开发中"
        }
        
    except NoCredentialsError:
        logger.error("AWS 凭证未配置")
        raise HTTPException(status_code=500, detail="AWS 凭证未配置，请检查 AWS 配置")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Bedrock API 调用失败: {error_code} - {error_message}")
        raise HTTPException(status_code=500, detail=f"Bedrock API 调用失败: {error_message}")
    except Exception as e:
        logger.error(f"模拟视频生成失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"模拟视频生成失败: {str(e)}")

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
    """生成视频的API端点（测试版本）"""
    
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
            os.remove(file_path)
            file_path = resized_path
            logger.info(f"图片尺寸调整完成: {file_path}")
        
        # 将图片转换为base64
        logger.info("开始转换图片为base64")
        image_base64 = await image_to_base64(file_path)
        logger.info(f"图片转换完成，base64长度: {len(image_base64)}")
        
        # 模拟视频生成
        logger.info(f"开始模拟视频生成，提示词: {prompt[:100]}..., 时长: {duration}秒")
        
        response = await simulate_video_generation(image_base64, prompt, duration)
        
        logger.info("模拟视频生成完成")
        
        # 创建模拟的视频文件信息
        output_filename = f"video_{uuid.uuid4()}.json"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # 保存生成结果
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(response, indent=2, ensure_ascii=False))
        
        logger.info(f"结果文件创建完成: {output_path}")
        
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("临时文件清理完成")
        
        return JSONResponse({
            "success": True,
            "message": "模拟视频生成成功",
            "video_url": f"/download/{output_filename}",
            "video_filename": output_filename,
            "prompt": prompt,
            "duration": duration,
            "video_description": response.get("video_description", ""),
            "note": "这是一个测试版本，使用 Nova Lite 模拟了视频生成过程"
        })
        
    except HTTPException:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
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
        return FileResponse(
            file_path, 
            media_type='application/json',
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        raise HTTPException(status_code=404, detail="文件不存在")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "Nova Reel Video Generator (Test Version)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
