# DynamoDB 自动扩展配置

本目录包含用于配置 DynamoDB 表自动扩展能力的脚本和说明。

## 自动扩展脚本

`configure-dynamodb-autoscaling.sh` 脚本用于为 DynamoDB 表配置自动扩展能力，设置目标利用率为 10%。

### 使用方法

1. 编辑脚本，将 `TABLE_NAME` 变量修改为你的 DynamoDB 表名
2. 根据需要调整 `MIN_CAPACITY` 和 `MAX_CAPACITY` 值
3. 确保已配置 AWS CLI 凭证
4. 运行脚本：

```bash
./configure-dynamodb-autoscaling.sh
```

### 配置说明

脚本配置了以下内容：

- 读取容量的自动扩展：目标利用率为 10%
- 写入容量的自动扩展：目标利用率为 10%
- 冷却时间：扩展和收缩操作的冷却时间均为 60 秒

## 通过 AWS 控制台配置

如果你更喜欢使用 AWS 控制台，可以按照以下步骤操作：

1. 登录 AWS 控制台
2. 导航到 DynamoDB 服务
3. 选择你的表
4. 点击"容量"选项卡
5. 在"自动扩展"部分，配置读取和写入容量的自动扩展
6. 设置目标利用率为 10%
7. 设置最小和最大容量单位
8. 保存设置

## 验证配置

配置完成后，可以使用以下命令验证自动扩展设置：

```bash
aws application-autoscaling describe-scalable-targets --service-namespace dynamodb --resource-ids "table/your-table-name"
aws application-autoscaling describe-scaling-policies --service-namespace dynamodb --resource-id "table/your-table-name"
```

## 压力测试

本目录包含用于对 DynamoDB 表进行压力测试的 Python 脚本 `dynamodb_load_test.py`。该脚本可以模拟多用户并发读写操作，用于测试 DynamoDB 表的性能和自动扩展能力。

### 测试脚本功能

- 模拟多用户并发写入广告点击数据到 DynamoDB 表
- 模拟多用户并发读取广告点击数据
- 支持独立配置读写线程数量和持续时间
- 支持 TPS (Transactions Per Second) 控制，可限制每秒事务数
- 生成约 2KB 大小的广告点击数据记录
- 详细的测试结果统计和报告
- 实时 TPS 监控和统计

### 数据结构

测试脚本将向 `first_dyn_table_new` 表写入以下结构的数据：

- 主键：userid (Number)
- 排序键：timestamp (Number)
- 其他字段：
  - click_time：点击时间
  - ad_id：广告ID
  - ad_type：广告类型（从预定义列表中随机选择）
  - ad_position：广告位置（从预定义列表中随机选择）
  - channel：渠道来源（从预定义列表中随机选择）
  - click_id：点击ID
  - click_url：点击URL
  - extra_data：额外数据（确保总记录大小约为2KB）

### 测试执行步骤

1. **配置 DynamoDB 表的自动扩展**

   首先，使用自动扩展配置脚本为表设置自动扩展能力：

   ```bash
   ./configure-dynamodb-autoscaling.sh
   ```

2. **验证自动扩展配置**

   确认自动扩展设置已正确应用：

   ```bash
   aws application-autoscaling describe-scalable-targets --service-namespace dynamodb --resource-ids "table/first_dyn_table_new" --region us-east-1
   aws application-autoscaling describe-scaling-policies --service-namespace dynamodb --resource-id "table/first_dyn_table_new" --region us-east-1
   ```

3. **运行压力测试**

   执行压力测试脚本，可以使用默认参数或自定义参数：

   ```bash
   # 使用默认参数运行测试（10个写入线程，5个读取线程，各持续5分钟）
   python3 dynamodb_load_test.py

   # 自定义参数运行测试
   python3 dynamodb_load_test.py --write-threads 20 --read-threads 10 --write-duration 10 --read-duration 5
   ```

4. **监控测试结果**

   在测试执行过程中，脚本会输出实时进度信息。测试完成后，将显示详细的测试结果统计，包括：
   - 总写入/读取项目数
   - 总执行时间
   - 写入/读取吞吐量（项目/秒）
   - 遇到的错误数量
   - TPS 统计信息（平均值、最大值、最小值）

5. **监控 AWS 控制台**

   在测试过程中，可以在 AWS 控制台监控 DynamoDB 表的以下指标：
   - 已消耗的读取/写入容量单位
   - 节流事件
   - 自动扩展活动
   - 延迟指标

### 测试脚本参数说明

```bash
python3 dynamodb_load_test.py [选项]
```

可用选项：
- `--table TABLE`：DynamoDB 表名（默认：first_dyn_table_new）
- `--region REGION`：AWS 区域（默认：us-east-1）
- `--write-threads N`：写入线程数（默认：10）
- `--read-threads N`：读取线程数（默认：5）
- `--write-duration M`：写入测试持续时间（分钟，默认：5）
- `--read-duration M`：读取测试持续时间（分钟，默认：5）
- `--batch-size N`：每批写入的项目数（默认：25）
- `--write-tps N`：目标写入 TPS (每秒事务数)，0 表示不限制（默认：0）
- `--read-tps N`：目标读取 TPS (每秒事务数)，0 表示不限制（默认：0）
- `--write-only`：仅运行写入测试
- `--read-only`：仅运行读取测试

