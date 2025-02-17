package com.zhuermu;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.zhuermu.model.ClassificationResult;
import com.zhuermu.service.BedrockService;
import com.zhuermu.service.S3Service;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

@Slf4j
public class VideoClassification {
    private static final String BUCKET_NAME = System.getenv("AWS_S3_BUCKET_NAME");
    private static final String FOLDER_NAME = System.getenv("AWS_S3_BUCKET_FOLDER_NAME");
    private static final String CSV_FILE = "classification-video.csv";
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final int BATCH_SIZE = 5;
    private static final long BATCH_DELAY_MS = 5000; // 5 seconds delay between batches
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java -jar video-classification.jar [upload|classify]");
            System.out.println("Date format: yyyy-MM-dd HH:mm:ss");
            System.exit(1);
        }

        String command = args[0];
        
        try {
            log.info("Starting video classification application in {} mode", command);
            
            S3Service s3Service = new S3Service(BUCKET_NAME, FOLDER_NAME);
            BedrockService bedrockService = new BedrockService();
            
            switch (command) {
                case "upload":
                    uploadVideos(s3Service);
                    break;
                case "classify":
                    LocalDateTime cutoffDate = LocalDateTime.parse("2025-01-01 00:00:00", DATE_FORMATTER);
                    classifyVideos(bedrockService, cutoffDate);
                    break;
                default:
                    System.out.println("Invalid command. Use 'upload' or 'classify'");
                    System.exit(1);
            }
            
            s3Service.cleanup();
            log.info("Operation completed successfully");
        } catch (Exception e) {
            log.error("Application failed", e);
            System.exit(1);
        }
    }

    private static void uploadVideos(S3Service s3Service) throws IOException {
        Path inputPath = Paths.get("tiktok-video.csv");
        log.info("Reading input CSV from: {}", inputPath.toAbsolutePath());
        
        CSVFormat csvFormat = CSVFormat.DEFAULT.builder()
                .setSkipHeaderRecord(false)
                .build();

        try (CSVParser parser = new CSVParser(new FileReader(inputPath.toFile()), csvFormat)) {
            int uploadedCount = 0;
            int errorCount = 0;
            
            for (CSVRecord record : parser) {
                String videoUrl = record.get(0);
                if (videoUrl.startsWith("http")) {
                    try {
                        s3Service.uploadVideo(videoUrl);
                        uploadedCount++;
                    } catch (Exception e) {
                        log.error("Failed to upload video: {}", videoUrl, e);
                        errorCount++;
                    }
                }
            }
            
            log.info("Completed uploading videos. Uploaded: {}, Errors: {}", 
                    uploadedCount, errorCount);
        }
    }

    private static void classifyVideos(BedrockService bedrockService, LocalDateTime cutoffDate) throws IOException {
        Path csvPath = Paths.get(CSV_FILE);
        Path tempPath = Paths.get(CSV_FILE + ".tmp");
        
        CSVFormat csvFormat = CSVFormat.DEFAULT.builder()
                .setHeader()
                .setSkipHeaderRecord(true)
                .build();

        // Create a temporary file for writing updates
        try (CSVParser parser = new CSVParser(new FileReader(csvPath.toFile()), csvFormat);
             CSVPrinter printer = new CSVPrinter(new FileWriter(tempPath.toFile()), 
                     CSVFormat.DEFAULT.withHeader("URL", "S3", "OutPut", "DateTime"))) {
            
            List<CSVRecord> batchRecords = new ArrayList<>();
            int batchCount = 0;
            
            for (CSVRecord record : parser) {
                String dateTime = record.get("DateTime");
                boolean shouldProcess = dateTime.isEmpty();
                
                if (!shouldProcess && !dateTime.isEmpty()) {
                    try {
                        LocalDateTime recordDate = LocalDateTime.parse(dateTime, DATE_FORMATTER);
                        shouldProcess = recordDate.isBefore(cutoffDate);
                    } catch (Exception e) {
                        log.warn("Invalid date format in record: {}", dateTime);
                        shouldProcess = true;
                    }
                }

                if (shouldProcess) {
                    batchRecords.add(record);
                    
                    // Process batch when it reaches BATCH_SIZE
                    if (batchRecords.size() >= BATCH_SIZE) {
                        processBatchAndWrite(batchRecords, bedrockService, printer);
                        batchCount++;
                        log.info("Completed batch {}", batchCount);
                        batchRecords.clear();
                        
                        // Add delay between batches
                        try {
                            Thread.sleep(BATCH_DELAY_MS);
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            throw new RuntimeException("Thread interrupted while processing", e);
                        }
                    }
                } else {
                    // Write unprocessed record as-is
                    printer.printRecord(
                        record.get("URL"),
                        record.get("S3"),
                        record.get("OutPut"),
                        record.get("DateTime")
                    );
                }
            }
            
            // Process remaining records in the last batch
            if (!batchRecords.isEmpty()) {
                processBatchAndWrite(batchRecords, bedrockService, printer);
            }
        }
        
        // Replace original file with updated file
        Files.move(tempPath, csvPath, StandardCopyOption.REPLACE_EXISTING);
        log.info("Updated classification results in: {}", csvPath);
    }

    private static void processBatchAndWrite(List<CSVRecord> batch, BedrockService bedrockService, CSVPrinter printer) 
            throws IOException {
        for (CSVRecord record : batch) {
            String s3Uri = record.get("S3");
            String output = record.get("OutPut");
            String dateTime = LocalDateTime.now().format(DATE_FORMATTER);
            
            try {
                ClassificationResult result = bedrockService.classifyVideo(s3Uri);
                output = formatClassificationResult(result);
                log.info("Successfully processed video: {}", s3Uri);
            } catch (Exception e) {
                log.error("Failed to process video: {}", s3Uri, e);
                output = "Error: " + e.getMessage();
            }
            
            printer.printRecord(
                record.get("URL"),
                s3Uri,
                output,
                dateTime
            );
        }
        printer.flush();
    }

    private static String formatClassificationResult(ClassificationResult result) {
        StringBuilder sb = new StringBuilder();
        
        // Add categories
        if (!result.getCategories().isEmpty()) {
            sb.append("Categories: ");
            sb.append(result.getCategories().get(0).getCategory1());
            sb.append(" > ");
            sb.append(result.getCategories().get(0).getCategory2());
            sb.append(" > ");
            sb.append(String.join(", ", result.getCategories().get(0).getCategory3()));
        }
        
        // Add tags
        if (!result.getTags().isEmpty()) {
            if (sb.length() > 0) {
                sb.append(" | ");
            }
            sb.append("Tags: ");
            sb.append(result.getTags().stream()
                    .map(tag -> tag.getName() + "(" + tag.getScore() + ")")
                    .reduce((a, b) -> a + ", " + b)
                    .orElse(""));
        }
        
        return sb.toString();
    }
}
