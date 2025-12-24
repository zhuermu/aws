# 📁 Fluent-bit 日志路径映射关系

## 🔗 路径对应关系图

### 1. 容器内应用日志路径
```
应用容器内部:
├── /var/log/nginx/access.log     # Nginx 访问日志
├── /var/log/nginx/error.log      # Nginx 错误日志
├── /dev/stdout                   # 标准输出 (应用日志)
└── /dev/stderr                   # 标准错误
```

### 2. 节点文件系统路径
```
Kubernetes 节点:
├── /var/log/containers/          # 容器日志符号链接目录
│   └── {pod-name}_{namespace}_{container-name}-{container-id}.log
│       → 指向 /var/log/pods/...
│
├── /var/log/pods/               # 实际日志文件存储
│   └── {namespace}_{pod-name}_{pod-uid}/
│       └── {container-name}/
│           ├── 0.log           # 第一个日志文件
│           ├── 1.log           # 轮转后的日志文件
│           └── ...
│
└── /var/lib/docker/containers/  # Docker 容器日志 (已弃用)
```

### 3. Fluent-bit 采集路径
```
Fluent-bit 配置:
├── Path: /var/log/containers/*logs-collect*.log
├── 实际读取: /var/log/pods/{namespace}_{pod}_{uid}/{container}/N.log
└── Tag: application.var.log.containers.{filename}
```

## 📊 具体示例映射

### 当前系统中的路径映射

| 应用组件 | 容器内路径 | 节点符号链接路径 | 实际文件路径 |
|----------|------------|------------------|--------------|
| **log-generator** | `/dev/stdout` | `/var/log/containers/log-generator-f544bf65d-8jw8j_logs-collect_log-generator-{id}.log` | `/var/log/pods/logs-collect_log-generator-f544bf65d-8jw8j_{uid}/log-generator/1.log` |
| **mq-test-app** | `/dev/stdout` | `/var/log/containers/mq-test-app-648d677cd7-l9ksx_logs-collect_mq-test-app-{id}.log` | `/var/log/pods/logs-collect_mq-test-app-648d677cd7-l9ksx_{uid}/mq-test-app/1.log` |

## 🔍 路径解析规则

### 文件名格式解析
```
容器日志文件名格式:
{pod-name}_{namespace}_{container-name}-{container-id}.log

示例:
log-generator-f544bf65d-8jw8j_logs-collect_log-generator-2abdae505dc9eb10630afb3bc26f3f0e2cea02093604a441d08d5d9b13909998.log

解析结果:
├── Pod Name: log-generator-f544bf65d-8jw8j
├── Namespace: logs-collect  
├── Container Name: log-generator
└── Container ID: 2abdae505dc9eb10630afb3bc26f3f0e2cea02093604a441d08d5d9b13909998
```

### Fluent-bit Tag 格式
```
Tag 格式: application.var.log.containers.{filename}

示例:
application.var.log.containers.log-generator-f544bf65d-8jw8j_logs-collect_log-generator-2abdae505dc9eb10630afb3bc26f3f0e2cea02093604a441d08d5d9b13909998.log
```

## 🛠️ 其他应用日志路径对应

### 如何为其他应用添加日志采集

#### 1. 修改 Fluent-bit 采集路径
```yaml
[INPUT]
    Name                tail
    Tag                 application.*
    # 当前只采集 logs-collect 命名空间
    Path                /var/log/containers/*logs-collect*.log
    
    # 如果要采集其他命名空间，可以修改为:
    # Path                /var/log/containers/*{namespace}*.log
    # 或采集所有:
    # Path                /var/log/containers/*.log
```

#### 2. 添加命名空间过滤
```yaml
[FILTER]
    Name                grep
    Match               application.*
    Regex               kubernetes.namespace_name ^(logs-collect|other-namespace)$
```

#### 3. 不同应用的路径示例

| 应用类型 | 命名空间 | 容器日志路径示例 |
|----------|----------|------------------|
| **Web 应用** | `web-app` | `/var/log/containers/nginx-xxx_web-app_nginx-{id}.log` |
| **数据库** | `database` | `/var/log/containers/mysql-xxx_database_mysql-{id}.log` |
| **监控系统** | `monitoring` | `/var/log/containers/prometheus-xxx_monitoring_prometheus-{id}.log` |
| **消息队列** | `messaging` | `/var/log/containers/rabbitmq-xxx_messaging_rabbitmq-{id}.log` |

## 🔧 路径配置最佳实践

### 1. 按命名空间分类采集
```yaml
# 为不同命名空间创建不同的 INPUT
[INPUT]
    Name                tail
    Tag                 web.*
    Path                /var/log/containers/*web-app*.log

[INPUT]
    Name                tail  
    Tag                 db.*
    Path                /var/log/containers/*database*.log
```

### 2. 使用标签区分应用
```yaml
[FILTER]
    Name                modify
    Match               web.*
    Add                 app_type web-application
    Add                 log_category frontend

[FILTER]
    Name                modify
    Match               db.*
    Add                 app_type database
    Add                 log_category backend
```

### 3. 路径信息丰富化
```yaml
[FILTER]
    Name                lua
    Match               *
    script              /fluent-bit/etc/enrich_path.lua
    call                add_path_metadata
```

## 📈 监控和调试

### 查看当前采集的文件
```bash
# 检查 Fluent-bit 正在监控的文件
kubectl exec -n amazon-cloudwatch fluent-bit-xxx -- ls -la /var/log/containers/

# 查看实际的日志文件
kubectl exec -n amazon-cloudwatch fluent-bit-xxx -- ls -la /var/log/pods/
```

### 验证路径映射
```bash
# 查看符号链接指向
kubectl exec -n amazon-cloudwatch fluent-bit-xxx -- readlink /var/log/containers/{filename}.log

# 检查文件内容
kubectl exec -n amazon-cloudwatch fluent-bit-xxx -- tail -f /var/log/containers/{filename}.log
```

## 🎯 总结

1. **容器日志** → **节点符号链接** → **实际文件** → **Fluent-bit 采集** → **OpenSearch**
2. 每个容器的日志都有唯一的路径标识
3. Fluent-bit 通过文件路径可以准确识别日志来源
4. 路径信息被添加到日志记录中，便于溯源和分析
5. 可以通过修改采集路径来扩展到其他应用和命名空间
