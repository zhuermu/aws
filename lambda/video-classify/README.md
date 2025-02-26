# Video Classification Lambda Function

This AWS Lambda function processes videos from an S3 bucket using Amazon Bedrock's multimodal capabilities to classify video content according to a predefined category system.

## Overview

The `video-classify-from-sqs` Lambda function:

1. Receives messages from an SQS queue named `video-event-from-s3`
2. Extracts S3 URI from the message
3. Uses Amazon Bedrock's Nova model to analyze and classify the video content
4. Deletes the message from the queue after successful processing

## Prerequisites

- Java 17
- Maven
- AWS Account with access to:
  - AWS Lambda
  - Amazon SQS
  - Amazon S3
  - Amazon Bedrock (with access to Nova model)
- An SQS queue named `video-event-from-s3` that receives notifications when videos are uploaded to S3

## Project Structure

```
video-classify/
├── pom.xml                                  # Maven project configuration
├── prompt.md                                # Classification prompt for Bedrock
├── README.md                                # This file
└── src/
    └── main/
        └── java/
            └── com/
                └── zhuermu/
                    └── VideoClassifyFromSqsHandler.java  # Lambda handler
```

## Building the Project

To build the project, run:

```bash
mvn clean package
```

This will create a JAR file in the `target` directory.

## Deploying to AWS Lambda

1. Create a new Lambda function in the AWS Console:
   - Name: `video-classify-from-sqs`
   - Runtime: Java 17
   - Handler: `com.zhuermu.VideoClassifyFromSqsHandler::handleRequest`
   - Memory: 1024 MB (or higher depending on video size)
   - Timeout: 5 minutes

2. Upload the JAR file from the `target` directory.

3. Configure the Lambda function with the following environment variables:
   - `AWS_REGION`: The AWS region (e.g., `us-east-1`)

4. Set up the following IAM permissions for the Lambda function:
   - SQS: `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueUrl`
   - S3: `s3:GetObject`
   - Bedrock: `bedrock:InvokeModel`

5. Configure the SQS queue as a trigger for the Lambda function.

6. Upload the `prompt.md` file to the Lambda function's root directory.

## Message Format

The Lambda function expects SQS messages to contain an S3 URI in the message body. The message can be in JSON format with an `s3Uri` field, or the S3 URI can be included directly in the message body.

Example JSON message:

```json
{
  "s3Uri": "s3://your-bucket/path/to/video.mp4",
  "metadata": {
    "fileName": "example-video.mp4",
    "uploadTime": "2025-02-25T01:30:00Z"
  }
}
```

## Output

The Lambda function processes the video and returns a JSON response with category and tag information according to the classification system defined in `prompt.md`.

Example output:

```json
{
  "catetorys": [
    {
      "catetory1": "Entertainment",
      "catetory2": "Movies & TV Shows",
      "catetory3": ["Reviews & Recommendations", "New Releases & Trailers"],
      "weight": {
        "Entertainment": 85,
        "Movies & TV Shows": 80,
        "Reviews & Recommendations": 75,
        "New Releases & Trailers": 70
      }
    }
  ],
  "tags": [
    {
      "tag": "Movie Trailer",
      "scores": 95
    },
    {
      "tag": "Action",
      "scores": 85
    },
    {
      "tag": "Sci-Fi",
      "scores": 80
    }
  ]
}
```

## Monitoring and Logging

The Lambda function uses SLF4J for logging. All logs are sent to CloudWatch Logs, where you can monitor the function's execution and troubleshoot any issues.

## Error Handling

If an error occurs during processing, the Lambda function will log the error but will not delete the message from the queue. This allows the message to be retried according to the queue's retry policy.
