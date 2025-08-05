#!/bin/bash

echo "🚀 Testing 10 messages through Amazon MQ..."

# Port forward in background
kubectl port-forward -n logs-collect svc/mq-test-app-service 8082:80 &
PF_PID=$!

# Wait for port forward to be ready
echo "⏳ Waiting for port forward to be ready..."
sleep 5

echo "📤 Sending 10 messages..."

# Send 10 messages
for i in {1..10}; do
    echo "Sending message $i..."
    response=$(curl -s -X POST http://localhost:8082/api/mq/send \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Test message #$i from batch test at $(date)\"}")
    
    if [[ $response == *"success"* ]]; then
        echo "✅ Message $i sent successfully"
    else
        echo "❌ Message $i failed: $response"
    fi
    
    # Small delay between messages
    sleep 0.5
done

echo "⏳ Waiting for messages to be processed..."
sleep 5

# Kill port forward
kill $PF_PID 2>/dev/null

echo "✅ Test completed! Check the application logs to see all messages."
