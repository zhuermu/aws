package com.example.mqtest.controller;

import com.example.mqtest.service.MessageProducer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/mq")
public class MqTestController {

    private static final Logger logger = LoggerFactory.getLogger(MqTestController.class);

    @Autowired
    private MessageProducer messageProducer;

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "mq-test-app");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/send")
    public ResponseEntity<Map<String, String>> sendMessage(@RequestBody Map<String, String> request) {
        try {
            String message = request.get("message");
            if (message == null || message.trim().isEmpty()) {
                message = "Default test message";
            }

            messageProducer.sendMessage(message);

            Map<String, String> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Message sent successfully");
            response.put("sentMessage", message);

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("Error sending message", e);
            Map<String, String> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", "Failed to send message: " + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }

    @PostMapping("/send-test")
    public ResponseEntity<Map<String, String>> sendTestMessage() {
        try {
            messageProducer.sendTestMessage();

            Map<String, String> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Test message sent successfully");

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("Error sending test message", e);
            Map<String, String> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", "Failed to send test message: " + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }
}
