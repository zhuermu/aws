# AWS Bedrock Java Client

This project provides two ways to call the AWS Bedrock Runtime API for Claude 3.5 Haiku model using Java.

## Prerequisites

1. Java 11 or higher
2. Maven 3.6 or higher
3. AWS credentials configured (for SDK approach) or AWS Bearer Token (for HTTP approach)

## Setup

### 1. Build the project
```bash
mvn clean compile
```

### 2. AWS Authentication

#### For AWS SDK approach (BedrockClient.java):
Configure AWS credentials using one of these methods:
- AWS credentials file (`~/.aws/credentials`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM roles (if running on EC2)
- AWS CLI (`aws configure`)

#### For HTTP client approach (BedrockHttpClient.java):
Set the bearer token environment variable:
```bash
export AWS_BEARER_TOKEN_BEDROCK="your-bearer-token-here"
```

## Usage

### Approach 1: Using AWS SDK (Recommended)

```bash
mvn exec:java -Dexec.mainClass="com.example.BedrockClient"
```

### Approach 2: Using HTTP Client

```bash
mvn exec:java -Dexec.mainClass="com.example.BedrockHttpClient"
```

## Code Examples

### AWS SDK Approach
```java
BedrockClient client = new BedrockClient();
try {
    String response = client.sendMessage("Hello, how are you?");
    System.out.println("Response: " + response);
} finally {
    client.close();
}
```

### HTTP Client Approach
```java
BedrockHttpClient client = new BedrockHttpClient();
String response = client.sendMessage("Hello, how are you?");
System.out.println("Response: " + response);
```

## Required IAM Permissions

For the AWS SDK approach, ensure your AWS credentials have the following permission:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-3-5-haiku-20241022-v1:0"
        }
    ]
}
```

## Dependencies

- AWS SDK for Java v2 (Bedrock Runtime)
- Jackson for JSON processing
- SLF4J for logging

## Notes

- The AWS SDK approach is recommended as it handles authentication, retries, and other AWS-specific concerns automatically
- The HTTP client approach gives you more control but requires manual handling of authentication and error scenarios
- Both implementations target the Claude 3.5 Haiku model in the us-east-1 region
