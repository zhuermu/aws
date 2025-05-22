#!/usr/bin/env python3
"""
Script to reorder classification results files based on the S3 URI order in classification_data.csv
"""

import csv
import os
import glob
import sys

def load_s3_uri_order(input_file):
    """Load the S3 URI order from the input file"""
    s3_uris = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            if row and len(row) > 0:
                s3_uris.append(row[0])  # First column is S3 URI
    return s3_uris

def reorder_results_file(results_file, s3_uri_order):
    """Reorder a results file based on the S3 URI order"""
    # Read the results file
    with open(results_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows_dict = {}
        for row in reader:
            if row and len(row) > 0:
                rows_dict[row[0]] = row  # Use S3 URI as key

    # Create a new ordered list of rows
    ordered_rows = []
    for uri in s3_uri_order:
        if uri in rows_dict:
            ordered_rows.append(rows_dict[uri])
        else:
            print(f"Warning: S3 URI {uri} not found in {results_file}")

    # Write the reordered data back to the file
    output_file = results_file.replace('.csv', '_reordered.csv')
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(ordered_rows)
    
    print(f"Reordered file saved as {output_file}")
    return output_file

def main():
    # Check if input file is provided
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = 'data/classification_data.csv'
    
    # Check if results files are provided
    if len(sys.argv) > 2:
        results_files = sys.argv[2:]
    else:
        # Find all classification_results_*.csv files
        results_files = glob.glob('data/classification_results_one_step_nova-pro.csv')
        # Exclude any *_reordered.csv files
        results_files = [f for f in results_files if '_reordered.csv' not in f]
    
    print(f"Using input file: {input_file}")
    print(f"Found {len(results_files)} results files to reorder")
    
    # Load the S3 URI order
    s3_uri_order = load_s3_uri_order(input_file)
    print(f"Loaded {len(s3_uri_order)} S3 URIs from input file")
    
    # Reorder each results file
    for results_file in results_files:
        print(f"Reordering {results_file}...")
        reorder_results_file(results_file, s3_uri_order)

if __name__ == "__main__":
    main()
