# video-classification

## description
1. download the url link from local file ./tiktok-video.csv and upload to s3
2. classify video and add tags to the video and output to csv file by using amazon nova pro.

> cp .env.example .env

edit .env as your aws configuration: aws access key, secret key, region, s3 bucket name, s3 bucket path

> source .env

build
> mvn clean package
upload video to s3, if your video exits, you can skip this step
> java -jar target/video-classification-1.0-SNAPSHOT.jar upload

classify video and output to csv file
java -jar target/video-classification-1.0-SNAPSHOT.jar classify


## Another AWS account S3 bucket
If the bucket belongs to another AWS account, specify that account’s ID. add the bucketOwnerAccountId when you call the converse method.
1. api doc:
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html

2. add bucket policy to allow the account to access the bucket
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCrossAccountUserAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::ACCOUNT_ID:user/YOUR_USERNAME"
            },
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

## deployment
使用aws cli 命令行完成以下操作：
```bash
# 1. 创建一个s3 存储桶名称为 video-classify;

aws s3api create-bucket \
    --bucket video-classify \
    --region us-east-1

# 2. 创建一个SQS topic 名称为 video-event-from-s3;
# 创建 SQS 队列
aws sqs create-queue \
    --queue-name video-event-from-s3 \
    --region us-east-1

# 3. 获取 SQS 队列 ARN
aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/$YOUR_ACCOUNT_ID/video-event-from-s3 \
    --attribute-names QueueArn

# 4. 创建一个lambda函数名为 video-classify-from-sqs，使用java 17环境来创建；
创建 Lambda 函数:
首先创建 Lambda 执行角色:
# 创建角色信任策略文件 trust-policy.json
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 创建 Lambda 执行角色
aws iam create-role \
    --role-name lambda-video-classify-role \
    --assume-role-policy-document file://trust-policy.json

# 附加基础 Lambda 执行策略
aws iam attach-role-policy \
    --role-name lambda-video-classify-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# 附加 SQS 权限策略
cat > sqs-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": "arn:aws:sqs:us-east-1:$YOUR_ACCOUNT_ID:video-event-from-s3"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name lambda-video-classify-role \
    --policy-name sqs-permissions \
    --policy-document file://sqs-policy.json

# 创建 Lambda 函数 (假设已经准备好了代码包 function.zip)
aws lambda create-function \
    --function-name video-classify-from-sqs \
    --runtime java17 \
    --handler com.example.Handler::handleRequest \
    --role arn:aws:iam::767828766472:role/lambda-video-classify-role \
    --zip-file fileb:///home/xiaowely/ws/git/zhuermu/aws/lambda/video-classify/video-classify.zip \
    --memory-size 512 \
    --timeout 30

3. 配置s3 存储桶video-classify Event notifications，选择SQS topic video-event-from-s3；
# 创建 S3 通知权限策略
cat > s3-notification-policy.json << EOF
{
    "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AllowS3ToSendMessage\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"s3.amazonaws.com\"},\"Action\":\"SQS:SendMessage\",\"Resource\":\"arn:aws:sqs:us-east-1:$YOUR_ACCOUNT_ID:video-event-from-s3\",\"Condition\":{\"ArnLike\":{\"aws:SourceArn\":\"arn:aws:s3:::video-classify\"}}}]}"
}
EOF

# 设置 SQS 队列策略
aws sqs set-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/$YOUR_ACCOUNT_ID/video-event-from-s3 \
    --attributes file://s3-notification-policy.json

# 配置 S3 事件通知
cat > notification.json << EOF
{
    "QueueConfigurations": [
        {
            "Id": "video-classify-event",
            "QueueArn": "arn:aws:sqs:us-east-1:$YOUR_ACCOUNT_ID:video-event-from-s3",
            "Events": ["s3:ObjectCreated:*"]
        }
    ]
}
EOF

aws s3api put-bucket-notification-configuration \
    --bucket video-classify \
    --notification-configuration file://notification.json

4. 配置lambda函数video-classify-from-sqs的触发器为SQS topic video-event-from-s3； 

aws lambda create-event-source-mapping \
    --function-name video-classify-from-sqs \
    --batch-size 1 \
    --event-source-arn arn:aws:sqs:us-east-1:$YOUR_ACCOUNT_ID:video-event-from-s3
```