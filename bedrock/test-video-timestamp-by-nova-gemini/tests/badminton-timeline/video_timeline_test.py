"""
视频时间线理解测试 - 多模型对比
测试 Amazon Nova 和 Google Gemini 模型对羽毛球比赛视频的理解能力
"""

import boto3
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import google.generativeai as genai
from pathlib import Path

# 配置
BEDROCK_REGION = "us-east-1"
VIDEO_1_S3 = "s3://bedrock-video-generation-us-east-1-pi8hu9/agents/batball.mov"
VIDEO_2_S3 = "s3://bedrock-video-generation-us-east-1-pi8hu9/agents/1cut2-5-small.mov"
VIDEO_1_LOCAL = "video/video-1-person.mov"
VIDEO_2_LOCAL = "video/video-2-match.mov"

PROMPT = """Analyze this badminton video and identify all rallies from serve to dead ball. For each rally, provide the start and end timestamps along with the reason the rally ended in the following JSON format:

{"segments": [
{"start": "00:05", "end": "00:12", "reason": "shuttlecock out of bounds"},
{"start": "00:15", "end": "00:23", "reason": "net fault"}
...
]}

Process the entire video from beginning to end. Use MM:SS format for timestamps. This video is a 5-minute long video.

Common badminton dead ball reasons include:
- shuttlecock out of bounds
- net fault (shuttlecock hits net)
- shuttlecock lands on wrong side
- double hit
- smash winner
- drop shot winner
- clear out of bounds
- service fault
- let (replay point)
- unforced error

**Requirements:**
- ACCURATE timestamps within 00:00 to 05:00
- Output JSON format ONLY

Focus on identifying the exact moment each rally begins (serve contact) and ends (shuttlecock becomes dead)."""

