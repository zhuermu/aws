# 🚀 EKS 日志采集系统 (Logs Collect)

> 基于 AWS EKS 1.33 + OpenSearch + Fluent-bit 的完整日志采集解决方案，提供交互式网页测试界面

## 📋 项目概述

这是一个在 AWS EKS 上部署的现代化日志采集系统，集成了测试应用、ALB 负载均衡、OpenSearch 可视化和 Fluent-bit 日志采集，并提供直观的网页界面进行日志测试和监控。

### 🎯 核心特性

- **🏗️ EKS 1.33 集群**: 最新 Kubernetes 版本，自动模式部署
- **🌐 交互式网页界面**: 现代化响应式设计，实时日志触发和监控
- **📊 完整日志链路**: 从应用生成到存储分析的端到端解决方案
- **🔒 生产级安全**: HTTPS、加密存储、RBAC 权限控制
- **⚡ 一键部署**: 自动化脚本，简化部署流程

## 🏗️ 系统架构

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   用户访问      │───▶│     ALB      │───▶│   测试应用      │
│  (网页界面)     │    │   (HTTPS)    │    │ (log-generator) │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
                                                     ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  OpenSearch     │◀───│  Fluent-bit  │◀───│   容器日志      │
│   Dashboard     │    │   (采集器)   │    │   (JSON格式)    │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### 核心组件

| 组件 | 版本 | 功能 |
|------|------|------|
| **EKS 集群** | 1.33 | Kubernetes 容器编排平台 |
| **测试应用** | Nginx + 网页界面 | 日志生成和交互式测试 |
| **ALB Ingress** | AWS Load Balancer | HTTPS 访问和域名路由 |
| **OpenSearch** | 2.19 | 日志存储、搜索和可视化 |
| **Fluent-bit** | 最新版 | 日志采集和转发 |

## 📁 项目结构

```
logs-collect/
├── 📋 配置文件
│   ├── cluster-config.yaml          # EKS集群配置
│   ├── test-app-deployment.yaml     # 测试应用部署（含网页界面）
│   ├── ingress.yaml                 # ALB Ingress配置
│   ├── opensearch-config.yaml       # OpenSearch域配置
│   └── fluent-bit-config.yaml       # Fluent-bit日志采集配置
├── 🚀 部署脚本
│   ├── deploy.sh                    # 自动部署脚本
│   ├── cleanup.sh                   # 资源清理脚本
│   └── verify.sh                    # 验证脚本
├── 📚 文档
│   └── README.md                    # 项目文档（本文件）
└── 🔧 配置
    ├── sample.env                   # 环境变量配置模板
    ├── .env                         # 环境变量配置（需要填入实际值）
    └── .gitignore                   # Git忽略配置
```

## 🚀 快速开始

### 前置要求

1. **安装必要工具**
```bash
# 安装 eksctl (最新版本)
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# 安装 kubectl (1.33兼容版本)
curl -LO "https://dl.k8s.io/release/v1.33.0/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 安装 helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

2. **配置 AWS CLI**
```bash
aws configure
```

3. **配置环境变量**
```bash
# 复制配置模板
cp sample.env .env

# 编辑 .env 文件，填入你的实际配置值
vim .env

# 加载环境变量
source .env
```

### 一键部署

```bash
# 克隆项目
git clone <repository-url>
cd logs-collect

# 执行部署
chmod +x deploy.sh
./deploy.sh

