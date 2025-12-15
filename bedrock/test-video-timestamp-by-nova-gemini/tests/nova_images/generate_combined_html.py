#!/usr/bin/env python3
import json

# Load both results
with open('ocr_results.json', 'r', encoding='utf-8') as f:
    nova_data = json.load(f)
with open('gemini_ocr_results.json', 'r', encoding='utf-8') as f:
    gemini_data = json.load(f)

model_config = {
    "amazon.nova-pro-v1:0": {"name": "Nova Pro", "icon": "🟣", "class": "nova-pro", "card": "pro"},
    "amazon.nova-lite-v1:0": {"name": "Nova Lite", "icon": "🔵", "class": "nova-lite", "card": "lite"},
    "amazon.nova-2-lite-v1:0": {"name": "Nova Lite 2", "icon": "🟠", "class": "nova-lite2", "card": "lite2"},
    "gemini-2.5-flash": {"name": "Gemini 2.5 Flash", "icon": "🟢", "class": "gemini", "card": "gemini"}
}

image_names = {
    "20251023-174349.jpg": "口红广告 (英文)",
    "20251023-174354.jpg": "聊天界面 (泰文)",
    "20251023-174358.jpg": "Y.O.U 品牌 (泰文)",
    "20251023-174403.jpg": "内衣广告 (越南文)",
    "20251023-174407.jpg": "贷款广告 (英文/菲律宾)",
    "2616eed4e3594d6be70b8c26dd5beacd.jpg": "视频截图 (中文)",
    "4fbef4f903f72041c65c82138baf43fb.jpg": "京东广告 (中文)",
    "8bf2b7238d5802bdb630f29a6c4321a9.jpg": "直播截图 (中文)"
}

nova_models = ["amazon.nova-pro-v1:0", "amazon.nova-lite-v1:0", "amazon.nova-2-lite-v1:0"]
all_models = nova_models + ["gemini-2.5-flash"]

# Merge summaries
summary = {**nova_data['summary'], **gemini_data['summary']}

def escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')

# Generate summary cards
summary_html = ""
for m in all_models:
    if m not in summary: continue
    s = summary[m]
    cfg = model_config[m]
    summary_html += f'''<div class="summary-card {cfg['card']}">
        <h3>{cfg['icon']} {cfg['name']}</h3>
        <div class="stats">总 Tokens: <strong>{s['total_tokens']:,}</strong><br>
        总耗时: <strong>{s['total_time_ms']/1000:.1f}s</strong><br>
        平均: {s['avg_tokens']} tokens / {s['avg_time_ms']}ms<br>
        响应: {s['min_time_ms']}ms ~ {s['max_time_ms']}ms</div>
    </div>'''

# Merge rounds - use Nova's structure, add Gemini results
merged_rounds = []
for ri, nova_round in enumerate(nova_data['rounds']):
    gemini_round = gemini_data['rounds'][ri] if ri < len(gemini_data['rounds']) else None
    merged_images = []
    
    for nova_img in nova_round['images']:
        filename = nova_img['s3_uri'].split('/')[-1]
        merged_results = dict(nova_img['results'])
        
        # Find matching Gemini result
        if gemini_round:
            for g_img in gemini_round['images']:
                g_filename = g_img['s3_uri'].split('/')[-1]
                if g_filename == filename:
                    merged_results.update(g_img['results'])
                    break
        
        merged_images.append({'s3_uri': nova_img['s3_uri'], 'results': merged_results})
    
    merged_rounds.append({'round': nova_round['round'], 'images': merged_images})

# Generate tabs
tabs_html = "".join([f'<button class="round-tab{" active" if i==0 else ""}" onclick="switchRound({i})">第 {r["round"]} 轮</button>' for i, r in enumerate(merged_rounds)])

# Generate results
results_html = ""
for ri, round_data in enumerate(merged_rounds):
    images_html = ""
    for img in round_data['images']:
        filename = img['s3_uri'].split('/')[-1]
        img_name = image_names.get(filename, filename)
        
        models_html = ""
        for m in all_models:
            r = img['results'].get(m, {})
            if not r.get('success'): continue
            cfg = model_config[m]
            models_html += f'''<div class="model-result {cfg['class']}">
                <div class="model-name">{cfg['icon']} {cfg['name']} <span class="metrics">{r['usage']['total_tokens']} tokens | {r['response_time_ms']}ms</span></div>
                <div class="extracted-text">{escape(r['extracted_text'])}</div>
                <div class="tokens"><span>输入: {r['usage']['input_tokens']}</span><span>输出: {r['usage']['output_tokens']}</span><span class="time">⏱ {r['response_time_ms']}ms</span></div>
            </div>'''
        
        images_html += f'''<div class="image-section">
            <div class="image-header">📷 {filename} - {img_name}</div>
            <div class="image-content">
                <div class="image-preview"><img src="images/{filename}" onclick="showModal(this.src)" alt="{img_name}"></div>
                <div class="models-compare">{models_html}</div>
            </div>
        </div>'''
    
    results_html += f'<div class="round-content{" active" if ri==0 else ""}">{images_html}</div>'

