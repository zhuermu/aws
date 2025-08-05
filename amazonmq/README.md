# Amazon MQ Test Application

This repository contains a Spring Boot application for testing Amazon MQ (RabbitMQ) connectivity.

## Configuration

Before running the application, you need to configure the following sensitive information:

### 1. Application Configuration (`mq-test-app/src/main/resources/application.yml`)

Replace the placeholders with your actual values:

```yaml
spring:
  rabbitmq:
    host: <your-amazonmq-broker-endpoint>  # Your Amazon MQ broker endpoint
    username: <username>                   # Your RabbitMQ username
    password: <password>                   # Your RabbitMQ password
```

### 2. Kubernetes Deployment (`mq-test-app/k8s/deployment.yaml`)

Replace the placeholder with your actual ECR repository:

```yaml
image: <your-account-id>.dkr.ecr.<region>.amazonaws.com/mq-test-app:latest
```

## Files Structure

- `mq-test-app/` - Spring Boot application for MQ testing
- `test-mq.sh` - Script to test MQ connectivity
- `send-10-messages.sh` - Script to send 10 test messages
- `mq-test-app/k8s/deployment.yaml` - Kubernetes deployment configuration

## Usage

1. Configure the sensitive information as described above
2. Build and deploy the application
3. Use the provided scripts to test MQ functionality

## Security Note

This repository has been sanitized to remove sensitive information. Make sure to:
- Never commit actual credentials to version control
- Use environment variables or secret management systems for production
- Consider using AWS Secrets Manager or Kubernetes secrets for sensitive data
