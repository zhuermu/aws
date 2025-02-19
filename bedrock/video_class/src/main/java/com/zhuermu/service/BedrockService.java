package com.zhuermu.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhuermu.model.ClassificationResult;
import lombok.extern.slf4j.Slf4j;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.ContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ConversationRole;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseResponse;
import software.amazon.awssdk.services.bedrockruntime.model.Message;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;


@Slf4j
public class BedrockService {
    private final BedrockRuntimeClient bedrockClient;
    private final String promptTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public BedrockService() throws IOException {
        String accessKey = System.getenv("AWS_ACCESS_KEY_ID");
        String secretKey = System.getenv("AWS_SECRET_ACCESS_KEY");
        if (accessKey == null || secretKey == null) {
            throw new IllegalStateException("AWS credentials not found in environment variables");
        }
        String region = System.getenv("AWS_REGION");
        if (region == null || region.isEmpty()) {
            region = Region.US_EAST_1.id();
        }
        var credentials = AwsBasicCredentials.create(accessKey, secretKey);
        this.bedrockClient = BedrockRuntimeClient.builder()
        .credentialsProvider(StaticCredentialsProvider.create(credentials))
        .region(Region.of(region))
        .build();
        // Read prompt from file
        this.promptTemplate = Files.readString(Paths.get("prompt.md"));
    }

    public ClassificationResult classifyVideo(String s3Uri) {
        var modelId = "us.amazon.nova-lite-v1:0";

        try {
            log.info("Starting video classification for: {}", s3Uri);       
            
            String bucketOwner = System.getenv("AWS_S3_BUCKET_OWNER");
            // Create video content block
            var videoContent = ContentBlock.builder()
                    .video(video -> video
                            .format("mp4")
                            .source(source -> source
                                    .s3Location(s3 -> s3
                                            .uri(s3Uri).bucketOwner(bucketOwner)
                                            )))
                    .build();

            // Create text content block
            var textContent = ContentBlock.fromText(promptTemplate);

            // Create message with both video and text content
            var message = Message.builder()
                    .content(Arrays.asList(videoContent, textContent))
                    .role(ConversationRole.USER)
                    .build();
           
            ConverseResponse response = bedrockClient.converse(request -> request
                    .modelId(modelId)
                    .messages(message)
                    .inferenceConfig(config -> config
                            .maxTokens(512)
                            .temperature(0.7F)
                            .topP(0.9F)));

            var responseText = response.output().message().content().get(0).text();
            log.info("Received response: {}", responseText);

                // Extract JSON from responseText
            int startIndex = responseText.indexOf("{");
            int endIndex = responseText.lastIndexOf("}") + 1;
            String jsonResponse = responseText.substring(startIndex, endIndex);
            log.info("Extracted JSON response: {}", jsonResponse);
            
            ClassificationResult result = objectMapper.readValue(jsonResponse, ClassificationResult.class);
            log.info("Successfully parsed classification result: {}", result);
            return result;

        } catch (Exception e) {
            System.err.printf("ERROR: Can't invoke '%s'. Reason: %s", modelId, e.getMessage());
            throw new RuntimeException(e);
        }
    }
}
