// Load data from JSON file
fetch('ocr_results.json')
    .then(r => r.json())
    .then(data => {
        renderConfig(data.config);
        renderSummary(data.summary);
        renderConclusion(data.summary);
        renderTabs(data.rounds);
        renderResults(data.rounds);
    });

const modelConfig = {
    "amazon.nova-pro-v1:0": { name: "Nova Pro", icon: "🟣", class: "nova-pro", cardClass: "pro" },
    "amazon.nova-lite-v1:0": { name: "Nova Lite", icon: "🔵", class: "nova-lite", cardClass: "lite" },
    "amazon.nova-2-lite-v1:0": { name: "Nova Lite 2", icon: "🟠", class: "nova-lite2", cardClass: "lite2" }
};

const imageNames = {
    "20251023-174349.jpg": "口红广告 (英文)",
    "20251023-174354.jpg": "聊天界面 (泰文)",
    "20251023-174358.jpg": "Y.O.U 品牌 (泰文)",
    "20251023-174403.jpg": "内衣广告 (越南文)",
    "20251023-174407.jpg": "贷款广告 (英文/菲律宾)"
};

const modelOrder = ["amazon.nova-pro-v1:0", "amazon.nova-lite-v1:0", "amazon.nova-2-lite-v1:0"];

function showModal(src) {
    document.getElementById('modalImg').src = src;
    document.getElementById('modal').classList.add('active');
}

function renderConfig(config) {
    document.getElementById('config').innerHTML = `
        <h2>⚙️ 测试配置</h2>
        <div class="config-grid">
            <div class="config-item">
                <label>Prompt (提示词)</label>
                <code>${config.prompt}</code>
            </div>
            <div class="config-item">
                <label>Inference Config (推理参数)</label>
                <code>${JSON.stringify(config.inference_config, null, 2)}</code>
            </div>
            <div class="config-item">
                <label>测试轮数</label>
                <code>${config.num_rounds} 轮 × ${config.images.length} 张图片 × ${config.models.length} 个模型 = ${config.num_rounds * config.images.length * config.models.length} 次调用</code>
            </div>
            <div class="config-item">
                <label>测试模型</label>
                <code>${config.models.join('\n')}</code>
            </div>
        </div>`;
}

function renderSummary(summary) {
    document.getElementById('summary').innerHTML = modelOrder.map(modelId => {
        const s = summary[modelId];
        const cfg = modelConfig[modelId];
        return `<div class="summary-card ${cfg.cardClass}">
            <h3>${cfg.icon} ${cfg.name}</h3>
            <div class="stats">
                总 Tokens: <strong>${s.total_tokens.toLocaleString()}</strong><br>
                总耗时: <strong>${(s.total_time_ms/1000).toFixed(1)}s</strong><br>
                平均: ${s.avg_tokens} tokens / ${s.avg_time_ms}ms<br>
                响应时间: ${s.min_time_ms}ms ~ ${s.max_time_ms}ms
            </div>
        </div>`;
    }).join('');
}

function renderConclusion(summary) {
    const fastest = modelOrder.reduce((a, b) => summary[a].avg_time_ms < summary[b].avg_time_ms ? a : b);
    const cheapest = modelOrder.reduce((a, b) => summary[a].avg_tokens < summary[b].avg_tokens ? a : b);
    const mostStable = modelOrder.reduce((a, b) => 
        (summary[a].max_time_ms - summary[a].min_time_ms) < (summary[b].max_time_ms - summary[b].min_time_ms) ? a : b);
    
    document.getElementById('conclusion').innerHTML = `
        <h2>📊 测试总结</h2>
        <ul>
            <li><strong>最快响应:</strong> ${modelConfig[fastest].icon} ${modelConfig[fastest].name} (平均 ${summary[fastest].avg_time_ms}ms)</li>
            <li><strong>最省 Token:</strong> ${modelConfig[cheapest].icon} ${modelConfig[cheapest].name} (平均 ${summary[cheapest].avg_tokens} tokens)</li>
            <li><strong>最稳定:</strong> ${modelConfig[mostStable].icon} ${modelConfig[mostStable].name} (波动 ${summary[mostStable].max_time_ms - summary[mostStable].min_time_ms}ms)</li>
            <li><strong>OCR 准确性:</strong> Nova Lite 2 在多语言(泰文、越南文)识别上表现更好，输出格式更规范(保留换行)</li>
            <li><strong>性价比推荐:</strong> Nova Lite 2 - 速度最快、Token消耗最少、输出稳定</li>
        </ul>`;
}

function renderTabs(rounds) {
    document.getElementById('tabs').innerHTML = rounds.map((r, i) => 
        `<button class="round-tab ${i === 0 ? 'active' : ''}" onclick="switchRound(${i})">第 ${r.round} 轮</button>`
    ).join('');
}

function switchRound(index) {
    document.querySelectorAll('.round-tab').forEach((t, i) => t.classList.toggle('active', i === index));
    document.querySelectorAll('.round-content').forEach((c, i) => c.classList.toggle('active', i === index));
}

function renderResults(rounds) {
    document.getElementById('results').innerHTML = rounds.map((round, roundIndex) => {
        const imagesHtml = round.images.map(img => {
            const filename = img.s3_uri.split('/').pop();
            const imageName = imageNames[filename] || filename;
            
            const modelsHtml = modelOrder.map(modelId => {
                const r = img.results[modelId];
                const cfg = modelConfig[modelId];
                if (!r || !r.success) return '';
                return `<div class="model-result ${cfg.class}">
                    <div class="model-name">
                        ${cfg.icon} ${cfg.name}
                        <span class="metrics">${r.usage.total_tokens} tokens | ${r.response_time_ms}ms</span>
                    </div>
                    <div class="extracted-text">${escapeHtml(r.extracted_text)}</div>
                    <div class="tokens">
                        <span>输入: ${r.usage.input_tokens}</span>
                        <span>输出: ${r.usage.output_tokens}</span>
                        <span class="time">⏱ ${r.response_time_ms}ms</span>
                    </div>
                </div>`;
            }).join('');
            
            return `<div class="image-section">
                <div class="image-header">📷 ${filename} - ${imageName}</div>
                <div class="image-content">
                    <div class="image-preview">
                        <img src="images/${filename}" onclick="showModal(this.src)" alt="${imageName}">
                    </div>
                    <div class="models-compare">${modelsHtml}</div>
                </div>
            </div>`;
        }).join('');
        
        return `<div class="round-content ${roundIndex === 0 ? 'active' : ''}">${imagesHtml}</div>`;
    }).join('');
}

function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
}
