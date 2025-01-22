from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import boto3
import os
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware
import asyncio

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize AWS clients
s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bedrock_client = boto3.client('bedrock-runtime',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

@app.post("/upload")
async def upload_file(
    text: str = Form(None),
    file: UploadFile = None, # file name character just support a-z, A-Z, 0-9, -, _
    image: UploadFile = None,
    video: UploadFile = None
):
    try:
        # read file bytes as base64
        if file:
            file_bytes = await file.read()
        if image:
            image_bytes = await image.read()
        # Handle file uploads
        if video:
            video_bytes = await video.read()
    except asyncio.CancelledError:
        print("Request was cancelled")
        # Perform any necessary cleanup here
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        # Handle other exceptions

    # Call Bedrock
    async def generate_response():
        #prompt = json.dumps(response_data)
        MODEL_ID = "amazon.nova-pro-v1:0"
        contents = [{"text": text}]
        
        if file:
            # read file extension
            extension = file.filename.split('.')[-1]
            filename =  file.filename.split('.')[0]
            contents.append({
                "document": {
                    "name": filename,
                    "format": extension,
                    "source": {
                        "bytes": file_bytes
                    }
                }
            })
        if image:
            extension = image.filename.split('.')[-1]
            contents.append({
                "image": {
                    "format": extension,
                    "source": {
                        "bytes": image_bytes
                    }
                }
            })
        if video:
            # Check if video is larger than 10MB
            if video.size > 10 * 1024 * 1024:
                # Upload to S3
                bucket_name = os.getenv('AWS_S3_BUCKET')
                bucket_prefix = os.getenv('AWS_S3_PREFIX')
                file_key = f"{bucket_prefix}/{video.filename}"
                s3_url = f"s3://{bucket_name}/{file_key}"
                # Check if file exists
                try:
                    s3_client.head_object(Bucket=bucket_name, Key=file_key)
                except:
                    print("File not found, uploading to S3")
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=file_key,
                        Body=video_bytes
                    )
                contents.append({
                    "video": {
                        "format": 'mp4',
                        "source": {
                            "s3Location": {
                            # Replace the S3 URI
                                "uri": s3_url
                            }
                        }
                    }
                })
            else:
                contents.append({
                    "video": {
                        "format": 'mp4',
                        "source": {
                            "bytes": video_bytes
                        }
                    }
                })
        messages = [{"role": "user", "content": contents}]

        response = bedrock_client.converse_stream(
            modelId=MODEL_ID,
            messages=messages,
            inferenceConfig={"temperature": 0.0}
        )

        async def async_iterate():
            for event in response.get('stream'):
                if 'messageStart' in event:
                    yield f"data: {json.dumps({'role': event['messageStart']['role']})}\n\n"

                if 'contentBlockDelta' in event:
                    yield f"data: {json.dumps({'text': event['contentBlockDelta']['delta']['text']})}\n\n"

                if 'messageStop' in event:
                    yield f"data: {json.dumps({'stopReason': event['messageStop']['stopReason']})}\n\n"

                if 'metadata' in event:
                    metadata = event['metadata']
                    if 'usage' in metadata:
                        yield f"data: {json.dumps({'usage': metadata['usage']})}\n\n"
                        yield f"data: {json.dumps({'inputTokens': metadata['usage']['inputTokens']})}\n\n"
                        yield f"data: {json.dumps({'outputTokens': metadata['usage']['outputTokens']})}\n\n"
                        yield f"data: {json.dumps({'totalTokens': metadata['usage']['totalTokens']})}\n\n"
                    if 'metrics' in metadata:
                        latencyMs = metadata['metrics']['latencyMs']
                        yield f"data: {json.dumps({'latencyMs': f'{latencyMs} milliseconds'})}\n\n"
           

        async for chunk in async_iterate():
            yield chunk
                    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    import uvicorn
