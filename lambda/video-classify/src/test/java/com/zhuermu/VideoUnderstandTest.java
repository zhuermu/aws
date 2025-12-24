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

import java.io.FileWriter;
import java.io.IOException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

class VideoUnderstandTest {

    private static final Logger log = LoggerFactory.getLogger(VideoUnderstandTest.class);

    /**
     * 原生aws bedrock客户端
     */
    @Test
    void awsBedrockConverseTest() {
        String[] videos = {
            "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/ee51c5a7-a44f-4f0b-82d2-772736aa36f3-Screenrecorder20251107140342212.mp4",
            "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/youtube-search-aws.mp4",
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
                                                                
                                StepNo 1. Keyword Search -- Check if the keywords entered by the user starts with "Teen Patti master Explorer slots game play" or similar wording.
                                StepNo 2. Found Target Video -- Title Verification: Check if the title of the video played by the user starts with "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039" or similar wording. If the first few words match, it should also be considered as passed.
                                StepNo 3. Found Target Video –- Creator Verification: The creator name of the video played by the user must be "PVgaming00" or "PVgaming00" to be considered valid. The creator’s name is located below the video title.
                                StepNo 4. Target Video Playback Duration -- Localize the segments where the target video is being played. Answer with the starting and ending time in seconds. If the video is played multiple times, list all segments.
                                                                
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
                                      "state": "(Y/N)",
                                      "expected": "videoCreator: PVgaming00 or channelId: PVgaming00",
                                      "actual": "(Creator of the video being played)",
                                     
                                    },
                                    {
                                      "stepNo": 4,
                                      "stepName": "Video Play Duration",
                                      "segments": "[[start1, end1], [start2, end2], ...] in seconds, e.g. [[72, 82]] or [[40, 50], [72, 82]] if multiple segments"
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
                long cost = System.currentTimeMillis() - startTime;
                log.info("Result:\n{}", text);
                log.info("Cost: {}ms", cost);
                
                // 保存结果到文件
                saveResultToFile(i + 1, s3Url, text, cost);
            } catch (SdkClientException e) {
                log.error("Error: {}", e.getMessage());
            }
        }
    }
    
    private void saveResultToFile(int videoIndex, String s3Url, String result, long cost) {
        String fileName = "test-results-" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd")) + ".md";
        try (FileWriter fw = new FileWriter(fileName, true)) {
            if (videoIndex == 1) {
                fw.write("# Video Understanding Test Results\n\n");
                fw.write("**Test Time**: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "\n\n");
                fw.write("**Model**: global.amazon.nova-2-lite-v1:0\n\n");
                fw.write("---\n\n");
            }
            fw.write("## Video " + videoIndex + "\n\n");
            fw.write("**URL**: `" + s3Url + "`\n\n");
            fw.write("**Cost**: " + cost + "ms\n\n");
            fw.write("**Result**:\n```json\n" + result + "\n```\n\n");
            fw.write("---\n\n");
        } catch (IOException e) {
            log.error("Failed to save result to file: {}", e.getMessage());
        }
    }
}