### 测试场景示例

1. **高并发写入测试**

   ```bash
   python3 dynamodb_load_test.py --write-threads 50 --read-threads 0 --write-duration 5 --write-only
   ```

2. **高并发读取测试**

   ```bash
   python3 dynamodb_load_test.py --write-threads 0 --read-threads 50 --read-duration 5 --read-only
   ```

3. **混合读写测试**

   ```bash
   python3 dynamodb_load_test.py --write-threads 30 --read-threads 20 --write-duration 10 --read-duration 10
   ```

4. **长时间持续负载测试**

   ```bash
   python3 dynamodb_load_test.py --write-threads 15 --read-threads 10 --write-duration 30 --read-duration 30
   ```

5. **限制 TPS 的写入测试**

   ```bash
   python3 dynamodb_load_test.py --write-threads 20 --write-tps 100 --write-duration 5 --write-only
   ```
   这将使用 20 个线程进行写入测试，但总体写入速率不会超过 100 TPS。

6. **限制 TPS 的读取测试**

   ```bash
   python3 dynamodb_load_test.py --read-threads 30 --read-tps 200 --read-duration 5 --read-only
   ```
   这将使用 30 个线程进行读取测试，但总体读取速率不会超过 200 TPS。

7. **混合读写测试，同时限制 TPS**

   ```bash
   python3 dynamodb_load_test.py --write-threads 15 --read-threads 10 --write-tps 150 --read-tps 100 --write-duration 10 --read-duration 10
   ```
   这将同时进行读写测试，写入不超过 150 TPS，读取不超过 100 TPS。



| 对比维度 | AWS DynamoDB | 华为云Gemini Cassandra |
|---------|-------------|----------------------|
| 运维便利性 | • 完全托管服务，无需管理服务器<br>• 自动扩展能力<br>• 内置备份和恢复功能<br>• 全球表支持多区域部署<br>• 与AWS IAM无缝集成 | • 基于Apache Cassandra的托管服务<br>• 需要一定程度的配置和管理<br>• 版本升级和补丁需更多手动干预<br>• 备份恢复需更多手动配置<br>• 集群管理相对复杂 |
| SLA | • 99.999%可用性(单区域)<br>• 明确的读写延迟承诺<br>• 自动故障转移和恢复<br>• 透明的服务健康监控 | • 99.95%可用性<br>• 跨可用区部署提供高可用性<br>•故障转移需一定恢复时间<br>• 基本监控和告警功能 |
| 成本可预见性 | • 按需容量模式，按使用付费<br>• 预置容量模式可降低成本<br>• 自动扩展避免过度预置<br>• 透明的计费模型<br>• 完善的成本监控工具 | • 基于节点数量和规格计费<br>• 扩展可能导致成本突增<br>• 存储和计算资源捆绑计费<br>• 可能产生额外费用<br>• 成本优化需更多手动干预 |


| 对比维度 | Amazon DocumentDB | 华为云DDS MongoDB |
|---------|------------------|-----------------|
| 运维便利性 | • 完全托管的MongoDB兼容数据库服务<br>• 自动化补丁和版本管理<br>• 自动备份和时间点恢复功能<br>• 与AWS IAM无缝集成的安全管理<br>• 自动故障检测和恢复<br>• 简化的集群管理和扩展 | • 基于MongoDB的托管服务<br>• 提供一定程度的自动化管理<br>• 需要更多手动配置和监控<br>• 版本升级需要规划和手动干预<br>• 安全配置相对复杂<br>• 集群管理需要更多专业知识 |
| SLA | • 99.99%可用性承诺<br>• 跨可用区自动复制<br>• 快速故障转移机制<br>• 持续监控和自动恢复<br>• 透明的服务健康状态报告 | • 99.95%可用性(集群版)<br>• 跨可用区部署<br>• 故障转移需要一定恢复时间<br>• 基本监控和告警功能<br>• 需要更多手动干预确保高可用 |
| 成本可预见性 | • 基于实例类型和存储的透明定价<br>• 可预测的按小时计费模式<br>• 存储自动扩展，按使用量付费<br>• AWS Cost Explorer提供成本分析和预测<br>• 预留实例可降低长期成本 | • 基于实例规格和数量的计费<br>• 存储和计算捆绑定价<br>• 扩展可能导致成本突增<br>• 容量规划不当可能导致资源浪费<br>• 成本优化需要更多专业知识 |
| 容量 | • 存储自动扩展至64TB<br>• 计算资源可独立扩展<br>• 读取副本可扩展至15个<br>• 无需停机即可扩展实例<br>• 支持高吞吐量和低延迟操作 | • 存储容量有预设上限<br>• 扩展需要添加新节点<br>• 存储和计算能力耦合<br>• 扩展过程可能影响服务<br>• 需要预先规划集群容量 |
