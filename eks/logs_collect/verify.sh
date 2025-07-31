#!/bin/bash

# Logs Collect 项目验证脚本
# 验证部署状态和配置正确性

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

# 检查EKS集群状态
check_eks_cluster() {
    log_info "检查EKS集群状态..."
    
    if kubectl cluster-info &> /dev/null; then
        CLUSTER_NAME=$(kubectl config current-context | cut -d'/' -f2)
        log_success "EKS集群连接正常: $CLUSTER_NAME"
        
        # 检查节点状态
        NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
        READY_NODES=$(kubectl get nodes --no-headers | grep -c Ready || echo "0")
        
        echo "  节点总数: $NODE_COUNT"
        echo "  就绪节点: $READY_NODES"
        
        if [ "$READY_NODES" -eq "$NODE_COUNT" ] && [ "$NODE_COUNT" -gt 0 ]; then
            log_success "所有节点就绪"
        else
            log_warning "部分节点未就绪"
        fi
    else
        log_error "无法连接到EKS集群"
        return 1
    fi
}

# 检查测试应用状态
check_test_app() {
    log_info "检查测试应用状态..."
    
    if kubectl get namespace logs-collect &> /dev/null; then
        log_success "logs-collect命名空间存在"
        
        # 检查Pod状态
        POD_COUNT=$(kubectl get pods -n logs-collect --no-headers 2>/dev/null | wc -l)
        RUNNING_PODS=$(kubectl get pods -n logs-collect --no-headers 2>/dev/null | grep -c Running || echo "0")
        
        echo "  Pod总数: $POD_COUNT"
        echo "  运行中Pod: $RUNNING_PODS"
        
        if [ "$RUNNING_PODS" -gt 0 ]; then
            log_success "测试应用运行正常"
            
            # 显示Pod详情
            kubectl get pods -n logs-collect
        else
            log_warning "测试应用未运行"
        fi
    else
        log_warning "logs-collect命名空间不存在"
    fi
}

