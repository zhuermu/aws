package com.zhuermu;

import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.document.Document;
import software.amazon.awssdk.core.exception.SdkClientException;
import software.amazon.awssdk.core.retry.RetryMode;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.*;

import java.time.Duration;

class VideoUnderstandTest {

    private static final Logger log = LoggerFactory.getLogger(VideoUnderstandTest.class);

    /**
     * 原生aws bedrock客户端
     */
    @Test
    void awsBedrockConverseTest() {
        String[] videos = {
            "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/20251111-110712-caijian.mp4",
            "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/09211f8f-8d39-4038-ae0b-568b4e25bb26-FunPlay1.mp4",
            "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/6b80e970-67e6-4ee4-a51e-8ceb660e9c54-1000012057.mp4"
        };
        
        software.amazon.awssdk.http.SdkHttpClient sdkHttpClient = ApacheHttpClient.builder()
                .connectionTimeout(Duration.ofSeconds(10))
                .socketTimeout(Duration.ofSeconds(120))
                .build();
        BedrockRuntimeClient client = BedrockRuntimeClient.builder()
                .httpClient(sdkHttpClient)
                .credentialsProvider(DefaultCredentialsProvider.create())
                .region(Region.US_EAST_1)
                .overrideConfiguration(config -> config.retryStrategy(RetryMode.STANDARD))
                .build();

        String modelId = "global.amazon.nova-2-lite-v1:0";
        
        for (int i = 0; i < videos.length; i++) {
            String s3Url = videos[i];
            log.info("\n========== Video {} ==========\nURL: {}", i + 1, s3Url);
            
            S3Location s3Location = S3Location.builder().uri(s3Url).build();
            var message = Message.builder()
                    .content(ContentBlock.fromVideo(VideoBlock.builder()
                                    .format(VideoFormat.MP4)
                                    .source(VideoSource.builder().s3Location(s3Location).build())
                                    .build()),
                            ContentBlock.fromText("""
                                You are a video content analyzer. Analyze the provided video and identify which of the following user actions are shown:
                                                                
                                1. Keyword Search: Check if the keywords entered by the user starts with "Teen Patti master Explorer slots game play" or similar wording.
                                2. Found Target Video - Title Verification: Check if the title of the video played by the user starts with "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039" or similar wording. If the first few words match, it should also be considered as passed.
                                3. Found Target Video – Creator Verification: The creator name of the video played by the user must be "PVgaming00" or "PVgaming00" to be considered valid. The creator’s name is located below the video title.
                                4. Video Play Duration: Locate the segment where the target video is being played. Specify the start and end times of the playback in MM:SS format.
                                                                
                                **Output Format:**
                                (Y/N, If it meets items 1 and 2 above, it will pass. Output Y, otherwise output N.)
                                {
                                  "auditDetails": [
                                    {
                                      "stepNo": 1,
                                      "stepName": "Keyword Search",
                                      "state": "(Y/N)",
                                      "expected": "Teen Patti master Explorer slots game play",
                                      "actual": "(Keywords actually searched by the user)"
                                    },
                                    {
                                      "stepNo": 2,
                                      "stepName": "Found Target Video - Title Verification",
                                      "state": "(Y/N)",
                                      "expected": "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039",
                                      "actual": "(Title of the video being played)"
                                    },
                                    {
                                      "stepNo": 3,
                                      "stepName": "Found Target Video - Creator Verification",
                                      "expected": "videoCreator: PVgaming00 or channelId: PVgaming00",
                                      "actual": "(Creator of the video being played)",
                                      "state": "(Y/N), actual must be PVgaming00 or PVgaming00 to be considered valid",
                                    },
                                    {
                                      "stepNo": 4,
                                      "stepName": "Video Play Duration",
                                      "startTime": "(MM:SS timestamp in this recording when video starts playing)",
                                      "endTime": "(MM:SS timestamp in this recording when video stops playing)"
                                    }
                                  ]
                                }
                                """))
                    .role(ConversationRole.USER)
                    .build();

            ConverseRequest request = ConverseRequest.builder()
                    .modelId(modelId)
                    .messages(message)
                    .serviceTier(ServiceTier.builder().type("flex").build())
                    .inferenceConfig(config -> config
                            .maxTokens(1024)
                            .temperature(0.0F))
                    .build();

            long startTime = System.currentTimeMillis();
            try {
                ConverseResponse response = client.converse(request);
                String text = response.output().message().content().get(0).text();
                log.info("Result:\n{}", text);
                log.info("Cost: {}ms", System.currentTimeMillis() - startTime);
            } catch (SdkClientException e) {
                log.error("Error: {}", e.getMessage());
            }
        }
    }
}
