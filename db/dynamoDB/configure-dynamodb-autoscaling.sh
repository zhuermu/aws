#!/bin/bash
# DynamoDB 自动扩展配置脚本

# 配置参数
TABLE_NAME="first_dyn_table_new"
MIN_CAPACITY=5
MAX_CAPACITY=100
TARGET_VALUE=10  # 目标利用率 10%
REGION="us-east-1"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始为 DynamoDB 表 $TABLE_NAME 配置自动扩展...${NC}"

# 获取表的 ARN
TABLE_ARN=$(aws dynamodb describe-table \
    --table-name $TABLE_NAME \
    --region $REGION \
    --query "Table.TableArn" \
    --output text)

if [ $? -ne 0 ]; then
    echo -e "${RED}获取表 ARN 失败，请确认表名和权限${NC}"
    exit 1
fi

echo -e "${GREEN}表 ARN: $TABLE_ARN${NC}"

# 为读取容量注册可扩展目标
echo -e "${YELLOW}为读取容量注册可扩展目标...${NC}"
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id "table/$TABLE_NAME" \
    --scalable-dimension "dynamodb:table:ReadCapacityUnits" \
    --min-capacity $MIN_CAPACITY \
    --max-capacity $MAX_CAPACITY \
    --region $REGION

if [ $? -ne 0 ]; then
    echo -e "${RED}为读取容量注册可扩展目标失败${NC}"
    exit 1
fi

# 为写入容量注册可扩展目标
echo -e "${YELLOW}为写入容量注册可扩展目标...${NC}"
aws application-autoscaling register-scalable-target \
    --service-namespace dynamodb \
    --resource-id "table/$TABLE_NAME" \
    --scalable-dimension "dynamodb:table:WriteCapacityUnits" \
    --min-capacity $MIN_CAPACITY \
    --max-capacity $MAX_CAPACITY \
    --region $REGION

if [ $? -ne 0 ]; then
    echo -e "${RED}为写入容量注册可扩展目标失败${NC}"
    exit 1
fi

# 为读取容量配置扩展策略
echo -e "${YELLOW}为读取容量配置扩展策略...${NC}"
aws application-autoscaling put-scaling-policy \
    --service-namespace dynamodb \
    --resource-id "table/$TABLE_NAME" \
    --scalable-dimension "dynamodb:table:ReadCapacityUnits" \
    --policy-name "DynamoDBReadCapacityUtilization:$TABLE_NAME" \
    --policy-type "TargetTrackingScaling" \
    --target-tracking-scaling-policy-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "DynamoDBReadCapacityUtilization"
        },
        "TargetValue": '$TARGET_VALUE',
        "ScaleOutCooldown": 60,
        "ScaleInCooldown": 60
    }' \
    --region $REGION

if [ $? -ne 0 ]; then
    echo -e "${RED}为读取容量配置扩展策略失败${NC}"
    exit 1
fi

# 为写入容量配置扩展策略
echo -e "${YELLOW}为写入容量配置扩展策略...${NC}"
aws application-autoscaling put-scaling-policy \
    --service-namespace dynamodb \
    --resource-id "table/$TABLE_NAME" \
    --scalable-dimension "dynamodb:table:WriteCapacityUnits" \
    --policy-name "DynamoDBWriteCapacityUtilization:$TABLE_NAME" \
    --policy-type "TargetTrackingScaling" \
    --target-tracking-scaling-policy-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "DynamoDBWriteCapacityUtilization"
        },
        "TargetValue": '$TARGET_VALUE',
        "ScaleOutCooldown": 60,
        "ScaleInCooldown": 60
    }' \
    --region $REGION

if [ $? -ne 0 ]; then
    echo -e "${RED}为写入容量配置扩展策略失败${NC}"
    exit 1
fi

echo -e "${GREEN}DynamoDB 表 $TABLE_NAME 的自动扩展配置已完成！${NC}"
echo -e "${GREEN}目标利用率: $TARGET_VALUE%${NC}"
echo -e "${GREEN}最小容量: $MIN_CAPACITY${NC}"
echo -e "${GREEN}最大容量: $MAX_CAPACITY${NC}"
echo -e "${YELLOW}可以使用以下命令验证配置:${NC}"
echo "aws application-autoscaling describe-scalable-targets --service-namespace dynamodb --resource-ids \"table/$TABLE_NAME\" --region $REGION"
echo "aws application-autoscaling describe-scaling-policies --service-namespace dynamodb --resource-id \"table/$TABLE_NAME\" --region $REGION"
