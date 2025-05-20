# redshift 实例选择

## Redshift Serverless(无服务 Redshift)

## Provisioned Redshift（预留 Redshift 集群）
### 评估维度
- What is the estimated storage space needed by your data warehouse? 评估数据仓库所需的存储空间
- How much data do you query at one time? 一次查询多少数据，数据是时序数据还是非时序数据
  - My data is time based： My Choose if the data is added in time order to my data warehouse. For example, my sales data is added each month.
  - My data is not time based：Choose if the data doesn’t have a time dimension. For example, list the parts in my inventory by geographic region.
  - How many months of data does your data warehouse contain? 你的数据仓库包含多少个月的数据
  - How many months of data do you frequently query in your workload? 你的工作负载中经常查询多少个月的数据

### 样例
需求：容量 1TB，数据基于时间序列，包含 36 个月的数据，经常查询 12 个月的数据
**Calculated configuration summary**
Change your estimates to recalculate the configuration summary.
**ra3.xlplus | 2 nodes**
High performance with scalable managed storage
**Compute**
4 vCPU (gen 3) / node x 2 = 8 vCPU
**Estimated on-demand compute price**
$19,026.72/year
$1.086/node/hour
**Estimated reserved (1 year)**
$12,748.004/year
$0.364/node/hour
33% discount
**Estimated reserved (3 year)**
$7,516.005/year
$0.214/node/hour
60% discount
**Managed storage capacity**
Up to 32 TB x 2 nodes = 64 TB
$294.912/year (1TB)
$0.024/GB/month

## 同步RDS数据库到Redshift
参考文档：https://aws.amazon.com/cn/blogs/big-data/getting-started-guide-for-near-real-time-operational-analytics-using-amazon-aurora-zero-etl-integration-with-amazon-redshift/
1. 在RDS选择要迁移的实例
2. 在实例详情页选择“Zero-ETL integrations“ tab
3. 点击 “Create zero-ETL integration”按钮
4. 选择数据源 RDS 数据库
   - 这里可能需要fix RDS 数据库参数重启数据库
   - 可以设置同步filter 选择要同步的数据源 exclude: foodb.*, include: foodb.tbl, include: foodb./table_\d+/
5. 选择目标 Redshift 集群， 这里可能需要fix Redshift 集群参数重启集群
   - 注意⚠️： 这里自动fix没有设置 Redshift 集群的数据库名称，需要手动到Redshit 的 integrations tab 设置 Zero-ETL integrations 数据库名称
6. 由于redshift 语法时兼容PostgreSQL，直接使用mysql语法部分不兼容需要手动修改
7. redshift 首次查询会比较慢，二次查询类似语句会快非常多

## Redshift 性能优化原理
https://aws.amazon.com/cn/blogs/big-data/fast-and-predictable-performance-with-serverless-compilation-using-amazon-redshift/

## 数据类型差异
https://docs.aws.amazon.com/zh_cn/AmazonRDS/latest/AuroraUserGuide/zero-etl.querying.html#zero-etl.data-type-mapping