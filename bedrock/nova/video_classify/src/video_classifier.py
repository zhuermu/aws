"""
Video classification module.
"""
import os
import json
import csv
import logging
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd

from .common import (
    call_bedrock_llm,
    video_to_text,
    calibrate_classification,
    parse_json_result
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoClassifier:
    """Video classifier class."""
    
    def __init__(
        self,
        prompt_path: str = "prompt/one_step_prompt.md",
        model_id: str = "amazon.nova-lite-v1:0",
        region: str = "us-east-1",
        output_csv: str = "data/classification_results.csv",
        categories_path: str = "category.json"
    ):
        """
        Initialize the video classifier.
        
        Args:
            prompt_path: Path to the prompt file
            model_id: Model ID to use
            region: AWS region
            output_csv: Path to output CSV file
            categories_path: Path to the categories JSON file
        """
        self.prompt_path = prompt_path
        self.model_id = model_id
        self.region = region
        self.output_csv = output_csv
        self.system_prompt = "You are a professional video expert. You are given a video, and you need to classify the video into categories and tags."
        
        # Load categories from JSON file
        try:
            with open(categories_path, 'r', encoding='utf-8') as f:
                self.categories_json = json.load(f)
                logger.info(f"Loaded categories from {categories_path}")
        except Exception as e:
            logger.error(f"Error loading categories from {categories_path}: {e}")
            raise
        
        # Load prompt and replace categories placeholder
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
                
            # Convert categories to string format for prompt
            categories_str = json.dumps(self.categories_json, indent=2)
            
            # Replace placeholder with categories
            self.prompt = prompt_template.replace("${catetorys}", categories_str)
            logger.info(f"Loaded prompt from {prompt_path} and replaced categories placeholder")
        except Exception as e:
            logger.error(f"Error loading prompt from {prompt_path}: {e}")
            raise
            
        # Create output CSV if it doesn't exist
        if not os.path.exists(self.output_csv):
            try:
                with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar='\\')
                    writer.writerow([
                        'S3 URI',
                        'catetory',
                        'tags',
                        'result',
                        'new catetory',
                        'new tags',
                        'Input Tokens',
                        'Output Tokens'
                    ])
            except Exception as e:
                logger.error(f"Error creating output CSV {self.output_csv}: {e}")
                raise
    
    def classify_video(self, s3_uri: str) -> Dict[str, Any]:
        """
        Classify a video.
        
        Args:
            s3_uri: S3 URI of the video
            
        Returns:
            Classification results
        """
        try:
            logger.info(f"Classifying video: {s3_uri}")
            
            # Call Bedrock LLM
            response_text, token_usage = call_bedrock_llm(
                s3_uri=s3_uri,
                prompt=self.prompt,
                system=self.system_prompt,
                model_id=self.model_id,
                region=self.region,
                max_tokens=512,
                temperature=0.0,
                top_p=0.9,
                sleep_time=60.0
            )
            
            logger.info(f"Raw response: {response_text}")
            
            # Parse JSON result
            classification_result = parse_json_result(
                text=response_text,
                model_id=self.model_id,
                region=self.region
            )
            
            logger.info(f"Parsed classification result: {classification_result}")
            
            # Calibrate classification results
            calibrated_results = []
            
            for category in classification_result.get('catetorys', []):
                category1 = category.get('catetory1', '')
                category2 = category.get('catetory2', '')
                category3 = category.get('catetory3', [])
                
                calibrated = calibrate_classification(
                    category1=category1,
                    category2=category2,
                    category3=category3,
                    categories_json=self.categories_json,
                    region=self.region
                )
                
                calibrated_results.append({
                    'original': category,
                    'calibrated': {
                        'catetory1': calibrated['calibrated_category1'],
                        'catetory2': calibrated['calibrated_category2'],
                        'catetory3': calibrated['calibrated_category3'],
                        'weight': category.get('weight', {})
                    }
                })
            
            # Prepare final result
            final_result = {
                's3_uri': s3_uri,
                'original_classification': classification_result,
                'calibrated_classification': {
                    'catetorys': [item['calibrated'] for item in calibrated_results],
                    'tags': classification_result.get('tags', [])
                },
                'token_usage': token_usage
            }
            
            # Write to CSV
            self._write_to_csv(
                s3_uri=s3_uri,
                classification_result=final_result['calibrated_classification'],
                token_usage=token_usage
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error classifying video {s3_uri}: {e}")
            raise
    
    def _write_to_csv(
        self, 
        s3_uri: str, 
        classification_result: Dict[str, Any],
        token_usage: Dict[str, int]
    ) -> None:
        """
        Write classification results to CSV.
        
        Args:
            s3_uri: S3 URI of the video
            classification_result: Classification result
            token_usage: Token usage
        """
        try:
            # Convert classification result to string
            classification_str = json.dumps(classification_result.get('catetorys', []))
            tags_str = json.dumps(classification_result.get('tags', []))
            
            # Check if we have original data in the input CSV
            original_category = ''
            original_tags = ''
            original_result = ''
            
            # Skip trying to read the original data from CSV since it's causing parsing issues
            # Just proceed with writing the new classification results
            logger.info("Skipping reading original data from classification_data.csv due to parsing issues")
            
            # Write to CSV with proper quoting to handle JSON data with commas
            with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar='\\')
                writer.writerow([
                    s3_uri,
                    original_category,  # original catetory
                    original_tags,      # original tags
                    original_result,    # original result
                    classification_str, # new catetory
                    tags_str,           # new tags
                    token_usage.get('input_tokens', 0),
                    token_usage.get('output_tokens', 0)
                ])
                
            logger.info(f"Results written to {self.output_csv}")
            
        except Exception as e:
            logger.error(f"Error writing to CSV {self.output_csv}: {e}")
            raise

