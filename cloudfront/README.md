# CloudFront Token Validation Function with KVS

This CloudFront function implements request interception using tokens stored in CloudFront's KeyValueStore (KVS).

## Functionality

The function:
1. Checks if `tmpToken` exists in the request URL
2. If token exists, validates it by checking KeyValueStore
3. Returns 403 Forbidden if token is not found in KVS
4. Allows request to proceed if token is valid or not present

## Prerequisites

1. Create a CloudFront KeyValueStore:
   ```bash
   aws cloudfront create-key-value-store --name TokenStore
   ```

2. Associate the KeyValueStore with your CloudFront Function:
   ```bash
   aws cloudfront associate-key-value-store --key-value-store-id <KVS_ID> --function-arn <FUNCTION_ARN>
   ```

## Managing Tokens

Add tokens to KeyValueStore:
```bash
# Add a token
aws cloudfront put-key-value-entry \
    --key-value-store-id <KVS_ID> \
    --key "your-token-here" \
    --value "1"

# Remove a token
aws cloudfront delete-key-value-entry \
    --key-value-store-id <KVS_ID> \
    --key "your-token-here"
```

## Deployment Instructions

1. Go to CloudFront console in AWS
2. Navigate to "Functions" section
3. Click "Create function"
4. Enter a name for your function (e.g., "validate-token-kvs")
5. Copy the code from `validate-token.js` into the editor
6. Click "Save"
7. Test the function using the testing tool in the console

## Associating with CloudFront Distribution

1. Go to your CloudFront distribution
2. Click on "Behaviors"
3. Select the behavior you want to add the function to
4. Under "Function associations", add the function:
   - Event type: Viewer request
   - Function: Select your created function
5. Save changes

## Testing

You can test the function with these example URLs:
- Valid token (must exist in KVS): `https://your-distribution.cloudfront.net/path?tmpToken=your-valid-token`
- Invalid token: `https://your-distribution.cloudfront.net/path?tmpToken=invalid-token`
- No token: `https://your-distribution.cloudfront.net/path`

## Notes

- The KeyValueStore has a size limit per entry and total store size
- Tokens in KVS can be managed through AWS CLI or AWS Console
- Consider implementing token expiration by storing expiration timestamps in the token value
