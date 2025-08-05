package com.example.mqtest.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;

@Service
public class ConnectionHealthService {

    private static final Logger logger = LoggerFactory.getLogger(ConnectionHealthService.class);

    @Autowired
    private ConnectionFactory connectionFactory;

    @EventListener(ApplicationReadyEvent.class)
    public void checkConnectionOnStartup() {
        checkConnection();
    }

    public boolean checkConnection() {
        try {
            logger.info("Testing RabbitMQ connection...");
            
            // Test connection by creating and closing a connection
            var connection = connectionFactory.createConnection();
            if (connection.isOpen()) {
                logger.info("✅ Successfully connected to Amazon MQ RabbitMQ!");
                logger.info("Connection details: {}", connection.toString());
                connection.close();
                return true;
            } else {
                logger.error("❌ Connection is not open");
                return false;
            }
        } catch (Exception e) {
            logger.error("❌ Failed to connect to Amazon MQ RabbitMQ: {}", e.getMessage(), e);
            return false;
        }
    }
}
