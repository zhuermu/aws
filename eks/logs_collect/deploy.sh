#!/bin/bash

# Logs Collect 项目部署脚本
# 功能：创建EKS集群、部署测试应用、配置ALB、创建OpenSearch、部署Fluent-bit

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境变量
check_env_vars() {
    log_info "检查环境变量..."
    
    required_vars=("AWS_ACCOUNT_ID" "DOMAIN_NAME" "CERTIFICATE_ARN" "OPENSEARCH_PASSWORD")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "缺少必需的环境变量："
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "请设置环境变量："
        echo "export AWS_ACCOUNT_ID=\"your-account-id\""
        echo "export DOMAIN_NAME=\"your-domain.com\""
        echo "export CERTIFICATE_ARN=\"arn:aws:acm:us-east-1:account:certificate/cert-id\""
        echo "export OPENSEARCH_PASSWORD=\"your-secure-password\""
        exit 1
    fi
    
    log_success "环境变量检查通过"
}

# 检查必需工具
check_tools() {
    log_info "检查必需工具..."
    
    tools=("aws" "eksctl" "kubectl" "helm")
    missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必需工具："
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        exit 1
    fi
    
    log_success "工具检查通过"
}

# 1. 创建EKS集群
create_eks_cluster() {
    log_info "步骤1: 创建EKS集群 (版本1.33)..."
    
    CLUSTER_NAME="logs-collect-cluster"
    REGION="us-east-1"
    
    if eksctl get cluster --name $CLUSTER_NAME --region $REGION >/dev/null 2>&1; then
        log_warning "EKS集群 $CLUSTER_NAME 已存在，跳过创建"
        
        # 检查集群版本
        CURRENT_VERSION=$(aws eks describe-cluster --name $CLUSTER_NAME --region $REGION --query 'cluster.version' --output text)
        log_info "当前集群版本: $CURRENT_VERSION"
        
        if [ "$CURRENT_VERSION" != "1.33" ]; then
            log_warning "集群版本不是1.33，建议升级集群版本"
        fi
    else
        log_info "使用自动模式创建EKS集群 $CLUSTER_NAME (版本1.33)..."
        log_info "这将自动配置VPC、子网、安全组和托管节点组..."
        
        eksctl create cluster -f cluster-config.yaml
        
        log_success "EKS集群创建完成"
        log_info "集群特性："
        log_info "  ✓ Kubernetes版本: 1.33"
        log_info "  ✓ 托管节点组: 自动扩缩容"
        log_info "  ✓ VPC: 自动创建"
        log_info "  ✓ 插件: 自动安装最新版本"
        log_info "  ✓ Fargate: 已配置"
    fi
    
    # 更新kubeconfig
    aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME
    log_success "kubeconfig已更新"
    
    # 验证集群状态
    log_info "验证集群状态..."
    kubectl get nodes
    kubectl get pods --all-namespaces | head -10
}

# 2. 部署测试应用
deploy_test_app() {
    log_info "步骤2: 部署日志采集测试应用..."
    
    # 替换环境变量并应用配置
    envsubst < test-app-deployment.yaml | kubectl apply -f -
    
    # 等待Pod就绪
    log_info "等待测试应用Pod就绪..."
    kubectl wait --for=condition=ready pod -l app=log-generator -n logs-collect --timeout=300s
    
    log_success "测试应用部署完成"
}

# 3. 部署ALB Ingress Controller和配置
deploy_alb_ingress() {
    log_info "步骤3: 部署ALB Ingress Controller..."
    
    CLUSTER_NAME="logs-collect-cluster"
    
    # 检查是否已经通过eksctl配置了服务账户
    if kubectl get serviceaccount aws-load-balancer-controller -n kube-system >/dev/null 2>&1; then
        log_info "AWS Load Balancer Controller服务账户已存在（通过eksctl配置）"
    else
        # 手动创建IAM角色和策略（备用方案）
        log_info "创建ALB Controller IAM角色..."
        
        # 下载最新IAM策略
        curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.8.1/docs/install/iam_policy.json
        
        # 创建IAM策略
        aws iam create-policy \
            --policy-name AWSLoadBalancerControllerIAMPolicy \
            --policy-document file://iam_policy.json || true
        
        # 创建IAM角色
        eksctl create iamserviceaccount \
            --cluster=$CLUSTER_NAME \
            --namespace=kube-system \
            --name=aws-load-balancer-controller \
            --role-name AmazonEKSLoadBalancerControllerRole \
            --attach-policy-arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy \
            --approve || true
    fi
    
    # 安装AWS Load Balancer Controller
    log_info "安装AWS Load Balancer Controller (最新版本)..."
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    # 检查是否已安装
    if helm list -n kube-system | grep -q aws-load-balancer-controller; then
        log_info "升级AWS Load Balancer Controller..."
        helm upgrade aws-load-balancer-controller eks/aws-load-balancer-controller \
            -n kube-system \
            --set clusterName=$CLUSTER_NAME \
            --set serviceAccount.create=false \
            --set serviceAccount.name=aws-load-balancer-controller \
            --set region=us-east-1 \
            --set vpcId=$(aws eks describe-cluster --name $CLUSTER_NAME --query "cluster.resourcesVpcConfig.vpcId" --output text)
    else
        log_info "安装AWS Load Balancer Controller..."
        helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
            -n kube-system \
            --set clusterName=$CLUSTER_NAME \
            --set serviceAccount.create=false \
            --set serviceAccount.name=aws-load-balancer-controller \
            --set region=us-east-1 \
            --set vpcId=$(aws eks describe-cluster --name $CLUSTER_NAME --query "cluster.resourcesVpcConfig.vpcId" --output text)
    fi
    
    # 等待Controller就绪
    log_info "等待AWS Load Balancer Controller就绪..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=aws-load-balancer-controller -n kube-system --timeout=300s
    
    # 部署Ingress
    log_info "部署ALB Ingress..."
    envsubst < ingress.yaml | kubectl apply -f -
    
    # 等待ALB创建
    log_info "等待ALB创建完成（这可能需要2-3分钟）..."
    sleep 30
    
    log_success "ALB Ingress部署完成"
}

