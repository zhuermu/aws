package com.zhuermu;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.SQSEvent;
import com.amazonaws.services.lambda.runtime.events.SQSEvent.SQSMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.exception.SdkClientException;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.ContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.Message;
import software.amazon.awssdk.services.bedrockruntime.model.ConversationRole;
import software.amazon.awssdk.services.bedrockruntime.model.SystemContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseResponse;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.DeleteMessageRequest;
import software.amazon.awssdk.services.sqs.model.GetQueueUrlRequest;
import software.amazon.awssdk.services.sqs.model.GetQueueUrlResponse;

import java.io.File;
import java.nio.file.Files;
import java.time.Duration;
import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class VideoClassifyFromSqsHandler implements RequestHandler<SQSEvent, Void> {
    private static final Logger logger = LoggerFactory.getLogger(VideoClassifyFromSqsHandler.class);
    private static final String SQS_QUEUE_NAME = "video-event-from-s3";
    private static final Region REGION = Region.US_EAST_1;
    
    private final SqsClient sqsClient;
    private final BedrockRuntimeClient bedrockClient;
    private final String queueUrl;
    
    public VideoClassifyFromSqsHandler() {
        // Initialize SQS client
        this.sqsClient = SqsClient.builder()
                .region(REGION)
                .credentialsProvider(DefaultCredentialsProvider.create())
                .build();
        
        // Get queue URL
        GetQueueUrlResponse queueUrlResponse = sqsClient.getQueueUrl(
                GetQueueUrlRequest.builder().queueName(SQS_QUEUE_NAME).build());
        this.queueUrl = queueUrlResponse.queueUrl();
        
        // Initialize Bedrock client with extended timeout
        this.bedrockClient = BedrockRuntimeClient.builder()
                .region(REGION)
                .credentialsProvider(DefaultCredentialsProvider.create())
                .httpClient(ApacheHttpClient.builder()
                        .socketTimeout(Duration.ofMinutes(5))
                        .connectionTimeout(Duration.ofSeconds(30))
                        .build())
                .build();
    }
    
    @Override
    public Void handleRequest(SQSEvent sqsEvent, Context context) {
        logger.info("Received SQS event with {} records", sqsEvent.getRecords().size());
        
        for (SQSMessage message : sqsEvent.getRecords()) {
            try {
                // Process the message
                processMessage(message);
                
                // Delete the message from the queue
                deleteMessage(message);
                
                logger.info("Successfully processed and deleted message {}", message.getMessageId());
            } catch (Exception e) {
                logger.error("Error processing message {}: {}", message.getMessageId(), e.getMessage(), e);
                // Don't delete the message so it can be retried
            }
        }
        
        return null;
    }
    
    public void processMessage(SQSMessage message) throws Exception {
        logger.info("Processing message: {}", message.getBody());
        
        // Extract S3 URI from the message
        String s3Uri = extractS3UriFromMessage(message.getBody());
        if (s3Uri == null || s3Uri.isEmpty()) {
            throw new IllegalArgumentException("Could not extract S3 URI from message");
        }
        
        logger.info("Extracted S3 URI: {}", s3Uri);
        
        // Process the video using Bedrock
        String result = processVideoWithBedrock(s3Uri);
        
        // Log the result
        logger.info("Video classification result: {}", result);
    }
    
    private String extractS3UriFromMessage(String messageBody) {
        try {
            // Assuming the message body is JSON and contains an s3Uri field
            // This is a simple regex extraction - in production you might want to use a JSON parser
            logger.info("Extracting S3 URI from message body: {}", messageBody);
            Pattern pattern = Pattern.compile("\"s3Uri\"\\s*:\\s*\"(s3://[^\"]+)\"");
            Matcher matcher = pattern.matcher(messageBody);
            
            if (matcher.find()) {
                return matcher.group(1);
            }
            
            // Alternative approach: try to find any S3 URI in the message
            pattern = Pattern.compile("(s3://[\\w\\-\\.]+/[\\w\\-\\./]+)");
            matcher = pattern.matcher(messageBody);
            
            if (matcher.find()) {
                return matcher.group(1);
            }
            
            logger.warn("Could not extract S3 URI from message: {}", messageBody);
            return null;
        } catch (Exception e) {
            logger.error("Error extracting S3 URI: {}", e.getMessage(), e);
            return null;
        }
    }
    
    private String processVideoWithBedrock(String s3Uri) throws Exception {
        logger.info("Processing video from S3 URI: {}", s3Uri);
        
        // Create video content block
        ContentBlock videoContent = ContentBlock.builder()
                .video(video -> video
                        .format("mp4")
                        .source(source -> source
                                .s3Location(s3 -> s3
                                        .uri(s3Uri))))
                .build();
        
        // Read prompt from file
        String prompt = Files.readString(new File("prompt.md").toPath());
        ContentBlock textContent = ContentBlock.fromText(prompt);
        
        // Create message with both video and text content
        Message message = Message.builder()
                .content(Arrays.asList(videoContent, textContent))
                .role(ConversationRole.USER)
                .build();
        
        try {
            // Call Bedrock Runtime API
            ConverseResponse response = bedrockClient.converse(request -> request
                    .modelId("amazon.nova-lite-v1:0")
                    .system(SystemContentBlock.builder().text("You are a video classify ").build())
                    .messages(message)
                    .inferenceConfig(config -> config
                            .maxTokens(4096)
                            .temperature(0.5F)
                            .topP(0.9F)));
            
            // Extract and return the response text
            String responseText = response.output().message().content().get(0).text();
            return responseText;
        } catch (SdkClientException e) {
            logger.error("Error invoking Bedrock: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to process video with Bedrock", e);
        }
    }
    
    private void deleteMessage(SQSMessage message) {
        logger.info("Deleting message {} from queue {}", message.getMessageId(), queueUrl);
        
        sqsClient.deleteMessage(DeleteMessageRequest.builder()
                .queueUrl(queueUrl)
                .receiptHandle(message.getReceiptHandle())
                .build());
    }
}
