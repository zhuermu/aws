import pandas as pd
import re
from collections import Counter, defaultdict
from datetime import datetime
import os
import math

# 定义日志文件路径
log_file = 'file_path.2025-07-04-05.fc99a15b'
output_file = 'cloudfront_analysis_with_regions.xlsx'

# 定义 CloudFront 日志字段
fields = [
    'date', 'time', 'x-edge-location', 'sc-bytes', 'c-ip', 'cs-method', 'cs(Host)', 
    'cs-uri-stem', 'sc-status', 'cs(Referer)', 'cs(User-Agent)', 'cs-uri-query', 
    'cs(Cookie)', 'x-edge-result-type', 'x-edge-request-id', 'x-host-header', 
    'cs-protocol', 'cs-bytes', 'time-taken', 'x-forwarded-for', 'ssl-protocol', 
    'ssl-cipher', 'x-edge-response-result-type', 'cs-protocol-version', 'fle-status', 
    'fle-encrypted-fields', 'c-port', 'time-to-first-byte', 'x-edge-detailed-result-type', 
    'sc-content-type', 'sc-content-len', 'sc-range-start', 'sc-range-end'
]

# 定义 CloudFront 边缘节点代码到区域的映射
edge_node_regions = {
    # Asia Pacific
    'MNL': 'Manila, Philippines (Asia Pacific)',
    'HKG': 'Hong Kong, China (Asia Pacific)',
    'CGK': 'Jakarta, Indonesia (Asia Pacific)',
    'SIN': 'Singapore (Asia Pacific)',
    'TPE': 'Taipei, Taiwan (Asia Pacific)',
    'BKK': 'Bangkok, Thailand (Asia Pacific)',
    'KUL': 'Kuala Lumpur, Malaysia (Asia Pacific)',
    'CCU': 'Kolkata, India (Asia Pacific)',
    
    # North America
    'LOS': 'Los Angeles, USA (North America)',
    'ATL': 'Atlanta, USA (North America)',
    
    # Europe
    'AMS': 'Amsterdam, Netherlands (Europe)',
    'MRS': 'Marseille, France (Europe)',
    'LHR': 'London, UK (Europe)',
    'FRA': 'Frankfurt, Germany (Europe)',
    'MXP': 'Milan, Italy (Europe)',
    
    # Middle East
    'JED': 'Jeddah, Saudi Arabia (Middle East)',
    'DXB': 'Dubai, UAE (Middle East)',
    'MCT': 'Muscat, Oman (Middle East)',
    'BAH': 'Bahrain (Middle East)',
    
    # Africa
    'CAI': 'Cairo, Egypt (Africa)',
    
    # South America
    'SCL': 'Santiago, Chile (South America)'
}

def get_region_from_edge_location(edge_location):
    """从边缘节点代码获取区域信息"""
    # 提取位置代码（前3个字母）
    location_code = edge_location[:3] if len(edge_location) >= 3 else edge_location
    
    # 查找区域
    return edge_node_regions.get(location_code, 'Unknown Region')