# 检查ALB Ingress状态
check_alb_ingress() {
    log_info "检查ALB Ingress状态..."
    
    if kubectl get ingress logs-collect-ingress -n logs-collect &> /dev/null; then
        log_success "Ingress存在"
        
        # 获取ALB地址
        ALB_ADDRESS=$(kubectl get ingress logs-collect-ingress -n logs-collect -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
        
        if [ -n "$ALB_ADDRESS" ]; then
            log_success "ALB地址: $ALB_ADDRESS"
        else
            log_warning "ALB地址未分配（可能正在创建中）"
        fi
        
        # 检查AWS Load Balancer Controller
        if kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller &> /dev/null; then
            CONTROLLER_PODS=$(kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller --no-headers | grep -c Running || echo "0")
            if [ "$CONTROLLER_PODS" -gt 0 ]; then
                log_success "AWS Load Balancer Controller运行正常"
            else
                log_warning "AWS Load Balancer Controller未运行"
            fi
        else
            log_warning "AWS Load Balancer Controller未安装"
        fi
    else
        log_warning "Ingress不存在"
    fi
}

# 检查OpenSearch域状态
check_opensearch() {
    log_info "检查OpenSearch域状态..."
    
    DOMAIN_NAME="logs-collect-domain"
    REGION="us-east-1"
    
    if aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION &> /dev/null; then
        DOMAIN_STATUS=$(aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION --query 'DomainStatus.Processing' --output text)
        ENDPOINT=$(aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION --query 'DomainStatus.Endpoint' --output text)
        
        if [ "$DOMAIN_STATUS" = "false" ]; then
            log_success "OpenSearch域运行正常"
            echo "  端点: https://$ENDPOINT"
            echo "  Dashboard: https://$ENDPOINT/_dashboards"
        else
            log_warning "OpenSearch域正在处理中"
        fi
    else
        log_warning "OpenSearch域不存在"
    fi
}

# 检查Fluent-bit状态
check_fluent_bit() {
    log_info "检查Fluent-bit状态..."
    
    if kubectl get namespace amazon-cloudwatch &> /dev/null; then
        log_success "amazon-cloudwatch命名空间存在"
        
        # 检查Fluent-bit Pod状态
        if kubectl get daemonset fluent-bit -n amazon-cloudwatch &> /dev/null; then
            DESIRED=$(kubectl get daemonset fluent-bit -n amazon-cloudwatch -o jsonpath='{.status.desiredNumberScheduled}')
            READY=$(kubectl get daemonset fluent-bit -n amazon-cloudwatch -o jsonpath='{.status.numberReady}')
            
            echo "  期望Pod数: $DESIRED"
            echo "  就绪Pod数: $READY"
            
            if [ "$READY" = "$DESIRED" ] && [ "$READY" -gt 0 ]; then
                log_success "Fluent-bit运行正常"
            else
                log_warning "Fluent-bit部分Pod未就绪"
            fi
            
            # 显示Pod状态
            kubectl get pods -n amazon-cloudwatch -l k8s-app=fluent-bit
        else
            log_warning "Fluent-bit DaemonSet不存在"
        fi
    else
        log_warning "amazon-cloudwatch命名空间不存在"
    fi
}

# 检查日志流
check_log_flow() {
    log_info "检查日志流..."
    
    # 检查测试应用是否生成日志
    if kubectl get pods -n logs-collect -l app=log-generator &> /dev/null; then
        log_info "获取测试应用日志样本..."
        kubectl logs -n logs-collect -l app=log-generator --tail=5 | head -3
        log_success "测试应用正在生成日志"
    else
        log_warning "测试应用Pod不存在"
    fi
    
    # 检查Fluent-bit是否正常工作
    if kubectl get pods -n amazon-cloudwatch -l k8s-app=fluent-bit &> /dev/null; then
        log_info "检查Fluent-bit日志..."
        ERROR_COUNT=$(kubectl logs -n amazon-cloudwatch -l k8s-app=fluent-bit --tail=50 | grep -i error | wc -l)
        
        if [ "$ERROR_COUNT" -eq 0 ]; then
            log_success "Fluent-bit运行无错误"
        else
            log_warning "Fluent-bit有 $ERROR_COUNT 个错误"
        fi
    fi
}

# 生成验证报告
generate_report() {
    echo ""
    log_info "=== 验证报告 ==="
    echo ""
    
    echo "📊 组件状态概览："
    echo "  🔧 EKS集群: $(kubectl cluster-info &> /dev/null && echo "✅ 正常" || echo "❌ 异常")"
    echo "  🚀 测试应用: $(kubectl get pods -n logs-collect -l app=log-generator &> /dev/null && echo "✅ 运行中" || echo "❌ 未运行")"
    echo "  🌐 ALB Ingress: $(kubectl get ingress logs-collect-ingress -n logs-collect &> /dev/null && echo "✅ 已配置" || echo "❌ 未配置")"
    echo "  🔍 OpenSearch: $(aws opensearch describe-domain --domain-name logs-collect-domain --region us-east-1 &> /dev/null && echo "✅ 运行中" || echo "❌ 不存在")"
    echo "  📝 Fluent-bit: $(kubectl get daemonset fluent-bit -n amazon-cloudwatch &> /dev/null && echo "✅ 运行中" || echo "❌ 未部署")"
    echo ""
    
    # 获取访问信息
    if kubectl get ingress logs-collect-ingress -n logs-collect &> /dev/null; then
        ALB_ADDRESS=$(kubectl get ingress logs-collect-ingress -n logs-collect -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "正在创建中...")
        echo "🌐 访问信息："
        echo "  应用地址: $ALB_ADDRESS"
        if [ -n "$DOMAIN_NAME" ]; then
            echo "  域名: https://logs-collect.$DOMAIN_NAME"
        fi
    fi
    
    if aws opensearch describe-domain --domain-name logs-collect-domain --region us-east-1 &> /dev/null; then
        OPENSEARCH_ENDPOINT=$(aws opensearch describe-domain --domain-name logs-collect-domain --region us-east-1 --query 'DomainStatus.Endpoint' --output text 2>/dev/null || echo "获取中...")
        echo "  OpenSearch: https://$OPENSEARCH_ENDPOINT/_dashboards"
    fi
    
    echo ""
    echo "🔧 常用命令："
    echo "  查看所有Pod: kubectl get pods --all-namespaces"
    echo "  查看应用日志: kubectl logs -f -n logs-collect deployment/log-generator"
    echo "  查看Fluent-bit日志: kubectl logs -f -n amazon-cloudwatch daemonset/fluent-bit"
}

# 主函数
main() {
    echo "🔍 开始验证 Logs Collect 项目状态..."
    echo ""
    
    check_eks_cluster
    echo ""
    check_test_app
    echo ""
    check_alb_ingress
    echo ""
    check_opensearch
    echo ""
    check_fluent_bit
    echo ""
    check_log_flow
    
    generate_report
    
    log_success "🎉 验证完成！"
}

# 执行主函数
main "$@"
