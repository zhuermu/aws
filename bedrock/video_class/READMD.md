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