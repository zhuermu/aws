package com.example;

import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseRequest;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseResponse;
import software.amazon.awssdk.services.bedrockruntime.model.Message;
import software.amazon.awssdk.services.bedrockruntime.model.ContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ConversationRole;

import java.util.List;

public class BedrockConverseClient {
    
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
            
            // Define the message
            ContentBlock contentBlock = ContentBlock.builder()
                    .text("Hello")
                    .build();
            
            Message message = Message.builder()
                    .role(ConversationRole.USER)
                    .content(contentBlock)
                    .build();
            
            List<Message> messages = List.of(message);
            
            // Create and send the converse request
            ConverseRequest request = ConverseRequest.builder()
                    .modelId(MODEL_ID)
                    .messages(messages)
                    .build();
            
            System.out.println("Sending converse request to Bedrock...");
            ConverseResponse response = client.converse(request);
            
            // Display the response
            System.out.println("Response from Bedrock:");
            response.output().message().content().forEach(content -> {
                if (content.text() != null) {
                    System.out.println(content.text());
                }
            });
            
        } catch (Exception e) {
            System.err.println("Error occurred: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