# 验证部署
./verify.sh
```

### 访问系统

部署完成后，你可以通过以下地址访问系统：

- **🌐 测试应用网页**: https://logs-collect.{your-domain}
- **🔍 OpenSearch Dashboard**: https://{opensearch-endpoint}/_dashboards
- **👤 登录信息**: admin / {your-password}

## 🌐 网页测试界面

### 功能特性

#### 📊 系统状态监控
实时显示系统运行状态和配置信息：
- ✅ 应用运行状态
- 🏗️ 集群信息 (logs-collect-cluster)
- 🔧 Kubernetes 版本 (1.33)
- 📡 日志采集状态 (Fluent-bit)
- 🔍 存储状态 (OpenSearch)

#### 🎮 交互式日志触发

| 功能 | 描述 | API 端点 |
|------|------|----------|
| **✅ 正常日志** | 生成 INFO 级别日志，测试基本采集功能 | `/api/trigger-log` |
| **⚠️ 警告日志** | 生成 WARN 级别日志，测试警告处理 | `/api/trigger-warning` |
| **❌ 错误日志** | 生成 ERROR 级别日志，测试错误处理 | `/api/trigger-error` |
| **📦 批量日志** | 一次生成多条日志，测试高并发场景 | `/api/bulk-logs` |

#### 📝 实时日志显示
- 网页实时显示触发的日志
- 不同级别日志颜色区分
- 时间戳和详细信息展示
- 支持日志清空功能

### 界面特色

- **🎨 现代化设计**: 渐变背景、卡片式布局、阴影效果
- **📱 响应式布局**: 完美适配桌面和移动设备
- **⚡ 实时更新**: 状态和日志实时刷新
- **🎯 视觉反馈**: 按钮动画、加载状态、颜色编码
- **👥 用户友好**: 直观操作界面、清晰状态显示

## 🔧 配置详解

### 环境变量说明

项目提供了 `sample.env` 配置模板，包含所有必需的环境变量和详细说明。

#### 配置步骤
```bash
# 1. 复制配置模板
cp sample.env .env

# 2. 编辑配置文件，填入实际值
vim .env

# 3. 加载环境变量
source .env
```

#### 核心变量

| 变量名 | 描述 | 示例 |
|--------|------|------|
| `AWS_ACCOUNT_ID` | AWS 账户 ID | `123456789012` |
| `DOMAIN_NAME` | 你的域名 | `example.com` |
| `CERTIFICATE_ARN` | SSL 证书 ARN | `arn:aws:acm:us-east-1:...` |
| `OPENSEARCH_PASSWORD` | OpenSearch 管理员密码 | `MySecurePassword123!` |

#### 获取配置值
```bash
# 获取 AWS 账户 ID
aws sts get-caller-identity --query Account --output text

# 列出 SSL 证书
aws acm list-certificates --region us-east-1

# 验证域名解析
nslookup logs-collect.your-domain.com
```

### 核心配置文件

#### 1. cluster-config.yaml
EKS 集群配置，使用 1.33 版本和自动模式部署：
```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: logs-collect-cluster
  region: us-east-1
  version: "1.33"
```

#### 2. test-app-deployment.yaml
测试应用配置，包含完整网页界面：
- **Namespace**: logs-collect
- **Deployment**: log-generator (2副本)
- **ConfigMaps**: nginx-config, web-content, log-script
- **Service**: ClusterIP 服务

#### 3. fluent-bit-config.yaml
日志采集配置：
- **DaemonSet**: 在每个节点运行
- **采集范围**: logs-collect 命名空间
- **输出目标**: OpenSearch
- **日志格式**: JSON 结构化

## 📊 日志格式

### Nginx 访问日志 (JSON)
```json
{
  "timestamp": "2025-07-31T08:50:10+00:00",
  "remote_addr": "192.168.49.192",
  "request": "GET /api/trigger-log HTTP/1.1",
  "status": "200",
  "app_name": "log-generator",
  "log_level": "info",
  "request_id": "req-05849ac43dab19c604d37c34048ee2d7"
}
```

### 应用业务日志 (JSON)
```json
{
  "timestamp": "2025-07-31T08:49:45.123Z",
  "level": "INFO",
  "app": "log-generator",
  "message": "User authentication successful",
  "request_id": "req-1722420585-12345",
  "cluster": "logs-collect-cluster",
  "namespace": "logs-collect"
}
```

## 🧪 测试场景

### 1. 基础功能测试
1. 访问网页界面，确认系统状态正常
2. 点击"生成INFO日志"按钮
3. 观察实时日志输出
4. 在 OpenSearch 中验证日志收集

### 2. 多级别日志测试
1. 依次触发 INFO、WARN、ERROR 日志
2. 观察不同级别的颜色区分
3. 验证 Fluent-bit 正确采集所有级别

### 3. 高并发测试
1. 点击"生成批量日志"按钮
2. 观察系统并发处理能力
3. 检查日志完整性

### 4. API 自动化测试
```bash
# 批量测试 API 端点
for i in {1..10}; do
  curl -s https://logs-collect.{your-domain}/api/trigger-log
  curl -s https://logs-collect.{your-domain}/api/trigger-warning
  curl -s https://logs-collect.{your-domain}/api/trigger-error
  sleep 1