# Find best models
fastest = min(all_models, key=lambda m: summary.get(m, {}).get('avg_time_ms', float('inf')))
cheapest = min(all_models, key=lambda m: summary.get(m, {}).get('avg_tokens', float('inf')))

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova vs Gemini OCR 对比</title>
    <style>
        *{{box-sizing:border-box;margin:0;padding:0}}
        body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5;padding:20px}}
        h1{{text-align:center;margin-bottom:20px;color:#232f3e}}
        .config-section{{background:#232f3e;color:white;padding:20px;border-radius:8px;margin-bottom:20px}}
        .config-section h2{{margin-bottom:15px;font-size:18px}}
        .config-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:15px}}
        .config-item{{background:rgba(255,255,255,0.1);padding:12px;border-radius:4px}}
        .config-item label{{font-size:12px;color:#aaa;display:block;margin-bottom:5px}}
        .config-item code{{background:rgba(0,0,0,0.3);padding:8px;border-radius:4px;display:block;font-size:13px;white-space:pre-wrap;word-break:break-all}}
        .summary{{display:flex;justify-content:center;gap:20px;margin-bottom:20px;flex-wrap:wrap}}
        .summary-card{{background:white;padding:15px 25px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);min-width:200px}}
        .summary-card.pro{{border-top:4px solid #7b68ee}}
        .summary-card.lite{{border-top:4px solid #00a1c9}}
        .summary-card.lite2{{border-top:4px solid #ff9900}}
        .summary-card.gemini{{border-top:4px solid #34a853}}
        .summary-card h3{{margin-bottom:10px;text-align:center;font-size:14px}}
        .summary-card .stats{{font-size:12px;color:#666;line-height:1.8}}
        .conclusion{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:20px;border-radius:8px;margin-bottom:20px}}
        .conclusion h2{{margin-bottom:15px}}
        .conclusion ul{{margin-left:20px;line-height:1.8}}
        .round-tabs{{display:flex;gap:5px;margin-bottom:20px;background:white;padding:10px;border-radius:8px}}
        .round-tab{{padding:10px 20px;border:none;background:#eee;border-radius:4px;cursor:pointer;font-size:14px}}
        .round-tab.active{{background:#232f3e;color:white}}
        .round-content{{display:none}}
        .round-content.active{{display:block}}
        .image-section{{background:white;margin-bottom:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);overflow:hidden}}
        .image-header{{background:#232f3e;color:white;padding:12px 15px;font-weight:bold;font-size:14px}}
        .image-content{{display:flex;flex-wrap:wrap}}
        .image-preview{{flex:0 0 250px;padding:15px;border-right:1px solid #eee}}
        .image-preview img{{width:100%;border-radius:4px;cursor:pointer}}
        .models-compare{{flex:1;min-width:300px}}
        .model-result{{padding:12px 15px;border-bottom:1px solid #eee}}
        .model-result:last-child{{border-bottom:none}}
        .model-name{{font-weight:bold;color:#232f3e;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:5px;font-size:14px}}
        .model-name .metrics{{font-size:11px;color:#666;font-weight:normal}}
        .extracted-text{{background:#f9f9f9;padding:10px;border-radius:4px;font-size:13px;line-height:1.5;white-space:pre-wrap;word-break:break-word;max-height:150px;overflow-y:auto}}
        .tokens{{display:inline-flex;gap:6px;font-size:10px;color:#888;margin-top:6px;flex-wrap:wrap}}
        .tokens span{{background:#eee;padding:2px 6px;border-radius:10px}}
        .tokens .time{{background:#e8f5e9;color:#2e7d32}}
        .nova-pro{{border-left:4px solid #7b68ee}}
        .nova-lite{{border-left:4px solid #00a1c9}}
        .nova-lite2{{border-left:4px solid #ff9900}}
        .gemini{{border-left:4px solid #34a853}}
        .modal{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;justify-content:center;align-items:center}}
        .modal img{{max-width:90%;max-height:90%}}
        .modal.active{{display:flex}}
        @media(max-width:768px){{.image-preview{{flex:0 0 100%;border-right:none;border-bottom:1px solid #eee}}}}
    </style>
</head>
<body>
    <h1>🔍 Amazon Nova vs Google Gemini OCR 对比</h1>
    
    <div class="config-section">
        <h2>⚙️ 测试配置</h2>
        <div class="config-grid">
            <div class="config-item"><label>测试模型</label><code>Amazon: Nova Pro, Nova Lite, Nova Lite 2
Google: Gemini 2.5 Flash</code></div>
            <div class="config-item"><label>测试轮数</label><code>3 轮 × 8 张图片 × 4 个模型</code></div>
            <div class="config-item"><label>图片类型</label><code>多语言: 英文、泰文、越南文、中文、菲律宾文</code></div>
        </div>
    </div>
    
    <div class="summary">{summary_html}</div>
    
    <div class="conclusion">
        <h2>📊 测试总结</h2>
        <ul>
            <li><strong>最快响应:</strong> {model_config[fastest]['icon']} {model_config[fastest]['name']} (平均 {summary[fastest]['avg_time_ms']}ms)</li>
            <li><strong>最省 Token:</strong> {model_config[cheapest]['icon']} {model_config[cheapest]['name']} (平均 {summary[cheapest]['avg_tokens']} tokens)</li>
            <li><strong>Gemini 特点:</strong> 输出更详细的场景描述，但响应时间较长</li>
            <li><strong>Nova 特点:</strong> 响应快速，输出简洁，适合纯文本提取</li>
        </ul>
    </div>
    
    <div class="round-tabs">{tabs_html}</div>
    {results_html}
    
    <div class="modal" id="modal" onclick="this.classList.remove('active')">
        <img id="modalImg" src="" alt="放大图片">
    </div>
    
    <script>
        function showModal(src) {{ document.getElementById('modalImg').src = src; document.getElementById('modal').classList.add('active'); }}
        function switchRound(i) {{ document.querySelectorAll('.round-tab').forEach((t,j) => t.classList.toggle('active', i===j)); document.querySelectorAll('.round-content').forEach((c,j) => c.classList.toggle('active', i===j)); }}
    </script>
</body>
</html>'''

with open('combined_comparison.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Generated combined_comparison.html")
