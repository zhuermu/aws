import csv

def convert_url_to_s3(url):
    # Extract everything last "/" suffix name as video path, https://s3-video.x.me/tk/video/2025-01-09/22/cb4198e065f64149b7ccdf7f9b78f1b9.mp4, 
    # the video path is cb4198e065f64149b7ccdf7f9b78f1b9.mp4
    path_parts = url.split("/")
    
    video_path = path_parts[-1]
    # Create S3 path preserving the date structure
    return f"s3://bedrock-video-generation-us-east-1-pi8hu9/video-class/{video_path}"



def process_csv():
    # Read the input file
    rows = []
    with open('tiktok-video.csv', 'r') as file:
        reader = csv.reader(file)
        # Skip header
        next(reader)
        # Process each row
        for row in reader:
            if row:  # Skip empty rows
                url = row[0]
                s3_path = convert_url_to_s3(url)
                rows.append([url, s3_path, "", ""])

    # Write to classification-results.csv
    with open('classification-results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "S3", "OutPut", "DateTime"])
        writer.writerows(rows)

if __name__ == "__main__":
    process_csv()
