# AWS Bedrock Video Classification System

A Java-based video classification system that leverages AWS Bedrock Runtime service to automatically categorize and tag video content stored in Amazon S3. The system processes videos in batches and generates detailed content classifications including categories and tags with confidence scores.

The system provides an end-to-end solution for video content analysis by combining AWS services with efficient batch processing capabilities. It handles video upload management, content analysis through AWS Bedrock's AI models, and structured output generation. The system is particularly useful for content management systems, media libraries, and video platforms that require automated content categorization.

Key features include:
- Automated video upload to Amazon S3 with efficient temp file management
- Integration with AWS Bedrock Runtime for AI-powered video analysis
- Batch processing with throttling protection
- Hierarchical content categorization with confidence scores
- CSV-based input/output for easy integration
- Robust error handling and logging

## Repository Structure
```
.
├── src/main/java/com/zhuermu/          # Core application code
│   ├── Converse.java                    # AWS Bedrock Runtime integration
│   ├── VideoClassification.java         # Main application entry point
│   ├── model/                           # Data models for classification
│   │   ├── Category.java               # Category hierarchy model
│   │   ├── ClassificationResult.java   # Classification output model
│   │   └── Tag.java                    # Content tag model
│   └── service/                         # Service layer
│       ├── BedrockService.java         # Bedrock service integration
│       └── S3Service.java              # S3 operations handler
├── src/main/resources/                  # Application resources
│   └── logback.xml                     # Logging configuration
├── pom.xml                             # Maven project configuration
└── convert_urls.py                      # URL to S3 path converter utility
```

## Usage Instructions
### Prerequisites
- Java Development Kit (JDK) 17 or later
- Apache Maven 3.6 or later
- AWS Account with access to:
  - Amazon S3
  - AWS Bedrock Runtime service
- AWS credentials configured with appropriate permissions
- Python 3.x (for URL conversion utility)

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd video-classification
```

2. Configure AWS credentials:
```bash
# MacOS/Linux
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# Windows
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_REGION=us-east-1
```

3. Build the project:
```bash
mvn clean package
```

### Quick Start

1. Prepare your video URLs in a CSV file (tiktok-video.csv):
```csv
URL
https://example.com/video1.mp4
https://example.com/video2.mp4
```

2. Convert URLs to S3 paths:
```bash
python convert_urls.py
```

3. Run the video classification:
```bash
java -jar target/video-classification-1.0-SNAPSHOT.jar
```

### More Detailed Examples

1. Process videos with custom batch size:
```java
VideoClassification classifier = new VideoClassification();
classifier.processVideos("classification-video.csv", 5); // Process 5 videos per batch
```

2. Upload videos to S3:
```java
S3Service s3Service = new S3Service("your-bucket", "your-folder");
String s3Key = s3Service.uploadVideo("https://example.com/video.mp4");
```

### Troubleshooting

1. Throttling Issues
- Error: "Too many tokens, please wait before trying again"
- Solution: Increase delay between batch processing
```java
Thread.sleep(30000); // Add 30-second delay between batches
```

2. S3 Access Issues
- Check AWS credentials are properly configured
- Verify IAM permissions include:
  - s3:PutObject
  - s3:ListObjects
  - s3:GetObject

3. Memory Issues
- Increase JVM heap size:
```bash
java -Xmx4g -jar target/video-classification-1.0-SNAPSHOT.jar
```

## Data Flow
The system processes videos through a pipeline that handles upload, analysis, and classification storage.

```ascii
[Video URLs] -> [URL Converter] -> [S3 Upload] -> [AWS Bedrock Analysis] -> [Classification CSV]
     |                |               |                    |                        |
     +----------------+---------------+--------------------+------------------------+
                                Data Flow Pipeline
```

Component Interactions:
1. URL Converter (convert_urls.py) transforms video URLs to S3-compatible paths
2. S3Service handles video upload and temporary file management
3. Converse class integrates with AWS Bedrock Runtime for video analysis
4. VideoClassification orchestrates the entire process and manages batch processing
5. Results are stored in CSV format with categories, tags, and timestamps