class VideoTimelineTest:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        self.results = {}
        
    def test_nova_lite_v1(self, video_s3_uri: str, video_name: str) -> Dict[str, Any]:
        """测试 amazon.nova-lite-v1:0"""
        print(f"\n测试 Nova Lite v1 - {video_name}...")
        
        model_id = "amazon.nova-lite-v1:0"
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "video": {
                                "format": "mov",
                                "source": {"s3Location": {"uri": video_s3_uri}}
                            }
                        },
                        {"text": PROMPT}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 2048,
                "temperature": 0,
                "topP": 1.0,
            }
        }
        
        start_time = time.time()
        try:
            response = self.bedrock.converse(
                modelId=model_id,
                **request_body
            )
            elapsed_time = time.time() - start_time
            
            result_text = response['output']['message']['content'][0]['text']
            
            return {
                "model": model_id,
                "video": video_name,
                "success": True,
                "response": result_text,
                "elapsed_time": elapsed_time,
                "input_tokens": response['usage']['inputTokens'],
                "output_tokens": response['usage']['outputTokens']
            }
        except Exception as e:
            return {
                "model": model_id,
                "video": video_name,
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time
            }
    
    def test_nova_2_lite(self, video_s3_uri: str, video_name: str, use_reasoning: bool = False) -> Dict[str, Any]:
        """测试 amazon.nova-2-lite-v1:0 (支持 reasoning 和非 reasoning 模式)"""
        mode_label = "Reasoning" if use_reasoning else "Standard"
        print(f"\n测试 Nova 2 Lite ({mode_label}) - {video_name}...")
        
        model_id = "amazon.nova-2-lite-v1:0"
        
        # Reasoning 模式需要更多 tokens
        max_tokens = 65535 if use_reasoning else 2000
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "video": {
                                "format": "mov",
                                "source": {"s3Location": {"uri": video_s3_uri}}
                            }
                        },
                        {"text": PROMPT}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": 0,
                "topP": 1.0,
            }
        }
        
        # 如果启用 reasoning 模式，添加配置
        if use_reasoning:
            request_body["additionalModelRequestFields"] = {
                "reasoningConfig": {
                    "type": "enabled",
                    "maxReasoningEffort": "low"
                }
            }
        
        start_time = time.time()
        try:
            # Reasoning 模式需要使用流式 API
            if use_reasoning:
                response = self.bedrock.converse_stream(
                    modelId=model_id,
                    **request_body
                )
                
                # 收集流式响应
                result_text = ""
                reasoning_text = ""
                input_tokens = 0
                output_tokens = 0
                
                for event in response['stream']:
                    if 'contentBlockDelta' in event:
                        delta = event['contentBlockDelta']['delta']
                        if 'text' in delta:
                            result_text += delta['text']
                        if 'reasoningText' in delta:
                            reasoning_text += delta['reasoningText']
                    
                    if 'metadata' in event:
                        usage = event['metadata'].get('usage', {})
                        input_tokens = usage.get('inputTokens', 0)
                        output_tokens = usage.get('outputTokens', 0)
                
                elapsed_time = time.time() - start_time
                
                model_label = f"{model_id} (reasoning=low)"
                result = {
                    "model": model_label,
                    "video": video_name,
                    "success": True,
                    "response": result_text,
                    "elapsed_time": elapsed_time,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
                
                if reasoning_text:
                    result["reasoning"] = reasoning_text
                
                return result
            else:
                # 标准模式使用普通 converse
                response = self.bedrock.converse(
                    modelId=model_id,
                    **request_body
                )
                elapsed_time = time.time() - start_time
                
                content_blocks = response['output']['message']['content']
                result_text = ""
                
                for block in content_blocks:
                    if 'text' in block:
                        result_text += block['text']
                
                return {
                    "model": model_id,
                    "video": video_name,
                    "success": True,
                    "response": result_text,
                    "elapsed_time": elapsed_time,
                    "input_tokens": response['usage']['inputTokens'],
                    "output_tokens": response['usage']['outputTokens']
                }
            
        except Exception as e:
            model_label = f"{model_id} (reasoning=low)" if use_reasoning else model_id
            return {
                "model": model_label,
                "video": video_name,
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time
            }
    
    def test_nova_pro_v1(self, video_s3_uri: str, video_name: str) -> Dict[str, Any]:
        """测试 amazon.nova-pro-v1:0"""
        print(f"\n测试 Nova Pro v1 - {video_name}...")
        
        model_id = "amazon.nova-pro-v1:0"
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "video": {
                                "format": "mov",
                                "source": {"s3Location": {"uri": video_s3_uri}}
                            }
                        },
                        {"text": PROMPT}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 3000,
                "temperature": 0.1
            }
        }
        
        start_time = time.time()
        try:
            response = self.bedrock.converse(
                modelId=model_id,
                **request_body
            )
            elapsed_time = time.time() - start_time
            
            result_text = response['output']['message']['content'][0]['text']
            
            return {
                "model": model_id,
                "video": video_name,
                "success": True,
                "response": result_text,
                "elapsed_time": elapsed_time,
                "input_tokens": response['usage']['inputTokens'],
                "output_tokens": response['usage']['outputTokens']
            }
        except Exception as e:
            return {
                "model": model_id,
                "video": video_name,
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time
            }

    def get_or_upload_video(self, video_path: str) -> Any:
        """检查视频是否已上传，如果没有则上传"""
        from pathlib import Path
        
        video_filename = Path(video_path).name
        
        # 列出所有已上传的文件
        print(f"检查文件是否已存在: {video_filename}")
        try:
            existing_files = genai.list_files()
            for file in existing_files:
                if file.display_name == video_filename and file.state.name == "ACTIVE":
                    print(f"✅ 找到已上传的文件: {file.name}")
                    return file
        except Exception as e:
            print(f"检查文件时出错: {e}")
        
        # 文件不存在，需要上传
        print(f"上传新文件: {video_path}")
        video_file = genai.upload_file(path=video_path)
        
        # 等待视频处理完成
        while video_file.state.name == "PROCESSING":
            print("等待视频处理...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            raise ValueError(f"视频处理失败: {video_file.state.name}")
        
        print(f"✅ 文件上传成功: {video_file.name}")
        return video_file
    
    def test_gemini_2_5_flash(self, video_path: str, video_name: str, api_key: str) -> Dict[str, Any]:
        """测试 gemini-2.5-flash"""
        print(f"\n测试 Gemini 2.5 Flash - {video_name}...")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        start_time = time.time()
        try:
            # 获取或上传视频文件
            video_file = self.get_or_upload_video(video_path)
            
            # 生成内容
            response = model.generate_content([video_file, PROMPT])
            elapsed_time = time.time() - start_time
            
            return {
                "model": "gemini-2.5-flash",
                "video": video_name,
                "success": True,
                "response": response.text,
                "elapsed_time": elapsed_time
            }
        except Exception as e:
            return {
                "model": "gemini-2.5-flash",
                "video": video_name,
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time
            }
    
    def test_gemini_2_5_flash_lite(self, video_path: str, video_name: str, api_key: str) -> Dict[str, Any]:
        """测试 gemini-2.5-flash-lite"""
        print(f"\n测试 Gemini 2.5 Flash Lite - {video_name}...")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        start_time = time.time()
        try:
            # 获取或上传视频文件
            video_file = self.get_or_upload_video(video_path)
            
            # 生成内容
            response = model.generate_content([video_file, PROMPT])
            elapsed_time = time.time() - start_time
            
            return {
                "model": "gemini-2.5-flash-lite",
                "video": video_name,
                "success": True,
                "response": response.text,
                "elapsed_time": elapsed_time
            }
        except Exception as e:
            return {
                "model": "gemini-2.5-flash-lite",
                "video": video_name,
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time
            }
    
    def run_all_tests(self, gemini_api_key: str = None):
        """运行所有测试"""
        print("=" * 80)
        print("开始视频时间线理解测试")
        print("=" * 80)
        
        all_results = []
        
        # 测试 Video 1 - Amazon Nova 模型
        print("\n" + "=" * 80)
        print("测试 Video 1 (batball.mov) - Amazon Nova 模型")
        print("=" * 80)
        
        result = self.test_nova_lite_v1(VIDEO_1_S3, "video-1-person")
        all_results.append(result)
        
        # Nova 2 Lite - Standard 模式
        result = self.test_nova_2_lite(VIDEO_1_S3, "video-1-person", use_reasoning=False)
        all_results.append(result)
        
        # Nova 2 Lite - Reasoning 模式
        result = self.test_nova_2_lite(VIDEO_1_S3, "video-1-person", use_reasoning=True)
        all_results.append(result)
        
        result = self.test_nova_pro_v1(VIDEO_1_S3, "video-1-person")
        all_results.append(result)
        
        # 测试 Video 2 - Amazon Nova 模型
        print("\n" + "=" * 80)
        print("测试 Video 2 (1cut2-5-small.mov) - Amazon Nova 模型")
        print("=" * 80)
        
        result = self.test_nova_lite_v1(VIDEO_2_S3, "video-2-match")
        all_results.append(result)
        
        # Nova 2 Lite - Standard 模式
        result = self.test_nova_2_lite(VIDEO_2_S3, "video-2-match", use_reasoning=False)
        all_results.append(result)
        
        # Nova 2 Lite - Reasoning 模式
        result = self.test_nova_2_lite(VIDEO_2_S3, "video-2-match", use_reasoning=True)
        all_results.append(result)
        
        result = self.test_nova_pro_v1(VIDEO_2_S3, "video-2-match")
        all_results.append(result)
        
        # 测试 Google Gemini 模型（如果提供了 API key）
        # if gemini_api_key:
        #     print("\n" + "=" * 80)
        #     print("测试 Video 1 - Google Gemini 模型")
        #     print("=" * 80)
            
        #     result = self.test_gemini_2_5_flash(VIDEO_1_LOCAL, "video-1-person", gemini_api_key)
        #     all_results.append(result)
            
        #     result = self.test_gemini_2_5_flash_lite(VIDEO_1_LOCAL, "video-1-person", gemini_api_key)
        #     all_results.append(result)
            
        #     print("\n" + "=" * 80)
        #     print("测试 Video 2 - Google Gemini 模型")
        #     print("=" * 80)
            
        #     result = self.test_gemini_2_5_flash(VIDEO_2_LOCAL, "video-2-match", gemini_api_key)
        #     all_results.append(result)
            
        #     result = self.test_gemini_2_5_flash_lite(VIDEO_2_LOCAL, "video-2-match", gemini_api_key)
        #     all_results.append(result)
        
        self.results = all_results
        return all_results
    
    def save_results(self, filename: str = "test_results.json"):
        """保存测试结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        print(f"\n测试结果已保存到: {filename}")
    
    def generate_report(self, output_file: str = "test_report.md"):
        """生成测试报告"""
        report = []
        report.append("# 视频时间线理解测试报告\n")
        report.append(f"**测试日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("---\n")
        
        report.append("## 测试概述\n")
        report.append("本测试评估多个模型对羽毛球比赛视频的时间线理解能力：\n")
        report.append("- amazon.nova-lite-v1:0\n")
        report.append("- amazon.nova-2-lite-v1:0 (standard mode)\n")
        report.append("- amazon.nova-2-lite-v1:0 (reasoning mode, maxReasoningEffort=low)\n")
        report.append("- amazon.nova-pro-v1:0\n")
        report.append("- gemini-2.5-flash\n")
        report.append("- gemini-2.5-flash-lite\n\n")
        
        report.append("## 测试结果汇总\n")
        report.append("| 模型 | 视频 | 状态 | 响应时间(秒) | 输入Token | 输出Token |\n")
        report.append("|------|------|------|-------------|-----------|----------|\n")
        
        for result in self.results:
            status = "✅ 成功" if result['success'] else "❌ 失败"
            model = result['model']
            video = result['video']
            elapsed = f"{result['elapsed_time']:.2f}"
            input_tokens = result.get('input_tokens', 'N/A')
            output_tokens = result.get('output_tokens', 'N/A')
            
            report.append(f"| {model} | {video} | {status} | {elapsed} | {input_tokens} | {output_tokens} |\n")
        
        report.append("\n## 详细结果\n")
        
        for i, result in enumerate(self.results, 1):
            report.append(f"\n### {i}. {result['model']} - {result['video']}\n")
            
            if result['success']:
                report.append(f"**状态**: ✅ 成功\n")
                report.append(f"**响应时间**: {result['elapsed_time']:.2f} 秒\n")
                if 'input_tokens' in result:
                    report.append(f"**输入Token**: {result['input_tokens']}\n")
                    report.append(f"**输出Token**: {result['output_tokens']}\n")
                
                report.append("\n**模型响应**:\n")
                report.append("```json\n")
                report.append(result['response'])
                report.append("\n```\n")
            else:
                report.append(f"**状态**: ❌ 失败\n")
                report.append(f"**错误信息**: {result.get('error', 'Unknown error')}\n")
        
        report.append("\n## 评估指标\n")
        report.append("本测试主要评估以下指标：\n")
        report.append("1. **时间戳准确性**: 模型识别的比赛回合起止时间是否准确\n")
        report.append("2. **回合识别完整性**: 是否识别出所有比赛回合\n")
        report.append("3. **结束原因准确性**: 对每个回合结束原因的判断是否正确\n")
        report.append("4. **响应时间**: 模型处理视频的速度\n")
        report.append("5. **输出格式**: 是否按照要求的JSON格式输出\n")
        
        report_text = "".join(report)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n测试报告已生成: {output_file}")
        return report_text


def main():
    """主函数"""
    import os
    
    # 从环境变量获取 Gemini API Key（可选）
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("警告: 未设置 GEMINI_API_KEY 环境变量，将跳过 Gemini 模型测试")
        print("如需测试 Gemini 模型，请设置: export GEMINI_API_KEY='your-api-key'")
    
    # 创建测试实例
    tester = VideoTimelineTest()
    
    # 运行所有测试
    results = tester.run_all_tests(gemini_api_key)
    
    # 保存结果
    tester.save_results("test_results.json")
    
    # 生成报告
    tester.generate_report("test_report.md")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