done
```

## 🔍 故障排除

### 常见问题及解决方案

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 网页无法访问 | Ingress 配置错误 | 检查域名和证书配置 |
| 日志未采集 | Fluent-bit 配置问题 | 检查 OpenSearch 连接 |
| 集群创建失败 | 权限或配额不足 | 检查 IAM 权限和服务配额 |

### 调试命令

```bash
# 检查集群状态
kubectl get nodes
kubectl get pods --all-namespaces

# 检查应用状态
kubectl get pods -n logs-collect
kubectl logs -n logs-collect deployment/log-generator

# 检查 Fluent-bit 状态
kubectl get pods -n amazon-cloudwatch
kubectl logs -n amazon-cloudwatch daemonset/fluent-bit

# 测试 API 端点
curl -s https://logs-collect.{your-domain}/api/health
```

## 🔒 安全特性

### 网络安全
- ✅ HTTPS 强制重定向
- ✅ SSL 证书集成
- ✅ CORS 配置
- ✅ Security Groups 限制

### 数据保护
- ✅ 传输加密 (TLS 1.2+)
- ✅ 静态数据加密
- ✅ 节点间通信加密
- ✅ IMDSv2 强制令牌

### 访问控制
- ✅ IAM 角色和策略
- ✅ Kubernetes RBAC
- ✅ OpenSearch 内置认证
- ✅ 最小权限原则

## 📈 性能优化

### 资源配置
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi"
    cpu: "100m"
```

### 扩展建议
- **水平扩展**: 增加副本数和节点数
- **垂直扩展**: 升级实例类型
- **多可用区**: 配置跨 AZ 部署
- **缓存优化**: 调整 Fluent-bit 缓冲配置

## 🔧 自定义配置

### 修改网页内容
```bash
kubectl edit configmap web-content -n logs-collect
kubectl rollout restart deployment/log-generator -n logs-collect
```

### 修改日志格式
```bash
kubectl edit configmap log-script -n logs-collect
kubectl rollout restart deployment/log-generator -n logs-collect
```

## 🧹 清理资源

```bash
chmod +x cleanup.sh
./cleanup.sh
```

⚠️ **注意**: 清理操作将删除所有创建的 AWS 资源，请确认后执行。

## 🎉 项目优势

### 🔧 易于部署
- 一键部署脚本
- 自动化配置管理
- 详细错误处理
- 环境变量模板

### 📊 功能完整
- 端到端日志采集链路
- 交互式网页测试界面
- 实时可视化展示
- 生产级安全配置

### 🛡️ 安全可靠
- 多层安全防护
- 加密传输和存储
- 最小权限原则
- 现代化安全标准

### 🔄 易于维护
- 清晰的项目结构
- 完整的文档说明
- 便捷的验证工具
- 模块化配置管理

---

## 📞 支持与贡献

如果你在使用过程中遇到问题或有改进建议，欢迎：

- 📝 提交 Issue
- 🔧 发起 Pull Request  
- 📖 完善文档
- 🧪 添加测试用例

---

**🎯 项目状态**: ✅ 生产就绪  
**📅 最后更新**: 2025-07-31  
**👨‍💻 维护者**: AWS Q Assistant

🎉 **享受使用 EKS 日志采集测试系统！**

这个系统提供了完整的日志采集解决方案，从交互式网页界面到后端的 EKS、Fluent-bit 和 OpenSearch 集成。通过网页界面，你可以轻松测试各种日志场景，验证整个日志采集链路的功能和性能。
