import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Bedrock AgentCore client
region = os.getenv('AWS_REGION', 'us-east-1')
agent_core_client = boto3.client('bedrock-agentcore', region_name=region)

input_text = "Hello, how can you assist me today?"

# The payload should be a JSON object with a "prompt" key, not just a string
payload = {
    "prompt": input_text
}

try:
    agent_runtime_arn = os.getenv('AGENT_RUNTIME_ARN')
    if not agent_runtime_arn:
        raise ValueError("AGENT_RUNTIME_ARN environment variable is not set. Please check your .env file.")
    
    response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        qualifier="DEFAULT",
        payload=json.dumps(payload)  # Convert to JSON string
    )
    
    # Print the response
    print("Response:", response)
    
    # If there's a response body, decode it
    if 'payload' in response:
        response_payload = response['payload']
        if isinstance(response_payload, bytes):
            response_text = response_payload.decode('utf-8')
        else:
            response_text = response_payload
        print("Agent Response:", response_text)
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure your agent is deployed and running.")
    print("Also ensure your .env file is properly configured with AGENT_RUNTIME_ARN.")