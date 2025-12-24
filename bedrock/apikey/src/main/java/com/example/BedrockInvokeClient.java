package com.example;

import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.InvokeModelRequest;
import software.amazon.awssdk.services.bedrockruntime.model.InvokeModelResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.ArrayNode;

public class BedrockInvokeClient {
    
    private static final String MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0";
    private static final Region REGION = Region.US_EAST_1;
    
    public static void main(String[] args) {
        try {
            // Set the API key as environment variable (equivalent to Python's os.environ)
            // You can set this before running: export AWS_BEARER_TOKEN_BEDROCK="your-api-key"
            // Or set it programmatically (not recommended for production):
            // System.setProperty("AWS_BEARER_TOKEN_BEDROCK", "your-api-key");
            
            // Create credentials provider that will use the bearer token
            AwsCredentialsProvider credentialsProvider = DefaultCredentialsProvider.create();
            
            // Create Amazon Bedrock client
            BedrockRuntimeClient client = BedrockRuntimeClient.builder()
                    .region(REGION)
                    .credentialsProvider(credentialsProvider)
                    .build();
            
            // Create request payload using Jackson
            ObjectMapper mapper = new ObjectMapper();
            ObjectNode requestBody = mapper.createObjectNode();
            requestBody.put("anthropic_version", "bedrock-2023-05-31");
            requestBody.put("max_tokens", 1000);
            
            // Create messages array
            ArrayNode messagesArray = mapper.createArrayNode();
            ObjectNode message = mapper.createObjectNode();
            message.put("role", "user");
            
            // Create content array
            ArrayNode contentArray = mapper.createArrayNode();
            ObjectNode textContent = mapper.createObjectNode();
            textContent.put("type", "text");
            textContent.put("text", "Hello");
            contentArray.add(textContent);
            
            message.set("content", contentArray);
            messagesArray.add(message);
            requestBody.set("messages", messagesArray);
            
            String jsonPayload = mapper.writeValueAsString(requestBody);
            System.out.println("Request payload: " + jsonPayload);
            
            // Create and send the invoke model request
            InvokeModelRequest request = InvokeModelRequest.builder()
                    .modelId(MODEL_ID)
                    .body(SdkBytes.fromUtf8String(jsonPayload))
                    .build();
            
            System.out.println("Sending invoke model request to Bedrock...");
            InvokeModelResponse response = client.invokeModel(request);
            
            // Parse and display response
            String responseBody = response.body().asUtf8String();
            System.out.println("Response from Bedrock:");
            System.out.println(responseBody);
            
        } catch (Exception e) {
            System.err.println("Error occurred: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
