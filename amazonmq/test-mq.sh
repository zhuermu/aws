#!/bin/bash

echo "Testing MQ connectivity..."

# Port forward in background
kubectl port-forward -n logs-collect svc/mq-test-app-service 8080:80 &
PF_PID=$!

# Wait for port forward to be ready
sleep 5

echo "Sending test message..."
response=$(curl -s -X POST http://localhost:8080/api/mq/send-test -H "Content-Type: application/json")
echo "Response: $response"

echo "Checking health endpoint..."
health=$(curl -s http://localhost:8080/api/mq/health)
echo "Health: $health"

echo "Checking actuator health..."
actuator_health=$(curl -s http://localhost:8080/actuator/health)
echo "Actuator Health: $actuator_health"

# Kill port forward
kill $PF_PID

echo "Test completed!"
