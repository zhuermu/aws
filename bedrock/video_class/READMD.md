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
