package com.example;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * HTTP client implementation for calling Bedrock Runtime API directly
 * Note: This requires AWS_BEARER_TOKEN_BEDROCK environment variable to be set
 */
public class BedrockHttpClient {
    
    private static final String BEDROCK_URL = "https://bedrock-runtime.us-east-1.amazonaws.com/model/us.anthropic.claude-3-5-haiku-20241022-v1:0/converse";
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final String bearerToken;
    
    public BedrockHttpClient() {
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(30))
                .build();
        this.objectMapper = new ObjectMapper();
        this.bearerToken = System.getenv("AWS_BEARER_TOKEN_BEDROCK");
        
        if (bearerToken == null || bearerToken.isEmpty()) {
            throw new IllegalStateException("AWS_BEARER_TOKEN_BEDROCK environment variable is required");
        }
    }
    
    /**
     * Send a message to Claude 3.5 Haiku model via HTTP
     * @param userMessage The message to send
     * @return The model's response
     */
    public String sendMessage(String userMessage) {
        try {
            // Create request body JSON
            String requestBody = createRequestBody(userMessage);
            
            // Build HTTP request
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(BEDROCK_URL))
                    .header("Content-Type", "application/json")
                    .header("Authorization", "Bearer " + bearerToken)
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .timeout(Duration.ofSeconds(60))
                    .build();
            
            // Send request
            HttpResponse<String> response = httpClient.send(request, 
                    HttpResponse.BodyHandlers.ofString());
            
            // Check response status
            if (response.statusCode() != 200) {
                throw new RuntimeException("HTTP " + response.statusCode() + ": " + response.body());
            }
            
            // Parse response
            return parseResponse(response.body());
            
        } catch (IOException | InterruptedException e) {
            System.err.println("Error calling Bedrock API: " + e.getMessage());
            e.printStackTrace();
            return "Error: " + e.getMessage();
        }
    }
    
    /**
     * Create JSON request body
     */
    private String createRequestBody(String userMessage) {
        return String.format("{\n" +
            "    \"messages\": [\n" +
            "        {\n" +
            "            \"role\": \"user\",\n" +
            "            \"content\": [{\"text\": \"%s\"}]\n" +
            "        }\n" +
            "    ]\n" +
            "}", userMessage.replace("\"", "\\\""));
    }
    
    /**
     * Parse the JSON response to extract the text content
     */
    private String parseResponse(String responseBody) {
        try {
            JsonNode root = objectMapper.readTree(responseBody);
            JsonNode output = root.get("output");
            
            if (output != null) {
                JsonNode message = output.get("message");
                if (message != null) {
                    JsonNode content = message.get("content");
                    if (content != null && content.isArray() && content.size() > 0) {
                        JsonNode firstContent = content.get(0);
                        JsonNode text = firstContent.get("text");
                        if (text != null) {
                            return text.asText();
                        }
                    }
                }
            }
            
            return "No response text found in: " + responseBody;
            
        } catch (Exception e) {
            System.err.println("Error parsing response: " + e.getMessage());
            return "Error parsing response: " + responseBody;
        }
    }
    
    public static void main(String[] args) {
        try {
            BedrockHttpClient client = new BedrockHttpClient();
            String response = client.sendMessage("Hello");
            System.out.println("Response: " + response);
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
