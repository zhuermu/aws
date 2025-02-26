"""
Video evaluation module.
"""
import os
import json
import csv
import logging
import pandas as pd
import boto3
from typing import Dict, Any, List, Tuple, Optional

from .common import call_bedrock_llm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoEvaluator:
    """Video evaluator class."""
    
    def __init__(
        self,
        classification_csv: str,
        ground_truth_csv: str,
        model_id: str = "amazon.nova-lite-v1:0",
        region: str = "us-east-1",
        output_csv: str = "evaluation_results.csv"
    ):
        """
        Initialize the video evaluator.
        
        Args:
            classification_csv: Path to classification results CSV
            ground_truth_csv: Path to ground truth CSV
            model_id: Model ID to use for evaluation
            region: AWS region
            output_csv: Path to output CSV file
        """
        self.classification_csv = classification_csv
        self.ground_truth_csv = ground_truth_csv
        self.model_id = model_id
        self.region = region
        self.output_csv = output_csv
        
        # Create output CSV if it doesn't exist
        if not os.path.exists(self.output_csv):
            try:
                with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'S3 URI', 
                        'Accuracy Score',
                        'Category Accuracy',
                        'Tag Accuracy',
                        'Input Tokens',
                        'Output Tokens'
                    ])
            except Exception as e:
                logger.error(f"Error creating output CSV {self.output_csv}: {e}")
                raise
    
    def evaluate_all(self) -> Dict[str, Any]:
        """
        Evaluate all videos in the classification results.
        
        Returns:
            Evaluation results
        """
        try:
            # Load classification results
            classification_df = pd.read_csv(self.classification_csv)
            
            # Load ground truth
            ground_truth_df = pd.read_csv(self.ground_truth_csv)
            
            # Merge dataframes on S3 URI
            merged_df = pd.merge(
                classification_df, 
                ground_truth_df, 
                on='S3 URI', 
                suffixes=('_pred', '_true')
            )
            
            # Evaluate each video
            results = []
            for _, row in merged_df.iterrows():
                s3_uri = row['S3 URI']
                
                # Parse classification results
                try:
                    classification_result = json.loads(row['Classification Result'])
                except:
                    classification_result = []
                    
                try:
                    tags_result = json.loads(row['Tags'])
                except:
                    tags_result = []
                
                # Parse ground truth
                try:
                    ground_truth_classification = json.loads(row['Classification Result_true'])
                except:
                    ground_truth_classification = []
                    
                try:
                    ground_truth_tags = json.loads(row['Tags_true'])
                except:
                    ground_truth_tags = []
                
                # Evaluate
                result = self.evaluate_video(
                    s3_uri=s3_uri,
                    classification_result=classification_result,
                    tags_result=tags_result,
                    ground_truth_classification=ground_truth_classification,
                    ground_truth_tags=ground_truth_tags
                )
                
                results.append(result)
            
            # Calculate overall accuracy
            if results:
                overall_accuracy = sum(r['accuracy_score'] for r in results) / len(results)
                category_accuracy = sum(r['category_accuracy'] for r in results) / len(results)
                tag_accuracy = sum(r['tag_accuracy'] for r in results) / len(results)
            else:
                overall_accuracy = 0.0
                category_accuracy = 0.0
                tag_accuracy = 0.0
            
            return {
                'overall_accuracy': overall_accuracy,
                'category_accuracy': category_accuracy,
                'tag_accuracy': tag_accuracy,
                'individual_results': results
            }
            
        except Exception as e:
            logger.error(f"Error evaluating videos: {e}")
            raise
    
    def evaluate_video(
        self,
        s3_uri: str,
        classification_result: List[Dict[str, Any]],
        tags_result: List[Dict[str, Any]],
        ground_truth_classification: List[Dict[str, Any]],
        ground_truth_tags: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate a single video.
        
        Args:
            s3_uri: S3 URI of the video
            classification_result: Classification result
            tags_result: Tags result
            ground_truth_classification: Ground truth classification
            ground_truth_tags: Ground truth tags
            
        Returns:
            Evaluation result
        """
        try:
            # Prepare prompt for LLM evaluation
            prompt = f"""
            Please evaluate the accuracy of the video classification results compared to the ground truth.
            
            Predicted Classification:
            ```json
            {json.dumps(classification_result, indent=2)}
            ```
            
            Predicted Tags:
            ```json
            {json.dumps(tags_result, indent=2)}
            ```
            
            Ground Truth Classification:
            ```json
            {json.dumps(ground_truth_classification, indent=2)}
            ```
            
            Ground Truth Tags:
            ```json
            {json.dumps(ground_truth_tags, indent=2)}
            ```
            
            Provide an accuracy score between 0.0 and 1.0, where 1.0 means perfect match.
            Also provide separate accuracy scores for categories and tags.
            Return your evaluation in the following JSON format:
            
            ```json
            {{
                "accuracy_score": 0.85,
                "category_accuracy": 0.9,
                "tag_accuracy": 0.8,
                "explanation": "Explanation of the evaluation..."
            }}
            ```
            """
            
            # Call Bedrock LLM for evaluation
            system = "You are a video classification evaluation expert. Provide accurate and objective evaluations."
            response_text, token_usage = call_bedrock_llm(
                s3_uri=None,  # No video needed for evaluation
                prompt=prompt,
                system=system,
                model_id=self.model_id,
                region=self.region
            )
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                evaluation_result = json.loads(json_text)
            else:
                raise ValueError("No JSON object found in response")
            
            # Add token usage
            evaluation_result['token_usage'] = token_usage
            
            # Write to CSV
            with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    s3_uri,
                    evaluation_result.get('accuracy_score', 0.0),
                    evaluation_result.get('category_accuracy', 0.0),
                    evaluation_result.get('tag_accuracy', 0.0),
                    token_usage.get('input_tokens', 0),
                    token_usage.get('output_tokens', 0)
                ])
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating video {s3_uri}: {e}")
            raise
