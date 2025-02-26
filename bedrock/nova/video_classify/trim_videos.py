#!/usr/bin/env python3
"""
Script to trim videos to a specified length and upload them to S3.
This script only handles video trimming and S3 uploading, without any classification.
"""
import os
import sys
import csv
import logging
import pandas as pd
import tempfile
import subprocess
import boto3
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def download_video(url: str, output_path: str) -> bool:
    """
    Download video from URL.
    
    Args:
        url: Video URL
        output_path: Path to save the video
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ['curl', '-L', '-o', output_path, url]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        logger.error(f"Error downloading video from {url}: {e}")
        return False

def trim_video(input_path: str, output_path: str, max_duration: int = 30) -> bool:
    """
    Trim video to specified duration.
    
    Args:
        input_path: Path to input video
        output_path: Path to save trimmed video
        max_duration: Maximum duration in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get video duration
        duration = get_video_duration(input_path)
        if duration is None:
            logger.error(f"Could not determine video duration for {input_path}")
            return False
        
        # Trim video if needed
        if duration > max_duration:
            cmd = [
                'ffmpeg', '-i', input_path, 
                '-t', str(max_duration), 
                '-c:v', 'copy', '-c:a', 'copy', 
                output_path
            ]
            subprocess.run(cmd, check=True)
            logger.info(f"Trimmed video from {duration:.2f}s to {max_duration}s")
            return True
        else:
            # Just copy the file if it's already shorter than max_duration
            cmd = ['cp', input_path, output_path]
            subprocess.run(cmd, check=True)
            logger.info(f"Video duration ({duration:.2f}s) is already less than {max_duration}s, no trimming needed")
            return True
    except Exception as e:
        logger.error(f"Error trimming video: {e}")
        return False

def upload_to_s3(file_path: str, bucket_name: str, object_key: str, region: str = "us-east-1") -> str:
    """
    Upload file to S3.
    
    Args:
        file_path: Path to file
        bucket_name: S3 bucket name
        object_key: S3 object key
        region: AWS region
        
    Returns:
        S3 URI if successful, empty string otherwise
    """
    try:
        s3_client = boto3.client('s3', region_name=region)
        s3_client.upload_file(file_path, bucket_name, object_key)
        s3_uri = f"s3://{bucket_name}/{object_key}"
        logger.info(f"Uploaded file to {s3_uri}")
        return s3_uri
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        return ""

def extract_filename_from_url(url: str) -> str:
    """
    Extract filename from URL.
    
    Args:
        url: Video URL
        
    Returns:
        Filename
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)
    return filename

def process_videos(
    input_csv: str = "data/video-input.csv",
    output_csv: str = "data/video-output.csv",
    max_duration: int = 30,
    s3_bucket: str = "video-classify",
    region: str = "us-east-1"
):
    """
    Process videos: download, trim, and upload to S3.
    
    Args:
        input_csv: Path to input CSV file
        output_csv: Path to output CSV file
        max_duration: Maximum duration in seconds
        s3_bucket: S3 bucket name
        region: AWS region
    """
    try:
        # Load input data
        df = pd.read_csv(input_csv)
        logger.info(f"Loaded {len(df)} videos from {input_csv}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        
        # Create output CSV with headers if it doesn't exist
        if not os.path.exists(output_csv):
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'content_id',
                    'original_url',
                    'S3 URI'
                ])
        
        # Process each video
        results = []
        for _, row in df.iterrows():
            content_id = row['content_id']
            video_url = row['media_info']
            
            # Skip if already processed
            if os.path.exists(output_csv):
                output_df = pd.read_csv(output_csv)
                if str(content_id) in output_df['content_id'].astype(str).values:
                    logger.info(f"Skipping already processed video: {content_id}")
                    continue
            
            logger.info(f"Processing video: {content_id}, URL: {video_url}")
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=True) as temp_video:
                temp_video_path = temp_video.name
                
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=True) as trimmed_video:
                trimmed_video_path = trimmed_video.name
            
            try:
                # Download video
                if not download_video(video_url, temp_video_path):
                    logger.error(f"Failed to download video: {video_url}")
                    continue
                
                # Trim video
                if not trim_video(temp_video_path, trimmed_video_path, max_duration):
                    logger.error(f"Failed to trim video: {temp_video_path}")
                    continue
                
                # Extract filename from URL
                filename = extract_filename_from_url(video_url)
                
                # Upload to S3
                s3_object_key = filename
                s3_uri = upload_to_s3(trimmed_video_path, s3_bucket, s3_object_key, region)
                
                if not s3_uri:
                    logger.error(f"Failed to upload video to S3: {trimmed_video_path}")
                    continue
                
                # Write to output CSV
                with open(output_csv, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        content_id,
                        video_url,
                        s3_uri
                    ])
                
                logger.info(f"Successfully processed video: {content_id}")
                
                # Add to results
                results.append({
                    'content_id': content_id,
                    'original_url': video_url,
                    's3_uri': s3_uri
                })
                
            except Exception as e:
                logger.error(f"Error processing video {content_id}: {e}")
                continue
            finally:
                # Clean up temporary files
                if os.path.exists(temp_video_path):
                    os.unlink(temp_video_path)
                if os.path.exists(trimmed_video_path):
                    os.unlink(trimmed_video_path)
        
        logger.info(f"Processed {len(results)} videos")
        logger.info(f"Results written to {output_csv}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing videos: {e}")
        raise

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trim videos and upload to S3')
    parser.add_argument('--input', default='data/video-input.csv', help='Path to input CSV file')
    parser.add_argument('--output', default='data/video-output.csv', help='Path to output CSV file')
    parser.add_argument('--max-duration', type=int, default=30, help='Maximum duration in seconds')
    parser.add_argument('--s3-bucket', default='video-classify', help='S3 bucket name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    process_videos(
        input_csv=args.input,
        output_csv=args.output,
        max_duration=args.max_duration,
        s3_bucket=args.s3_bucket,
        region=args.region
    )

if __name__ == '__main__':
    main()