def parse_log_file(file_path):
    """解析 CloudFront 日志文件到 pandas DataFrame"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            
            # 按制表符分割行
            parts = line.strip().split('\t')
            
            # 为此日志条目创建字典
            if len(parts) == len(fields):
                entry = dict(zip(fields, parts))
                data.append(entry)
    
    return pd.DataFrame(data)

def format_file_size(size_bytes):
    """将字节格式化为人类可读的文件大小"""
    if pd.isna(size_bytes) or size_bytes == 0:
        return "0 B"
    
    size_bytes = float(size_bytes)
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_name[i]}"

def get_file_size_range(size_bytes):
    """获取文件大小范围分类"""
    if pd.isna(size_bytes):
        return "Unknown"
    
    size_bytes = float(size_bytes)
    
    if size_bytes < 100 * 1024:  # < 100KB
        return "< 100KB"
    elif size_bytes < 500 * 1024:  # 100KB - 500KB
        return "100KB - 500KB"
    elif size_bytes < 1024 * 1024:  # 500KB - 1MB
        return "500KB - 1MB"
    else:  # > 1MB
        return "1MB - 5MB"

def analyze_logs():
    """分析 CloudFront 日志并创建 Excel 报告"""
    print("解析日志文件...")
    df = parse_log_file(log_file)
    
    # 转换数据类型
    df['sc-bytes'] = pd.to_numeric(df['sc-bytes'], errors='coerce')
    df['time-taken'] = pd.to_numeric(df['time-taken'], errors='coerce')
    
    # 添加区域信息
    df['region'] = df['x-edge-location'].apply(get_region_from_edge_location)
    
    # 创建 Excel 写入器
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # 表1: 摘要统计
        print("创建表1: 摘要统计...")
        total_requests = len(df)
        slow_requests = len(df[df['time-taken'] > 1.5])
        very_slow_requests = len(df[df['time-taken'] > 30])
        
        slow_percentage = (slow_requests / total_requests) * 100 if total_requests > 0 else 0
        very_slow_percentage = (very_slow_requests / total_requests) * 100 if total_requests > 0 else 0
        
        summary_data = {
            '指标': ['总请求数', '慢请求数(>1.5秒)', '慢请求百分比', '超慢请求数(>30秒)', '超慢请求百分比'],
            '数值': [
                total_requests,
                slow_requests,
                f"{slow_percentage:.2f}%",
                very_slow_requests,
                f"{very_slow_percentage:.2f}%"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='摘要', index=False)
        
        # 表2: 慢请求详情
        print("创建表2: 慢请求详情...")
        slow_df = df[df['time-taken'] > 1.5].copy()
        
        if not slow_df.empty:
            # 按处理时间降序排序
            slow_df = slow_df.sort_values('time-taken', ascending=False)
            
            # 准备详细信息
            slow_details = []
            for i, (_, row) in enumerate(slow_df.iterrows(), 1):
                slow_details.append({
                    '序号': i,
                    '请求ID': row['x-edge-request-id'],
                    '日志的文件名': os.path.basename(log_file),
                    '请求的文件大小': format_file_size(row['sc-bytes']),
                    '请求日期': row['date'],
                    '请求时间': row['time'],
                    '处理时间(秒)': f"{float(row['time-taken']):.3f}",
                    '缓存状态': row['x-edge-result-type'],
                    '边缘节点': row['x-edge-location'],
                    '区域': row['region'],
                    '请求协议': f"{row['cs-protocol']} {row['cs-protocol-version']}",
                    '请求方法': row['cs-method'],
                    'URL': row['cs-uri-stem'],
                    '状态码': row['sc-status'],
                    '客户端IP': row['c-ip'],
                    '用户代理': row['cs(User-Agent)']
                })
            
            slow_details_df = pd.DataFrame(slow_details)
            slow_details_df.to_excel(writer, sheet_name='慢请求详情', index=False)
        else:
            # 如果没有慢请求，创建一个空表
            empty_df = pd.DataFrame(columns=[
                '序号', '请求ID', '日志的文件名', '请求的文件大小', '请求日期', '请求时间', 
                '处理时间(秒)', '缓存状态', '边缘节点', '区域', '请求协议', '请求方法', 'URL', 
                '状态码', '客户端IP', '用户代理'
            ])
            empty_df.to_excel(writer, sheet_name='慢请求详情', index=False)
        
        # 表3: 缓存状态统计
        print("创建表3: 缓存状态统计...")
        cache_stats = df['x-edge-result-type'].value_counts().reset_index()
        cache_stats.columns = ['缓存状态', '请求数']
        cache_stats['百分比'] = (cache_stats['请求数'] / total_requests * 100).apply(lambda x: f"{x:.2f}%")
        
        cache_stats.to_excel(writer, sheet_name='缓存状态', index=False)
        
        # 表4: 边缘节点统计
        print("创建表4: 边缘节点统计...")
        edge_stats = df.groupby(['x-edge-location', 'region']).size().reset_index(name='请求数')
        edge_stats['百分比'] = (edge_stats['请求数'] / total_requests * 100).apply(lambda x: f"{x:.2f}%")
        edge_stats = edge_stats.sort_values('请求数', ascending=False)
        edge_stats.columns = ['边缘节点', '区域', '请求数', '百分比']
        
        edge_stats.to_excel(writer, sheet_name='边缘节点统计', index=False)
        
        # 表5: 区域统计
        print("创建表5: 区域统计...")
        region_stats = df.groupby('region').size().reset_index(name='请求数')
        region_stats['百分比'] = (region_stats['请求数'] / total_requests * 100).apply(lambda x: f"{x:.2f}%")
        region_stats = region_stats.sort_values('请求数', ascending=False)
        region_stats.columns = ['区域', '请求数', '百分比']
        
        region_stats.to_excel(writer, sheet_name='区域统计', index=False)
        
        # 表6: 文件大小统计
        print("创建表6: 文件大小统计...")
        df['文件大小范围'] = df['sc-bytes'].apply(get_file_size_range)
        size_stats = df['文件大小范围'].value_counts().reset_index()
        size_stats.columns = ['文件大小范围', '请求数']
        size_stats['百分比'] = (size_stats['请求数'] / total_requests * 100).apply(lambda x: f"{x:.2f}%")
        
        # 确保所有范围都存在
        all_ranges = ["< 100KB", "100KB - 500KB", "500KB - 1MB", "1MB - 5MB"]
        for size_range in all_ranges:
            if size_range not in size_stats['文件大小范围'].values:
                size_stats = pd.concat([size_stats, pd.DataFrame({
                    '文件大小范围': [size_range],
                    '请求数': [0],
                    '百分比': ['0.00%']
                })], ignore_index=True)
        
        # 按照指定顺序排序
        size_stats['排序'] = size_stats['文件大小范围'].apply(lambda x: all_ranges.index(x) if x in all_ranges else 999)
        size_stats = size_stats.sort_values('排序').drop('排序', axis=1)
        
        size_stats.to_excel(writer, sheet_name='文件大小统计', index=False)
    
    print(f"分析完成。结果已保存到 {output_file}")

if __name__ == "__main__":
    analyze_logs()
