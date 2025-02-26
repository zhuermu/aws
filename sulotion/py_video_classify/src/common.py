"""
Common utility functions for video classification.
"""
import os
import json
import boto3
import logging
import time
from typing import Dict, Any, List, Tuple, Optional
import tempfile
import subprocess
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def call_bedrock_llm(
    s3_uri: str, 
    prompt: str, 
    system: str, 
    model_id: str = "amazon.nova-lite-v1:0",
    max_tokens: int = 4096,
    temperature: float = 0.5,
    top_p: float = 0.9,
    region: str = "us-east-1",
    sleep_time: float = 1.0  # Add sleep time parameter with default of 1 second
) -> Tuple[str, Dict[str, int]]:
    """
    Call Bedrock LLM with video input.
    
    Args:
        s3_uri: S3 URI of the video
        prompt: Prompt text
        system: System prompt
        model_id: Model ID
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        top_p: Top-p for sampling
        region: AWS region
        sleep_time: Time to sleep after API call to avoid rate limits (in seconds)
        
    Returns:
        Tuple of (response text, token usage)
    """
    try:
        # Create Bedrock Runtime client
        bedrock_client = boto3.client('bedrock-runtime', region_name=region)
        
        # Create video content block
        video_content = {
            "video": {
                "format": "mp4",
                "source": {
                    "s3Location": {
                        "uri": s3_uri
                    }
                }
            }
        }
        
        # Create text content block
        text_content = {
            "text": prompt
        }
        
        # Create message with both video and text content
        message = {
            "role": "user",
            "content": [video_content, text_content]
        }
        
        # Create system message
        system_message = {
            "text": system
        }
        
        # Create request
        request = {
            "modelId": model_id,
            "system": [system_message],
            "messages": [message],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p
            }
        }
        
        # Call Bedrock
        response = bedrock_client.converse(**request)
        
        # Extract response text
        response_text = response['output']['message']['content'][0]['text']
        
        # Extract token usage
        token_usage = {
            "input_tokens": response.get('usage', {}).get('inputTokens', 0),
            "output_tokens": response.get('usage', {}).get('outputTokens', 0)
        }
        
        # Sleep to avoid hitting API rate limits
        logger.info(f"Sleeping for {sleep_time} seconds to avoid API rate limits")
        time.sleep(sleep_time)
        
        return response_text, token_usage
        
    except Exception as e:
        logger.error(f"Error calling Bedrock LLM: {e}")
        raise

