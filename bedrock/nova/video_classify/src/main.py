"""
Main module for video classification.
"""
import os
import sys
import argparse
import logging
import json
import pandas as pd
import csv
from typing import Dict, Any, List, Tuple, Optional

from .common import call_bedrock_llm, video_to_text, calibrate_classification, parse_json_result
from .video_classifier import VideoClassifier, TwoStepVideoClassifier
from .video_evaluator import VideoEvaluator
from .comparison_tester import ComparisonTester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def classify_video(args):
    """
    Classify a video.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Generate output CSV filename if not provided
        output_csv = args.output_csv
        if output_csv is None:
            # Extract model name from model_id (e.g., 'nova-lite' from 'amazon.nova-lite-v1:0')
            model_name = args.model_id.split('.')[1].split('-v')[0] if '.' in args.model_id and '-v' in args.model_id else args.model_id
            output_csv = f"data/classification_results_{args.method}_{model_name}.csv"
            logger.info(f"Generated output CSV filename: {output_csv}")
        
        # Create classifier
        if args.method == "two_step":
            classifier = TwoStepVideoClassifier(
                first_prompt_path=args.first_prompt,
                second_prompt_path=args.second_prompt,
                model_id=args.model_id,
                region=args.region,
                output_csv=output_csv,
                categories_path=args.categories_path
            )
        else:  # one_step
            classifier = VideoClassifier(
                prompt_path=args.prompt,
                model_id=args.model_id,
                region=args.region,
                output_csv=output_csv,
                categories_path=args.categories_path
            )
        
        # Classify video
        result = classifier.classify_video(args.s3_uri)
        
        # Print result
        print(json.dumps(result, indent=2))
        
        logger.info(f"Classification result written to {output_csv}")
        
    except Exception as e:
        logger.error(f"Error classifying video: {e}")
        sys.exit(1)

def evaluate_videos(args):
    """
    Evaluate video classification results.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Create evaluator
        evaluator = VideoEvaluator(
            classification_csv=args.classification_csv,
            ground_truth_csv=args.ground_truth_csv,
            model_id=args.model_id,
            region=args.region,
            output_csv=args.output_csv
        )
        
        # Evaluate results
        result = evaluator.evaluate_all()
        
        # Print result
        print(json.dumps(result, indent=2))
        
        logger.info(f"Evaluation result written to {args.output_csv}")
        
    except Exception as e:
        logger.error(f"Error evaluating videos: {e}")
        sys.exit(1)

def run_comparison(args):
    """
    Run comparison tests.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Create comparison tester
        tester = ComparisonTester(
            videos_csv=args.videos_csv,
            ground_truth_csv=args.ground_truth_csv,
            output_dir=args.output_dir,
            region=args.region
        )
        
        # Parse model IDs and methods
        model_ids = args.model_ids.split(',')
        methods = args.methods.split(',')
        
        # Run comparison
        results = tester.run_comparison(
            model_ids=model_ids,
            methods=methods
        )
        
        # Generate report
        report = tester.generate_report()
        
        # Print report path
        print(f"Comparison report written to {os.path.join(args.output_dir, 'comparison_report.md')}")
        
    except Exception as e:
        logger.error(f"Error running comparison tests: {e}")
        sys.exit(1)

def transcribe_video(args):
    """
    Transcribe a video.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Transcribe video
        transcript = video_to_text(
            s3_uri=args.s3_uri,
            max_duration=args.max_duration,
            region=args.region
        )
        
        # Print transcript
        print(transcript)
        
        # Write to file if specified
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            logger.info(f"Transcript written to {args.output_file}")
        
    except Exception as e:
        logger.error(f"Error transcribing video: {e}")
        sys.exit(1)

