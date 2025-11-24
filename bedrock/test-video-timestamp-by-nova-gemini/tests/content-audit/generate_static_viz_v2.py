"""
生成包含所有资源的单文件静态可视化页面
"""

import json

# 读取测试结果
with open('audit_test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取 HTML
with open('audit_viz_v2.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 读取 CSS
with open('audit_viz_v2_style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

# 读取 JS
with open('audit_viz_v2.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# 替换 CSS 链接为内联样式
html_content = html_content.replace(
    '<link rel="stylesheet" href="audit_viz_v2_style.css">',
    f'<style>\n{css_content}\n    </style>'
)

# 替换 JS 引用为内联脚本，并嵌入数据
fetch_code = """fetch('audit_test_results.json')
    .then(response => response.json())
    .then(data => {
        initializeDashboard(data);
    })
    .catch(error => {
        console.error('Error loading data:', error);
        document.querySelector('.container').innerHTML = '<div style="text-align:center;padding:50px;color:#dc3545;">加载数据失败</div>';
    });"""

embedded_code = f"""// 嵌入的测试数据
const embeddedData = {json.dumps(data, ensure_ascii=False, indent=4)};

// 直接使用嵌入的数据
initializeDashboard(embeddedData);"""

js_content = js_content.replace(fetch_code, embedded_code)

html_content = html_content.replace(
    '<script src="audit_viz_v2.js"></script>',
    f'<script>\n{js_content}\n    </script>'
)

# 保存单文件版本
with open('audit_results_visualization_v2.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ 静态可视化页面生成完成！")
print("📄 文件: audit_results_visualization_v2.html")
print("💡 可以直接在浏览器中打开此文件")
print("\n功能特性:")
print("  ✓ 显示所有 4 个测试视频信息")
print("  ✓ 基于期望值计算准确率")
print("  ✓ 详细对比实际输出与期望值")
print("  ✓ 可展开查看完整响应内容")
