package com.zhuermu.service;

import lombok.extern.slf4j.Slf4j;
import org.apache.hc.client5.http.classic.methods.HttpGet;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Response;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.S3Object;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
public class S3Service {
    private final S3Client s3Client;
    private final String bucketName;
    private final String folderName;
    private final Path tempDir;

    public S3Service(String bucketName, String folderName) throws IOException {
        this.s3Client = S3Client.builder()
                .region(Region.US_EAST_1)
                .build();
        this.bucketName = bucketName;
        this.folderName = folderName;
        this.tempDir = Files.createTempDirectory("video-downloads");
    }

    public String uploadVideo(String videoUrl) {
        try {
            log.info("Starting video upload process for URL: {}", videoUrl);
            
            // Download video to temp file
            String fileName = extractFileName(videoUrl);
            Path tempFile = tempDir.resolve(fileName);
            log.info("Downloading video to temp file: {}", tempFile);
            downloadVideo(videoUrl, tempFile.toFile());
            log.info("Successfully downloaded video to temp file");

            // Upload to S3
            String s3Key = folderName + "/" + fileName;
            log.info("Uploading video to S3 with key: {}", s3Key);
            s3Client.putObject(PutObjectRequest.builder()
                            .bucket(bucketName)
                            .key(s3Key)
                            .build(),
                    RequestBody.fromFile(tempFile));

            log.info("Successfully uploaded video to S3: {}", s3Key);
            return s3Key;
        } catch (Exception e) {
            log.error("Failed to upload video to S3", e);
            throw new RuntimeException("Failed to upload video to S3", e);
        }
    }

    public List<String> listVideos() {
        log.info("Listing videos in bucket: {}, folder: {}", bucketName, folderName);
        
        ListObjectsV2Request request = ListObjectsV2Request.builder()
                .bucket(bucketName)
                .prefix(folderName + "/")
                .build();
                
        ListObjectsV2Response response = s3Client.listObjectsV2(request);
        
        List<String> videoKeys = response.contents().stream()
                .map(S3Object::key)
                .filter(key -> key.toLowerCase().endsWith(".mp4"))
                .collect(Collectors.toList());
                
        log.info("Found {} videos in S3", videoKeys.size());
        return videoKeys;
    }

    private void downloadVideo(String videoUrl, File outputFile) throws IOException {
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpGet request = new HttpGet(videoUrl);
            httpClient.execute(request, response -> {
                try (FileOutputStream out = new FileOutputStream(outputFile)) {
                    response.getEntity().writeTo(out);
                }
                return null;
            });
        }
    }

    private String extractFileName(String videoUrl) {
        int lastSlash = videoUrl.lastIndexOf('/');
        if (lastSlash == -1) {
            throw new IllegalArgumentException("Invalid video URL format");
        }
        return videoUrl.substring(lastSlash + 1);
    }

    public void cleanup() {
        try {
            Files.walk(tempDir)
                .filter(Files::isRegularFile)
                .forEach(path -> {
                    try {
                        Files.delete(path);
                    } catch (IOException e) {
                        log.warn("Failed to delete temp file: {}", path, e);
                    }
                });
            Files.deleteIfExists(tempDir);
        } catch (IOException e) {
            log.warn("Failed to cleanup temp directory", e);
        }
    }
}
