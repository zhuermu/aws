#!/bin/bash
# 部署静态网站到 S3 + CloudFront

set -e

BUCKET_NAME="nova-gemini-test-results-site"
REGION="us-east-1"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 开始部署静态网站..."
echo "📦 Bucket: $BUCKET_NAME"

# 1. 创建 S3 bucket (如果不存在)
echo "📁 创建 S3 bucket..."
aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket 已存在"

# 2. 配置静态网站托管
echo "🌐 配置静态网站托管..."
aws s3 website s3://$BUCKET_NAME --index-document index.html

# 3. 禁用 Block Public Access
echo "🔓 配置公开访问..."
aws s3api put-public-access-block --bucket $BUCKET_NAME --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 4. 设置 bucket policy
echo "🔐 配置 bucket policy..."
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
        \"Sid\": \"PublicReadGetObject\",
        \"Effect\": \"Allow\",
        \"Principal\": \"*\",
        \"Action\": \"s3:GetObject\",
        \"Resource\": \"arn:aws:s3:::$BUCKET_NAME/*\"
    }]
}"

# 5. 同步文件到 S3
echo "📤 上传文件到 S3..."
cd $PROJECT_DIR

aws s3 sync . s3://$BUCKET_NAME \
    --exclude ".venv/*" \
    --exclude ".git/*" \
    --exclude ".claude/*" \
    --exclude ".amazonq/*" \
    --exclude ".kiro/*" \
    --exclude ".vscode/*" \
    --exclude "__pycache__/*" \
    --exclude "*.py" \
    --exclude "*.sh" \
    --exclude "*.pyc" \
    --exclude ".DS_Store" \
    --exclude ".gitignore" \
    --exclude "requirements.txt" \
    --exclude "test_results_archive/*" \
    --exclude "deploy-info.txt"

echo ""
echo "✅ S3 上传完成!"
echo "🌐 S3 Website: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
