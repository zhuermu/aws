package com.zhuermu;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.exception.SdkClientException;
import software.amazon.awssdk.core.internal.http.AmazonAsyncHttpClient;
import software.amazon.awssdk.http.SdkHttpClient;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.*;
import java.io.File;
import java.nio.file.Files;
import java.time.Duration;
import java.util.Arrays;


public class Converse {

    public static String converse(String s3Uri, String bucketOwner) throws Exception {
        SdkHttpClient httpClient = ApacheHttpClient.builder()
        .socketTimeout(Duration.ofMinutes(5))  // Increase socket timeout
        .connectionTimeout(Duration.ofSeconds(30))
        .build();
        var client = BedrockRuntimeClient.builder()
                .credentialsProvider(DefaultCredentialsProvider.create())
                .region(Region.US_EAST_1)
                //.httpClient(httpClient)
                .build();
        //client.wait(60000);
        var modelId = "amazon.nova-lite-v1:0";

        // Create video content block
        var videoContent = ContentBlock.builder()
                .video(video -> video
                        .format("mp4")
                        .source(source -> source
                                .s3Location(s3 -> s3
                                        .uri(s3Uri)
                                        //.bucketOwner(bucketOwner)
                                        )))

                .build();

        // Create text content block
        // read file from local prompt.md
        var prompt = Files.readString(new File("prompt.md").toPath());
        var textContent = ContentBlock.fromText(prompt);

        // Create message with both video and text content
        var message = Message.builder()
                .content(Arrays.asList(videoContent, textContent))
                .role(ConversationRole.USER)
                .build();
        try {
            ConverseResponse response = client.converse(request -> request
                    .modelId(modelId)
                    .system(SystemContentBlock.builder().text("You are a helpful assistant.").build())
                    .messages(message)
                    .inferenceConfig(config -> config
                            .maxTokens(4096)
                            .temperature(0.5F)
                            .topP(0.9F)));

            var responseText = response.output().message().content().get(0).text();
            System.out.println(responseText);
            return responseText;

        } catch (SdkClientException e) {
            System.err.printf("ERROR: Can't invoke '%s'. Reason: %s", modelId, e.getMessage());
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args) {
        String s3Uri = "s3://video-classify/204fcf5a-20f0-4746-9f84-e65d0acc5402.mp4";
        String bucketOwner = "";
        try {
            converse(s3Uri, bucketOwner);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
