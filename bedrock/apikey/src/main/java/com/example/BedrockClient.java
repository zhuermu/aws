package com.example;

import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseRequest;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseResponse;
import software.amazon.awssdk.services.bedrockruntime.model.ContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.Message;
import software.amazon.awssdk.services.bedrockruntime.model.ConversationRole;

import java.util.List;

/**
 * AWS Bedrock Runtime client for calling Claude 3.5 Haiku model
 */
public class BedrockClient {
    
    private static final String MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0";
    private static final Region REGION = Region.US_EAST_1;
    
    private final BedrockRuntimeClient client;
    
    public BedrockClient() {
        this.client = BedrockRuntimeClient.builder()
                .region(REGION)
                .credentialsProvider(DefaultCredentialsProvider.create())
                .build();
    }
    
    /**
     * Send a message to Claude 3.5 Haiku model
     * @param userMessage The message to send
     * @return The model's response
     */
    public String sendMessage(String userMessage) {
        try {
            // Create content block with text
            ContentBlock contentBlock = ContentBlock.builder()
                    .text(userMessage)
                    .build();
            
            // Create message
            Message message = Message.builder()
                    .role(ConversationRole.USER)
                    .content(contentBlock)
                    .build();
            
            // Create converse request
            ConverseRequest request = ConverseRequest.builder()
                    .modelId(MODEL_ID)
                    .messages(message)
                    .build();
            
            // Send request
            ConverseResponse response = client.converse(request);
            
            // Extract response text
            if (response.output() != null && 
                response.output().message() != null && 
                !response.output().message().content().isEmpty()) {
                
                ContentBlock responseContent = response.output().message().content().get(0);
                return responseContent.text();
            }
            
            return "No response received";
            
        } catch (Exception e) {
            System.err.println("Error calling Bedrock: " + e.getMessage());
            e.printStackTrace();
            return "Error: " + e.getMessage();
        }
    }
    
    /**
     * Close the client
     */
    public void close() {
        if (client != null) {
            client.close();
        }
    }
    
    public static void main(String[] args) {
        BedrockClient bedrockClient = new BedrockClient();
        
        try {
            // Send a test message
            String response = bedrockClient.sendMessage("Hello");
            System.out.println("Response: " + response);
            
        } finally {
            bedrockClient.close();
        }
    }
}