class TwoStepVideoClassifier(VideoClassifier):
    """Two-step video classifier class."""
    
    def __init__(
        self,
        first_prompt_path: str = "prompt/two_step1_prompt.md",
        second_prompt_path: str = "prompt/two_stop2_prompt.md",
        model_id: str = "amazon.nova-lite-v1:0",
        region: str = "us-east-1",
        output_csv: str = "data/classification_results.csv",
        categories_path: str = "category.json"
    ):
        """
        Initialize the two-step video classifier.
        
        Args:
            first_prompt_path: Path to the first prompt file
            second_prompt_path: Path to the second prompt file
            model_id: Model ID to use
            region: AWS region
            output_csv: Path to output CSV file
            categories_path: Path to the categories JSON file
        """
        # Initialize with second prompt for categories
        super().__init__(
            prompt_path=second_prompt_path,
            model_id=model_id,
            region=region,
            output_csv=output_csv,
            categories_path=categories_path
        )
        
        self.first_prompt_path = first_prompt_path
        
        # Load first prompt
        try:
            with open(first_prompt_path, 'r', encoding='utf-8') as f:
                self.first_prompt = f.read()
            logger.info(f"Loaded first prompt from {first_prompt_path}")
        except Exception as e:
            logger.error(f"Error loading first prompt from {first_prompt_path}: {e}")
            raise
    
    def classify_video(self, s3_uri: str) -> Dict[str, Any]:
        """
        Classify a video using two-step approach.
        
        Args:
            s3_uri: S3 URI of the video
            
        Returns:
            Classification results
        """
        try:
            logger.info(f"Classifying video (two-step): {s3_uri}")
            
            # Step 1: Get video understanding
            first_response_text, first_token_usage = call_bedrock_llm(
                s3_uri=s3_uri,
                prompt=self.first_prompt,
                temperature=0.0,
                top_p=0.9,
                max_tokens=512,
                system="You are a video content analyst. Describe the video content in sample text.",
                model_id=self.model_id,
                region=self.region,
                sleep_time=40.0
            )
            
            logger.info(f"First step response: {first_response_text}")
            
            # Step 2: Classify based on understanding
            # Replace ${video_content} with the first step response
            second_prompt = self.prompt.replace("${video_content}", first_response_text)
            
            second_response_text, second_token_usage = call_bedrock_llm(
                s3_uri=s3_uri,
                prompt=second_prompt,
                temperature=0.0,
                top_p=0.9,
                max_tokens=512,
                system=self.system_prompt,
                model_id=self.model_id,
                region=self.region,
                sleep_time=20
            )
            
            logger.info(f"Second step response: {second_response_text}")
            
            # Parse JSON result
            classification_result = parse_json_result(
                text=second_response_text,
                model_id=self.model_id,
                region=self.region
            )
            
            logger.info(f"Parsed classification result: {classification_result}")
            
            # Calibrate classification results
            calibrated_results = []
            
            for category in classification_result.get('catetorys', []):
                category1 = category.get('catetory1', '')
                category2 = category.get('catetory2', '')
                category3 = category.get('catetory3', [])
                
                calibrated = calibrate_classification(
                    category1=category1,
                    category2=category2,
                    category3=category3,
                    categories_json=self.categories_json,
                    region=self.region
                )
                
                calibrated_results.append({
                    'original': category,
                    'calibrated': {
                        'catetory1': calibrated['calibrated_category1'],
                        'catetory2': calibrated['calibrated_category2'],
                        'catetory3': calibrated['calibrated_category3'],
                        'weight': category.get('weight', {})
                    }
                })
            
            # Combine token usage
            combined_token_usage = {
                'input_tokens': first_token_usage.get('input_tokens', 0) + second_token_usage.get('input_tokens', 0),
                'output_tokens': first_token_usage.get('output_tokens', 0) + second_token_usage.get('output_tokens', 0)
            }
            
            # Prepare final result
            final_result = {
                's3_uri': s3_uri,
                'video_understanding': first_response_text,
                'original_classification': classification_result,
                'calibrated_classification': {
                    'catetorys': [item['calibrated'] for item in calibrated_results],
                    'tags': classification_result.get('tags', [])
                },
                'token_usage': combined_token_usage
            }
            
            # Write to CSV
            self._write_to_csv(
                s3_uri=s3_uri,
                classification_result=final_result['calibrated_classification'],
                token_usage=combined_token_usage
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error classifying video {s3_uri} with two-step approach: {e}")
            raise