def get_video_duration(input_path: str) -> Optional[float]:
    """
    Get video duration using ffprobe.
    
    Args:
        input_path: Path to input video
        
    Returns:
        Duration in seconds or None if failed
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        logger.error(f"Error getting video duration: {e}")
        return None

def video_to_text(s3_uri: str, max_duration: int = 30, region: str = "us-east-1") -> str:
    """
    Convert video to text using Amazon Transcribe.
    
    Args:
        s3_uri: S3 URI of the video
        max_duration: Maximum duration in seconds
        region: AWS region
        
    Returns:
        Transcribed text
    """
    try:
        # Download video from S3
        s3_client = boto3.client('s3', region_name=region)
        bucket_name = s3_uri.split('/')[2]
        object_key = '/'.join(s3_uri.split('/')[3:])
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
            temp_video_path = temp_video.name
            s3_client.download_file(bucket_name, object_key, temp_video_path)
        
        # Trim video if needed
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as trimmed_video:
            trimmed_video_path = trimmed_video.name
            
            # Get video duration
            duration = get_video_duration(temp_video_path)
            if duration is None:
                raise ValueError("Could not determine video duration")
            
            if duration > max_duration:
                # Trim video
                cmd = [
                    'ffmpeg', '-i', temp_video_path, 
                    '-t', str(max_duration), 
                    '-c:v', 'copy', '-c:a', 'copy', 
                    trimmed_video_path
                ]
                subprocess.run(cmd, check=True)
            else:
                trimmed_video_path = temp_video_path
        
        # Extract audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
            audio_path = audio_file.name
            cmd = [
                'ffmpeg', '-i', trimmed_video_path, 
                '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', 
                audio_path
            ]
            subprocess.run(cmd, check=True)
        
        # Upload audio to S3
        audio_s3_key = f"temp-audio/{os.path.basename(audio_path)}"
        s3_client.upload_file(audio_path, bucket_name, audio_s3_key)
        audio_s3_uri = f"s3://{bucket_name}/{audio_s3_key}"
        
        # Start transcription job
        transcribe_client = boto3.client('transcribe', region_name=region)
        job_name = f"video-classify-{os.path.basename(audio_path).split('.')[0]}"
        
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': audio_s3_uri},
            MediaFormat='wav',
            LanguageOptions=['en-US', 'zh-CN', 'ja-JP', 'ko-KR'],
            IdentifyLanguage=True,
            OutputBucketName=bucket_name
        )
        
        # Wait for transcription job to complete
        import time
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)
        
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            # Get transcription results
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # Download transcript
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as transcript_file:
                transcript_path = transcript_file.name
                
                # Parse S3 URI from the HTTPS URI
                transcript_s3_key = transcript_uri.split(f"{bucket_name}/")[1]
                s3_client.download_file(bucket_name, transcript_s3_key, transcript_path)
                
                with open(transcript_path, 'r') as f:
                    transcript_data = json.load(f)
                    
                transcript_text = transcript_data['results']['transcripts'][0]['transcript']
                
                # Clean up
                os.unlink(temp_video_path)
                if trimmed_video_path != temp_video_path:
                    os.unlink(trimmed_video_path)
                os.unlink(audio_path)
                os.unlink(transcript_path)
                
                # Delete temporary S3 objects
                s3_client.delete_object(Bucket=bucket_name, Key=audio_s3_key)
                s3_client.delete_object(Bucket=bucket_name, Key=transcript_s3_key)
                
                return transcript_text
        else:
            error_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown error')
            raise Exception(f"Transcription job failed: {error_reason}")
            
    except Exception as e:
        logger.error(f"Error in video_to_text: {e}")
        raise

def calibrate_classification(
    category1: str, 
    category2: str, 
    category3: List[str], 
    categories_json: Dict[str, Any],
    model_id: str = "amazon.titan-embed-text-v1",
    region: str = "us-east-1"
) -> Dict[str, Any]:
    """
    Calibrate classification results using embedding model.
    
    Args:
        category1: First level category
        category2: Second level category
        category3: List of third level categories
        categories_json: Categories JSON object
        model_id: Embedding model ID
        region: AWS region
        
    Returns:
        Calibrated classification results
    """
    try:
        # Create Bedrock Runtime client
        bedrock_client = boto3.client('bedrock-runtime', region_name=region)
        
        # Function to get embedding
        def get_embedding(text: str) -> List[float]:
            response = bedrock_client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "inputText": text
                })
            )
            response_body = json.loads(response['body'].read())
            
            # Sleep to avoid hitting API rate limits
            logger.info("Sleeping for 1 second to avoid embedding API rate limits")
            time.sleep(1.0)
            
            return response_body['embedding']
        
        # Function to calculate cosine similarity
        def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        # Function to find most similar category
        def find_most_similar(text: str, candidates: List[str]) -> Tuple[str, float]:
            text_embedding = get_embedding(text)
            similarities = []
            
            for candidate in candidates:
                candidate_embedding = get_embedding(candidate)
                similarity = cosine_similarity(text_embedding, candidate_embedding)
                similarities.append((candidate, similarity))
            
            return max(similarities, key=lambda x: x[1])
        
        # Validate and calibrate category1
        level1_categories = list(categories_json.keys())
        if category1 not in level1_categories:
            calibrated_category1, similarity = find_most_similar(category1, level1_categories)
        else:
            calibrated_category1 = category1
            similarity = 1.0
            
        # Validate and calibrate category2
        if calibrated_category1 in categories_json:
            level2_categories = list(categories_json[calibrated_category1].keys())
            if category2 not in level2_categories:
                calibrated_category2, similarity = find_most_similar(category2, level2_categories)
            else:
                calibrated_category2 = category2
                similarity = 1.0
        else:
            calibrated_category2 = category2  # Keep original if level1 not found
            
        # Validate and calibrate category3
        calibrated_category3 = []
        if calibrated_category1 in categories_json and calibrated_category2 in categories_json[calibrated_category1]:
            level3_categories = list(categories_json[calibrated_category1][calibrated_category2].keys())
            
            for cat3 in category3:
                if cat3 not in level3_categories:
                    calibrated_cat3, similarity = find_most_similar(cat3, level3_categories)
                    calibrated_category3.append(calibrated_cat3)
                else:
                    calibrated_category3.append(cat3)
        else:
            calibrated_category3 = category3  # Keep original if level2 not found
            
        return {
            "calibrated_category1": calibrated_category1,
            "calibrated_category2": calibrated_category2,
            "calibrated_category3": calibrated_category3
        }
        
    except Exception as e:
        logger.error(f"Error in calibrate_classification: {e}")
        raise

def parse_json_result(text: str, model_id: str = "amazon.nova-lite-v1:0", region: str = "us-east-1") -> Dict[str, Any]:
    """
    Parse JSON result from text.
    
    Args:
        text: Text containing JSON
        model_id: Model ID for fixing JSON if needed
        region: AWS region
        
    Returns:
        Parsed JSON object
    """
    try:
        # Try to extract JSON from text
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = text[json_start:json_end]
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                # JSON is invalid, try to fix with Nova Lite
                bedrock_client = boto3.client('bedrock-runtime', region_name=region)
                
                prompt = f"""
                The following text contains a JSON object that is not properly formatted.
                Please fix the JSON formatting issues and return only the corrected JSON object.
                
                ```
                {json_text}
                ```
                """
                
                system = "You are a helpful assistant that specializes in fixing JSON formatting issues."
                
                request = {
                    "modelId": model_id,
                    "system": [{"text": system}],
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 512,
                        "temperature": 0.0,
                        "topP": 1.0
                    }
                }
                
                response = bedrock_client.converse(**request)
                fixed_json_text = response['output']['message']['content'][0]['text']
                
                # Sleep to avoid hitting API rate limits
                logger.info("Sleeping for 1 second to avoid API rate limits")
                time.sleep(1.0)
                
                # Extract JSON from the fixed text
                json_start = fixed_json_text.find('{')
                json_end = fixed_json_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    fixed_json_text = fixed_json_text[json_start:json_end]
                    return json.loads(fixed_json_text)
                else:
                    raise ValueError("Could not extract JSON from fixed text")
        else:
            raise ValueError("No JSON object found in text")
            
    except Exception as e:
        logger.error(f"Error parsing JSON result: {e}")
        raise
