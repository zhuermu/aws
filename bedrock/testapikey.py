import os
import boto3
                        
# Read AWS_BEARER_TOKEN_BEDROCK from environment variables
bearer_token = os.environ.get('AWS_BEARER_TOKEN_BEDROCK')
if not bearer_token:
    raise ValueError("AWS_BEARER_TOKEN_BEDROCK environment variable is not set")

# Set the bearer token for Bedrock
os.environ['AWS_BEARER_TOKEN_BEDROCK'] = bearer_token

# Create an Amazon Bedrock client
client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1" # If you've configured a default region, you can omit this line
)

# Define the model and message
model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
messages = [{"role": "user", "content": [{"text": "Hello"}]}]

response = client.converse(
    modelId=model_id,
    messages=messages,
)
print(response)