# 4. 创建OpenSearch域
create_opensearch_domain() {
    log_info "步骤4: 创建OpenSearch域..."
    
    DOMAIN_NAME="logs-collect-domain-v2"
    REGION="us-east-1"
    
    log_info "📋 使用最新配置："
    echo "  - 引擎版本: OpenSearch 2.19 (最新)"
    echo "  - 实例类型: r7g.large.search (ARM Graviton3)"
    echo "  - 数据节点: 3 个"
    echo "  - 存储: GP3 300 GiB"
    echo "  - 网络: Public access, IPv4"
    echo "  - 精细访问控制: 启用 (用户名密码认证)"
    echo "  - 加密: 全面启用"
    
    # 检查域是否已存在
    if aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION >/dev/null 2>&1; then
        log_warning "OpenSearch域 $DOMAIN_NAME 已存在，跳过创建"
    else
        log_info "创建OpenSearch域 $DOMAIN_NAME..."
        
        # 创建OpenSearch域 - 启用用户名密码认证
        aws opensearch create-domain \
            --domain-name $DOMAIN_NAME \
            --engine-version "OpenSearch_2.19" \
            --cluster-config '{
                "InstanceType": "r7g.large.search",
                "InstanceCount": 3,
                "DedicatedMasterEnabled": false,
                "ZoneAwarenessEnabled": false,
                "WarmEnabled": false,
                "ColdStorageOptions": {
                    "Enabled": false
                },
                "MultiAZWithStandbyEnabled": false
            }' \
            --ebs-options '{
                "EBSEnabled": true,
                "VolumeType": "gp3",
                "VolumeSize": 300,
                "Iops": 3000,
                "Throughput": 125
            }' \
            --access-policies '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":"*"},"Action":"es:*","Resource":"arn:aws:opensearch:'$REGION':'$AWS_ACCOUNT_ID':domain/'$DOMAIN_NAME'/*"}]}' \
            --domain-endpoint-options '{
                "EnforceHTTPS": true,
                "TLSSecurityPolicy": "Policy-Min-TLS-1-2-2019-07",
                "CustomEndpointEnabled": false
            }' \
            --advanced-security-options '{
                "Enabled": true,
                "InternalUserDatabaseEnabled": true,
                "AnonymousAuthEnabled": false,
                "MasterUserOptions": {
                    "MasterUserName": "admin",
                    "MasterUserPassword": "'$OPENSEARCH_PASSWORD'"
                }
            }' \
            --encryption-at-rest-options '{
                "Enabled": true
            }' \
            --node-to-node-encryption-options '{
                "Enabled": true
            }' \
            --advanced-options '{
                "override_main_response_version": "false",
                "rest.action.multi.allow_explicit_index": "true"
            }' \
            --snapshot-options '{
                "AutomatedSnapshotStartHour": 0
            }' \
            --auto-tune-options '{
                "DesiredState": "DISABLED",
                "UseOffPeakWindow": false
            }' \
            --software-update-options '{
                "AutoSoftwareUpdateEnabled": false
            }' \
            --tag-list '[
                {
                    "Key": "Environment",
                    "Value": "production"
                },
                {
                    "Key": "Project", 
                    "Value": "logs-collect"
                },
                {
                    "Key": "Version",
                    "Value": "v2"
                },
                {
                    "Key": "ManagedBy",
                    "Value": "kubernetes"
                }
            ]' \
            --region $REGION
        
        log_info "等待OpenSearch域创建完成（这可能需要15-20分钟）..."
        
        # 等待域变为可用状态
        while true; do
            STATUS=$(aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION --query 'DomainStatus.DomainProcessingStatus' --output text 2>/dev/null)
            ENDPOINT=$(aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION --query 'DomainStatus.Endpoint' --output text 2>/dev/null)
            
            if [ "$STATUS" = "Active" ] && [ "$ENDPOINT" != "None" ]; then
                log_success "OpenSearch域创建完成！"
                break
            else
                echo "⏳ 域状态: $STATUS, 端点: $ENDPOINT - 等待30秒后重试..."
                sleep 30
            fi
        done
    fi
    
    # 获取OpenSearch端点
    OPENSEARCH_ENDPOINT=$(aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION --query 'DomainStatus.Endpoint' --output text)
    export OPENSEARCH_ENDPOINT
    
    log_info "📊 OpenSearch域信息："
    log_info "  端点: https://$OPENSEARCH_ENDPOINT"
    log_info "  Dashboard: https://$OPENSEARCH_ENDPOINT/_dashboards"
    log_info "  用户名: admin"
    log_info "  密码: $OPENSEARCH_PASSWORD"
    log_info "  访问方式: 需要用户名密码认证"
    log_info "  引擎版本: OpenSearch 2.19"
    log_info "  实例配置: 3 x r7g.large.search"
    log_info "  存储配置: 300 GiB GP3"
}

# 5. 部署Fluent-bit
deploy_fluent_bit() {
    log_info "步骤5: 部署Fluent-bit日志采集..."
    
    # 检查是否已经通过eksctl配置了服务账户
    if kubectl get serviceaccount fluent-bit -n amazon-cloudwatch >/dev/null 2>&1; then
        log_info "Fluent-bit服务账户已存在（通过eksctl配置）"
    else
        # 手动创建Fluent-bit IAM角色（备用方案）
        log_info "创建Fluent-bit IAM角色..."
        
        eksctl create iamserviceaccount \
            --cluster=logs-collect-cluster \
            --namespace=amazon-cloudwatch \
            --name=fluent-bit \
            --role-name FluentBitRole \
            --attach-policy-arn=arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy \
            --approve || true
    fi
    
    # 确保命名空间存在
    kubectl create namespace amazon-cloudwatch --dry-run=client -o yaml | kubectl apply -f -
    
    # 部署Fluent-bit
    log_info "部署Fluent-bit配置..."
    envsubst < fluent-bit-config.yaml | kubectl apply -f -
    
    # 等待Fluent-bit就绪
    log_info "等待Fluent-bit Pod就绪..."
    kubectl wait --for=condition=ready pod -l k8s-app=fluent-bit -n amazon-cloudwatch --timeout=300s
    
    # 验证Fluent-bit状态
    log_info "验证Fluent-bit状态..."
    kubectl get pods -n amazon-cloudwatch
    kubectl logs -n amazon-cloudwatch -l k8s-app=fluent-bit --tail=10
    
    log_success "Fluent-bit部署完成"
}

# 显示访问信息
show_access_info() {
    log_info "获取访问信息..."
    
    # 获取ALB地址
    ALB_ADDRESS=$(kubectl get ingress logs-collect-ingress -n logs-collect -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "正在创建中...")
    
    echo ""
    log_success "=== 部署完成 ==="
    echo ""
    echo "📊 访问信息："
    echo "  🌐 测试应用: https://logs-collect.$DOMAIN_NAME"
    echo "  📈 OpenSearch Dashboard: https://$OPENSEARCH_ENDPOINT/_dashboards"
    echo "  👤 用户名: admin"
    echo "  🔑 密码: $OPENSEARCH_PASSWORD"
    echo ""
    echo "🔧 ALB信息："
    echo "  📍 ALB地址: $ALB_ADDRESS"
    echo ""
    echo "📋 后续步骤："
    echo "  1. 在Route53中添加CNAME记录："
    echo "     名称: logs-collect.$DOMAIN_NAME"
    echo "     值: $ALB_ADDRESS"
    echo ""
    echo "  2. 访问OpenSearch Dashboard配置索引模式"
    echo "  3. 查看实时日志数据"
    echo ""
    echo "🔍 验证命令："
    echo "  kubectl get pods -n logs-collect"
    echo "  kubectl get pods -n amazon-cloudwatch"
    echo "  kubectl logs -f -n logs-collect deployment/log-generator"
}

# 主函数
main() {
    echo "🚀 开始部署 Logs Collect 项目..."
    echo ""
    
    check_env_vars
    check_tools
    
    create_eks_cluster
    deploy_test_app
    deploy_alb_ingress
    create_opensearch_domain
    deploy_fluent_bit
    
    show_access_info
    
    log_success "🎉 所有组件部署完成！"
}

# 执行主函数
main "$@"
