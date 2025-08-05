package com.example.mqtest.service;

import com.example.mqtest.config.RabbitConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
public class MessageProducer {

    private static final Logger logger = LoggerFactory.getLogger(MessageProducer.class);

    @Autowired
    private RabbitTemplate rabbitTemplate;

    public void sendMessage(String message) {
        try {
            Map<String, Object> messageBody = new HashMap<>();
            messageBody.put("content", message);
            messageBody.put("timestamp", LocalDateTime.now().toString());
            messageBody.put("source", "mq-test-app");

            rabbitTemplate.convertAndSend(
                    RabbitConfig.TEST_EXCHANGE,
                    RabbitConfig.TEST_ROUTING_KEY,
                    messageBody
            );

            logger.info("Message sent successfully: {}", message);
        } catch (Exception e) {
            logger.error("Failed to send message: {}", message, e);
            throw new RuntimeException("Failed to send message", e);
        }
    }

    public void sendTestMessage() {
        String testMessage = "Test message from Spring Boot at " + LocalDateTime.now();
        sendMessage(testMessage);
    }
}
