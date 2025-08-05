package com.example.mqtest.service;

import com.example.mqtest.config.RabbitConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class MessageConsumer {

    private static final Logger logger = LoggerFactory.getLogger(MessageConsumer.class);

    @RabbitListener(queues = RabbitConfig.TEST_QUEUE)
    public void receiveMessage(Map<String, Object> message) {
        try {
            logger.info("Received message: {}", message);
            
            String content = (String) message.get("content");
            String timestamp = (String) message.get("timestamp");
            String source = (String) message.get("source");
            
            logger.info("Message details - Content: {}, Timestamp: {}, Source: {}", 
                       content, timestamp, source);
        } catch (Exception e) {
            logger.error("Error processing message: {}", message, e);
        }
    }
}