def process_videos(args):
    """
    Process videos from CSV file.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Generate output CSV filename if not provided
        output_csv = args.output_csv
        if output_csv is None:
            # Extract model name from model_id (e.g., 'nova-lite' from 'amazon.nova-lite-v1:0')
            model_name = args.model_id.split('.')[1].split('-v')[0] if '.' in args.model_id and '-v' in args.model_id else args.model_id
            output_csv = f"data/classification_results_{args.method}_{model_name}.csv"
            logger.info(f"Generated output CSV filename: {output_csv}")
        
        # Load input data with proper quoting to handle JSON in fields
        try:
            logger.info(f"Attempting to load CSV with proper quoting: {args.input_csv}")
            df = pd.read_csv(args.input_csv, quotechar='"', escapechar='\\')
            logger.info(f"Successfully loaded {len(df)} videos from {args.input_csv}")
        except Exception as e:
            logger.warning(f"Error loading CSV with standard method: {e}")
            logger.info("Falling back to extracting S3 URIs directly from the file...")
            
            # Extract S3 URIs directly from the file
            s3_uris = []
            with open(args.input_csv, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line in lines:
                    if 's3://' in line:
                        start = line.find('s3://')
                        end = line.find('.mp4', start)
                        if end != -1:
                            s3_uri = line[start:end+4]
                            s3_uris.append(s3_uri)
            
            # Create a DataFrame with just the S3 URIs
            df = pd.DataFrame({'S3 URI': s3_uris})
            logger.info(f"Extracted {len(df)} S3 URIs from {args.input_csv}")
        
        # Create output CSV with headers if it doesn't exist
        if not os.path.exists(output_csv):
            os.makedirs(os.path.dirname(output_csv), exist_ok=True)
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
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
        
        # Initialize classifier based on method
        if args.method == "two_step":
            classifier = TwoStepVideoClassifier(
                first_prompt_path=args.first_prompt,
                second_prompt_path=args.second_prompt,
                model_id=args.model_id,
                region=args.region,
                output_csv=output_csv,
                categories_path=args.categories_path
            )
        else:  # one_step
            classifier = VideoClassifier(
                prompt_path=args.prompt,
                model_id=args.model_id,
                region=args.region,
                output_csv=output_csv,
                categories_path=args.categories_path
            )
        
        # Process each video
        results = []
        for _, row in df.iterrows():
            # Make sure we're getting the S3 URI from the correct column
            if 'S3 URI' in row:
                s3_uri = row['S3 URI']
            else:
                # Try to find a column that contains an S3 URI
                for col, value in row.items():
                    if isinstance(value, str) and value.startswith('s3://'):
                        s3_uri = value
                        break
                else:
                    logger.warning(f"Could not find S3 URI in row: {row}")
                    continue
            
            # Skip if already processed
            if os.path.exists(output_csv):
                try:
                    output_df = pd.read_csv(output_csv, quotechar='"', escapechar='\\')
                    if s3_uri in output_df['S3 URI'].values:
                        logger.info(f"Skipping already processed video: {s3_uri}")
                        continue
                except Exception as e:
                    logger.warning(f"Error checking if video is already processed: {e}")
                    # Continue with processing as a fallback
            
            logger.info(f"Processing video: {s3_uri}")
            
            # Get original category and tags if available
            original_category = row.get('catetory', '')
            original_tags = row.get('tags', '')
            original_result = row.get('result', '')
            
            # Verify S3 URI format
            if not s3_uri.startswith('s3://'):
                logger.warning(f"Skipping invalid S3 URI: {s3_uri}")
                continue
                
            # Classify video
            try:
                logger.info(f"Processing video with S3 URI: {s3_uri}")
                result = classifier.classify_video(s3_uri)
                
                # Extract classification results for results list
                categories = result['calibrated_classification']['catetorys']
                tags = result['calibrated_classification']['tags']
                
                # Get token usage
                input_tokens = result['token_usage']['input_tokens']
                output_tokens = result['token_usage']['output_tokens']
                
                # Note: We don't write to CSV here because the VideoClassifier.classify_video method 
                # already writes to the CSV file via its _write_to_csv method
                
                logger.info(f"Successfully processed video: {s3_uri}")
                
                # Add to results
                results.append({
                    's3_uri': s3_uri,
                    'original_category': original_category,
                    'original_tags': original_tags,
                    'original_result': original_result,
                    'new_category': categories,
                    'new_tags': tags,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens
                })
                
            except Exception as e:
                logger.error(f"Error processing video {s3_uri}: {e}")
                continue
        
        logger.info(f"Processed {len(results)} videos")
        logger.info(f"Results written to {output_csv}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing videos: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Video Classification Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Classify command
    classify_parser = subparsers.add_parser('classify', help='Classify a video')
    classify_parser.add_argument('s3_uri', help='S3 URI of the video')
    classify_parser.add_argument('--method', choices=['one_step', 'two_step'], default='one_step', help='Classification method')
    classify_parser.add_argument('--prompt', default='prompt/one_step_prompt.md', help='Path to prompt file (for one-step method)')
    classify_parser.add_argument('--first-prompt', default='prompt/two_step1_prompt.md', help='Path to first prompt file (for two-step method)')
    classify_parser.add_argument('--second-prompt', default='prompt/two_stop2_prompt.md', help='Path to second prompt file (for two-step method)')
    classify_parser.add_argument('--model-id', default='amazon.nova-lite-v1:0', help='Model ID')
    classify_parser.add_argument('--region', default='us-east-1', help='AWS region')
    classify_parser.add_argument('--output-csv', help='Path to output CSV file (if not provided, will be generated based on method and model-id)')
    classify_parser.add_argument('--categories-path', default='category.json', help='Path to categories JSON file')
    
    # Evaluate command
    evaluate_parser = subparsers.add_parser('evaluate', help='Evaluate video classification results')
    evaluate_parser.add_argument('classification_csv', help='Path to classification results CSV')
    evaluate_parser.add_argument('ground_truth_csv', help='Path to ground truth CSV')
    evaluate_parser.add_argument('--model-id', default='amazon.nova-lite-v1:0', help='Model ID')
    evaluate_parser.add_argument('--region', default='us-east-1', help='AWS region')
    evaluate_parser.add_argument('--output-csv', default='data/evaluation_results.csv', help='Path to output CSV file')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Run comparison tests')
    compare_parser.add_argument('videos_csv', help='Path to CSV file with video S3 URIs')
    compare_parser.add_argument('ground_truth_csv', help='Path to ground truth CSV')
    compare_parser.add_argument('--model-ids', default='amazon.nova-lite-v1:0,amazon.nova-v1:0', help='Comma-separated list of model IDs')
    compare_parser.add_argument('--methods', default='one_step,two_step', help='Comma-separated list of methods')
    compare_parser.add_argument('--region', default='us-east-1', help='AWS region')
    compare_parser.add_argument('--output-dir', default='data/comparison_results', help='Directory to store output files')
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcribe a video')
    transcribe_parser.add_argument('s3_uri', help='S3 URI of the video')
    transcribe_parser.add_argument('--max-duration', type=int, default=30, help='Maximum duration in seconds')
    transcribe_parser.add_argument('--region', default='us-east-1', help='AWS region')
    transcribe_parser.add_argument('--output-file', help='Path to output file')
    
    # Process videos command
    process_parser = subparsers.add_parser('process', help='Process videos from CSV file')
    process_parser.add_argument('--input-csv', default='data/classification_data.csv', help='Path to input CSV file')
    process_parser.add_argument('--output-csv', help='Path to output CSV file (if not provided, will be generated based on method and model-id)')
    process_parser.add_argument('--method', choices=['one_step', 'two_step'], default='one_step', help='Classification method')
    process_parser.add_argument('--model-id', default='amazon.nova-lite-v1:0', help='Model ID')
    process_parser.add_argument('--region', default='us-east-1', help='AWS region')
    process_parser.add_argument('--categories-path', default='category.json', help='Path to categories JSON file')
    process_parser.add_argument('--prompt', default='prompt/one_step_prompt.md', help='Path to prompt file (for one-step method)')
    process_parser.add_argument('--first-prompt', default='prompt/two_step1_prompt.md', help='Path to first prompt file (for two-step method)')
    process_parser.add_argument('--second-prompt', default='prompt/two_stop2_prompt.md', help='Path to second prompt file (for two-step method)')
    
    args = parser.parse_args()
    
    if args.command == 'classify':
        classify_video(args)
    elif args.command == 'evaluate':
        evaluate_videos(args)
    elif args.command == 'compare':
        run_comparison(args)
    elif args.command == 'transcribe':
        transcribe_video(args)
    elif args.command == 'process':
        process_videos(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
