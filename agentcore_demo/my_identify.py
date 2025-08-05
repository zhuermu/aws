import os
from dotenv import load_dotenv
from bedrock_agentcore.services.identity import IdentityClient

# Load environment variables from .env file
load_dotenv()

# Get region from environment variable
region = os.getenv('AWS_REGION', 'us-east-1')
identity_client = IdentityClient(region)
workload_identity = identity_client.create_workload_identity(name="my-agent")

# Get credentials from environment variables
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')

# Only create providers if credentials are available
if google_client_id and google_client_secret:
    google_provider = identity_client.create_oauth2_credential_provider(
        {
            "name": "google-workspace",
            "credentialProviderVendor": "GoogleOauth2",
            "oauth2ProviderConfigInput": {
                "googleOauth2ProviderConfig": {
                    "clientId": google_client_id,
                    "clientSecret": google_client_secret,
                }
            },
        }
    )
else:
    print("Google OAuth2 credentials not found in environment variables")

if perplexity_api_key:
    perplexity_provider = identity_client.create_api_key_credential_provider(
        {
            "name": "perplexity-ai",
            "apiKey": perplexity_api_key
        }
    )
else:
    print("Perplexity API key not found in environment variables")
