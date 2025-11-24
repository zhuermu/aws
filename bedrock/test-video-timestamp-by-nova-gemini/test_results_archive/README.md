# 测试结果归档

本文件夹包含历史测试结果和中间测试数据。

## 📁 文件说明

### 当前测试结果
- **test_results.json** - 最新的完整测试结果（已移至根目录）
- **test_report.md** - 最新的测试报告

### 历史测试结果
- **test_results0.json** - 早期测试结果
- **test_results.json_nova_lite-v1** - Nova Lite V1 专项测试
- **test_results.json-nova-lite-v2-vdo-1** - Nova Lite V2 Video 1 测试
- **test_results.json-lite-v2-timeout** - Nova Lite V2 超时测试

## 📊 查看结果

### 方式 1: 使用可视化界面（推荐）
```bash
# 从根目录启动服务器
cd ..
python serve.py

# 浏览器访问
# http://localhost:8000/test_results_visualization.html
```

### 方式 2: 查看 JSON 文件
```bash
# 格式化查看
cat test_results.json | python -m json.tool | less

# 或使用 jq
cat test_results.json | jq '.'
```

### 方式 3: 查看 Markdown 报告
```bash
cat test_report.md
```

## 🔄 更新可视化数据

如果需要查看归档的测试结果：

```bash
# 1. 复制历史结果到根目录
cp test_results_archive/test_results0.json ../test_results.json

# 2. 更新可视化数据
cd ..
python update_visualization.py

# 3. 启动服务器查看
python serve.py
```

## 📝 测试日期

- **test_results.json** - 2024-11-17 (最新)
- **test_results0.json** - 早期版本
- **其他文件** - 中间测试版本

## 🗑️ 清理说明

这些文件保留用于：
- 对比不同版本的测试结果
- 分析模型性能变化趋势
- 问题排查和回溯

如果不再需要，可以安全删除此文件夹。

---

**归档日期**: 2024-11-17
