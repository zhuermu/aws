# 登陆docker
aws ecr get-login-password --region region_id | docker login --username AWS --password-stdin your_accountid.dkr.ecr.us-east-1.amazonaws.com

# 代码仓库
https://github.com/zhuermu/TEN-Agent.git

# 在本地构建镜像  在目录TEN-Agent/Dockerfile
docker build -t dev/ten_agent_build .

# 打tag
docker tag dev/ten_agent_build:latest your_accountid.dkr.ecr.us-east-1.amazonaws.com/dev/ten_agent_build:latest
# 推送镜像
docker push your_accountid.dkr.ecr.us-east-1.amazonaws.com/dev/ten_agent_build:latest

# 部署集群
eksctl create cluster -f cluster-config.yaml

# 创建命名空间
kubectl create namespace ten-framework --save-config

# 创建部署deployment
kubectl apply -n ten-framework -f deployment.k8s.yaml

# 创建服务service 和 ingress
kubectl apply -n ten-framework -f service.k8s.yaml

## 其他常用命令
### 进入容器
kubectl exec -it ten-agent-demo-{容器ID} -n ten-framework -- sh
kubectl exec -it ten-agent-build-{容器ID} -n ten-framework -- bash

### 查看容器日志
kubectl logs my-pod -c container-name
kubectl logs ten-agent-build-{容器ID} -n ten-framework -f

### 删除部署
kubectl delete deployment ten-agent-build -n ten-framework

### 查看资源
kubectl get ingress -n  ten-framework
### 查看部署
kubectl get Deployment -n  ten-framework
### 查看服务
kubectl get service -n  ten-framework
### 查看pod
kubectl get pod -n  ten-framework
