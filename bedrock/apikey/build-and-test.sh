#!/bin/bash

echo "Building the project..."
mvn clean compile

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo ""
    echo "Testing AWS SDK approach..."
    mvn exec:java -Dexec.mainClass="com.example.BedrockClient" -q
    
    echo ""
    echo "If you want to test the HTTP client approach, set AWS_BEARER_TOKEN_BEDROCK and run:"
    echo "mvn exec:java -Dexec.mainClass=\"com.example.BedrockHttpClient\" -q"
else
    echo "Build failed!"
    exit 1
fi
