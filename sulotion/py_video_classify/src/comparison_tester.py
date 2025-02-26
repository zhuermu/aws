"""
Comparison testing module.
"""
import os
import json
import csv
import logging
import time
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

from .video_classifier import VideoClassifier, TwoStepVideoClassifier
from .video_evaluator import VideoEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComparisonTester:
    """Comparison tester class."""
    
    def __init__(
        self,
        videos_csv: str,
        ground_truth_csv: str,
        output_dir: str = "comparison_results",
        region: str = "us-east-1"
    ):
        """
        Initialize the comparison tester.
        
        Args:
            videos_csv: Path to CSV file with video S3 URIs
            ground_truth_csv: Path to ground truth CSV
            output_dir: Directory to store output files
            region: AWS region
        """
        self.videos_csv = videos_csv
        self.ground_truth_csv = ground_truth_csv
        self.output_dir = output_dir
        self.region = region
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create summary CSV
        self.summary_csv = os.path.join(self.output_dir, "comparison_summary.csv")
        if not os.path.exists(self.summary_csv):
            try:
                with open(self.summary_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'Model ID', 
                        'Method',
                        'Overall Accuracy',
                        'Category Accuracy',
                        'Tag Accuracy',
                        'Average Processing Time (s)',
                        'Total Input Tokens',
                        'Total Output Tokens'
                    ])
            except Exception as e:
                logger.error(f"Error creating summary CSV {self.summary_csv}: {e}")
                raise
    
    def run_comparison(
        self,
        model_ids: List[str] = ["amazon.nova-lite-v1:0", "amazon.nova-v1:0"],
        methods: List[str] = ["one_step", "two_step"]
    ) -> Dict[str, Any]:
        """
        Run comparison tests.
        
        Args:
            model_ids: List of model IDs to test
            methods: List of methods to test
            
        Returns:
            Comparison results
        """
        try:
            # Load videos
            videos_df = pd.read_csv(self.videos_csv)
            s3_uris = videos_df['S3 URI'].tolist()
            
            results = {}
            
            for model_id in model_ids:
                for method in methods:
                    logger.info(f"Testing model {model_id} with method {method}")
                    
                    # Create output files
                    output_prefix = f"{model_id.replace('.', '_').replace(':', '_')}_{method}"
                    classification_csv = os.path.join(self.output_dir, f"{output_prefix}_classification.csv")
                    evaluation_csv = os.path.join(self.output_dir, f"{output_prefix}_evaluation.csv")
                    
                    # Create classifier
                    if method == "one_step":
                        classifier = VideoClassifier(
                            prompt_path="prompt.md",
                            model_id=model_id,
                            region=self.region,
                            output_csv=classification_csv
                        )
                    else:  # two_step
                        classifier = TwoStepVideoClassifier(
                            first_prompt_path="first_prompt.md",
                            second_prompt_path="second_prompt.md",
                            model_id=model_id,
                            region=self.region,
                            output_csv=classification_csv
                        )
                    
                    # Classify videos
                    classification_results = []
                    processing_times = []
                    total_input_tokens = 0
                    total_output_tokens = 0
                    
                    for s3_uri in s3_uris:
                        start_time = time.time()
                        result = classifier.classify_video(s3_uri)
                        end_time = time.time()
                        
                        processing_time = end_time - start_time
                        processing_times.append(processing_time)
                        
                        total_input_tokens += result['token_usage'].get('input_tokens', 0)
                        total_output_tokens += result['token_usage'].get('output_tokens', 0)
                        
                        classification_results.append(result)
                        
                        logger.info(f"Classified {s3_uri} in {processing_time:.2f} seconds")
                    
                    # Create evaluator
                    evaluator = VideoEvaluator(
                        classification_csv=classification_csv,
                        ground_truth_csv=self.ground_truth_csv,
                        model_id=model_id,
                        region=self.region,
                        output_csv=evaluation_csv
                    )
                    
                    # Evaluate results
                    evaluation_result = evaluator.evaluate_all()
                    
                    # Calculate average processing time
                    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
                    
                    # Store results
                    results[f"{model_id}_{method}"] = {
                        'model_id': model_id,
                        'method': method,
                        'overall_accuracy': evaluation_result['overall_accuracy'],
                        'category_accuracy': evaluation_result['category_accuracy'],
                        'tag_accuracy': evaluation_result['tag_accuracy'],
                        'avg_processing_time': avg_processing_time,
                        'total_input_tokens': total_input_tokens,
                        'total_output_tokens': total_output_tokens,
                        'classification_results': classification_results,
                        'evaluation_result': evaluation_result
                    }
                    
                    # Write to summary CSV
                    with open(self.summary_csv, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            model_id,
                            method,
                            evaluation_result['overall_accuracy'],
                            evaluation_result['category_accuracy'],
                            evaluation_result['tag_accuracy'],
                            avg_processing_time,
                            total_input_tokens,
                            total_output_tokens
                        ])
            
            return results
            
        except Exception as e:
            logger.error(f"Error running comparison tests: {e}")
            raise
    
    def generate_report(self) -> str:
        """
        Generate a comparison report.
        
        Returns:
            Report text
        """
        try:
            # Load summary CSV
            summary_df = pd.read_csv(self.summary_csv)
            
            # Sort by overall accuracy
            summary_df = summary_df.sort_values('Overall Accuracy', ascending=False)
            
            # Generate report
            report = "# Video Classification Comparison Report\n\n"
            
            report += "## Summary\n\n"
            report += "| Model ID | Method | Overall Accuracy | Category Accuracy | Tag Accuracy | Avg Processing Time (s) | Total Input Tokens | Total Output Tokens |\n"
            report += "|----------|--------|-----------------|-------------------|-------------|------------------------|-------------------|-------------------|\n"
            
            for _, row in summary_df.iterrows():
                report += f"| {row['Model ID']} | {row['Method']} | {row['Overall Accuracy']:.4f} | {row['Category Accuracy']:.4f} | {row['Tag Accuracy']:.4f} | {row['Average Processing Time (s)']:.2f} | {row['Total Input Tokens']} | {row['Total Output Tokens']} |\n"
            
            report += "\n## Analysis\n\n"
            
            # Find best model and method
            best_row = summary_df.iloc[0]
            report += f"The best performing combination is **{best_row['Model ID']}** with the **{best_row['Method']}** method, achieving an overall accuracy of {best_row['Overall Accuracy']:.4f}.\n\n"
            
            # Compare methods
            one_step_df = summary_df[summary_df['Method'] == 'one_step']
            two_step_df = summary_df[summary_df['Method'] == 'two_step']
            
            if not one_step_df.empty and not two_step_df.empty:
                one_step_avg_accuracy = one_step_df['Overall Accuracy'].mean()
                two_step_avg_accuracy = two_step_df['Overall Accuracy'].mean()
                
                one_step_avg_time = one_step_df['Average Processing Time (s)'].mean()
                two_step_avg_time = two_step_df['Average Processing Time (s)'].mean()
                
                report += "### Method Comparison\n\n"
                report += f"- One-step method average accuracy: {one_step_avg_accuracy:.4f}\n"
                report += f"- Two-step method average accuracy: {two_step_avg_accuracy:.4f}\n"
                report += f"- One-step method average processing time: {one_step_avg_time:.2f} seconds\n"
                report += f"- Two-step method average processing time: {two_step_avg_time:.2f} seconds\n\n"
                
                if two_step_avg_accuracy > one_step_avg_accuracy:
                    report += "The two-step method generally achieves higher accuracy, but at the cost of longer processing times.\n\n"
                else:
                    report += "The one-step method achieves comparable or better accuracy with faster processing times.\n\n"
            
            # Compare models
            report += "### Model Comparison\n\n"
            
            for model_id in summary_df['Model ID'].unique():
                model_df = summary_df[summary_df['Model ID'] == model_id]
                avg_accuracy = model_df['Overall Accuracy'].mean()
                avg_time = model_df['Average Processing Time (s)'].mean()
                
                report += f"- {model_id} average accuracy: {avg_accuracy:.4f}\n"
                report += f"- {model_id} average processing time: {avg_time:.2f} seconds\n\n"
            
            # Write report to file
            report_path = os.path.join(self.output_dir, "comparison_report.md")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
