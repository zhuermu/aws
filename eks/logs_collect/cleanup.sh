#!/bin/bash

# Logs Collect 项目清理脚本
# 清理所有创建的AWS资源

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

# 确认清理操作
confirm_cleanup() {
    echo "⚠️  这将删除以下资源："
    echo "  - EKS集群: logs-collect-cluster"
    echo "  - OpenSearch域: logs-collect-domain"
    echo "  - IAM角色和策略"
    echo "  - 所有相关的Kubernetes资源"
    echo ""
    read -p "确定要继续吗？(yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "清理操作已取消"
        exit 0
    fi
}

# 清理Kubernetes资源
cleanup_k8s_resources() {
    log_info "清理Kubernetes资源..."
    
    # 删除Ingress（这会删除ALB）
    kubectl delete ingress logs-collect-ingress -n logs-collect --ignore-not-found=true
    
    # 删除测试应用
    kubectl delete namespace logs-collect --ignore-not-found=true
    
    # 删除Fluent-bit
    kubectl delete namespace amazon-cloudwatch --ignore-not-found=true
    
    log_success "Kubernetes资源清理完成"
}

# 清理OpenSearch域
cleanup_opensearch() {
    log_info "清理OpenSearch域..."
    
    DOMAIN_NAME="logs-collect-domain"
    REGION="us-east-1"
    
    if aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION >/dev/null 2>&1; then
        log_info "删除OpenSearch域 $DOMAIN_NAME..."
        aws opensearch delete-domain --domain-name $DOMAIN_NAME --region $REGION
        log_success "OpenSearch域删除请求已提交"
    else
        log_warning "OpenSearch域 $DOMAIN_NAME 不存在"
    fi
}

# 清理IAM角色和策略
cleanup_iam() {
    log_info "清理IAM角色和策略..."
    
    # 清理ALB Controller角色
    aws iam detach-role-policy --role-name AmazonEKSLoadBalancerControllerRole --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID:-123456789012}:policy/AWSLoadBalancerControllerIAMPolicy || true
    aws iam delete-role --role-name AmazonEKSLoadBalancerControllerRole || true
    aws iam delete-policy --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID:-123456789012}:policy/AWSLoadBalancerControllerIAMPolicy || true
    
    # 清理Fluent-bit角色
    aws iam detach-role-policy --role-name FluentBitRole --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy || true
    aws iam delete-role --role-name FluentBitRole || true
    
    log_success "IAM资源清理完成"
}

# 清理EKS集群
cleanup_eks_cluster() {
    log_info "清理EKS集群..."
    
    CLUSTER_NAME="logs-collect-cluster"
    REGION="us-east-1"
    
    if eksctl get cluster --name $CLUSTER_NAME --region $REGION >/dev/null 2>&1; then
        log_info "删除EKS集群 $CLUSTER_NAME（这可能需要10-15分钟）..."
        eksctl delete cluster --name $CLUSTER_NAME --region $REGION --wait
        log_success "EKS集群删除完成"
    else
        log_warning "EKS集群 $CLUSTER_NAME 不存在"
    fi
}

# 清理本地文件
cleanup_local_files() {
    log_info "清理临时文件..."
    
    rm -f iam_policy.json
    
    log_success "临时文件清理完成"
}

# 显示清理后的状态
show_cleanup_status() {
    echo ""
    log_success "=== 清理完成 ==="
    echo ""
    echo "📋 已清理的资源："
    echo "  ✅ Kubernetes资源（Ingress、Namespace、Pods等）"
    echo "  ✅ OpenSearch域（删除请求已提交）"
    echo "  ✅ IAM角色和策略"
    echo "  ✅ EKS集群"
    echo "  ✅ 临时文件"
    echo ""
    echo "⚠️  注意事项："
    echo "  - OpenSearch域删除可能需要额外时间完成"
    echo "  - 请检查AWS控制台确认所有资源已删除"
    echo "  - 如果有手动创建的Route53记录，请手动删除"
    echo ""
    echo "🔍 验证命令："
    echo "  aws opensearch list-domain-names --region us-east-1"
    echo "  eksctl get cluster --region us-east-1"
}

# 主函数
main() {
    echo "🧹 开始清理 Logs Collect 项目资源..."
    echo ""
    
    confirm_cleanup
    
    cleanup_k8s_resources
    cleanup_opensearch
    cleanup_iam
    cleanup_eks_cluster
    cleanup_local_files
    
    show_cleanup_status
    
    log_success "🎉 资源清理完成！"
}

# 执行主函数
main "$@"
