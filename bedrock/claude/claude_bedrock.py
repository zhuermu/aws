import boto3

client = boto3.client(
    'bedrock-runtime',
    region_name='us-west-2',
    # aws_access_key_id='YOUR_ACCESS_KEY',
    # aws_secret_access_key='YOUR_SECRET_KEY'
)

response = client.converse(
    modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    messages=[
        {
            'role': 'user',
            'content': [{'text': 'Hello, how are you?'}]
        }
    ]
)

print(response['output']['message']['content'][0]['text'])
