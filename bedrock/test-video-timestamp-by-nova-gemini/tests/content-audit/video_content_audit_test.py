"""
视频内容审核测试 - 多模型对比
测试 Amazon Nova 和 Google Gemini 模型对视频内容的理解和审核能力
"""

import boto3
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import google.generativeai as genai
from pathlib import Path
import os

# 配置
BEDROCK_REGION = "us-east-1"

# 视频配置 - S3 URIs
VIDEOS = {
    "video-1": {
        "s3_uri": "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/6b80e970-67e6-4ee4-a51e-8ceb660e9c54-1000012057.mp4",
        "local_path": "video-1.mp4",
        "expected": {
            "search_keyword": None,  # 无搜索动作
            "title": "Explore Slot Super Win Trick",
            "creator": "Shiv_Storm",
            "watch_duration": 2  # 分钟
        }
    },
    "video-2": {
        "s3_uri": "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/09211f8f-8d39-4038-ae0b-568b4e25bb26-FunPlay1.mp4",
        "local_path": "video-2.mp4",
        "expected": {
            "search_keyword": None,  # 无搜索动作
            "title": None,  # 没观看视频
            "creator": None,  # 无作者
            "watch_duration": 0  # 无视频观看动作
        }
    },
    "video-3": {
        "s3_uri": "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/20251111-110712-caijian.mp4",
        "local_path": "video-3.mp4",
        "expected": {
            "search_keyword": "Slots Game Tricks Revealed",
            "title": "STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed",
            "creator": "K_Mater_Gaming",
            "watch_duration": 3  # 分钟
        }
    },
    "video-4": {
        "s3_uri": "s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/ee51c5a7-a44f-4f0b-82d2-772736aa36f3-Screenrecorder20251107140342212.mp4",
        "local_path": "video-4.mp4",
        "expected": {
            "search_keyword": None,  # 无搜索动作
            "title": "STOP Losing Money! TeenPatti Explorer Slo..",
            "creator": "@KGaming24",
            "watch_duration": 2  # 分钟
        }
    }
}

# 分析提示词
ANALYSIS_PROMPT = """You are a video content analyzer. Analyze the provided video and identify which of the following user actions are shown:

1. Keyword Search: Check if the keywords entered by the user starts with "explore slot super win trick" or similar words 80%.
2. Found Target Video - Title Verification: Check if the title of the video played by the user starts with "Explore Slot Super Win Trick".
3. Found Target Video - Creator Verification: Check if the creator of the video played by the user contains "Shiv_Storm". The creator is below the video title, to the right of the avatar.
4. Watched for 1 minute: User has watched the video for 1 minute.
5. Watched for 2 minute: User has watched the video for 2 minute.
6. Watched for 3 minute: User has watched the video for 3 minute.

**Output Format:**
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "(COMPLETED/NOT_COMPLETED)",
      "expected": "explore slot super win trick",
      "actual": "(Keywords actually searched by the user)"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "(COMPLETED/NOT_COMPLETED)",
      "expected": "Explore Slot Super Win Trick",
      "actual": "(Title of the video being played)"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "(COMPLETED/NOT_COMPLETED)",
      "expected": "Shiv_Storm",
      "actual": "(Creator of the video being played)"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "(COMPLETED/NOT_COMPLETED)"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "(COMPLETED/NOT_COMPLETED)"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "(COMPLETED/NOT_COMPLETED)"
    }
  ]
}"""


class VideoContentAuditTest:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        self.results = []
        
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
                                "format": "mp4",
                                "source": {"s3Location": {"uri": video_s3_uri}}
                            }
                        },
                        {"text": ANALYSIS_PROMPT}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1024,
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
    
    def test_nova_2_lite(self, video_s3_uri: str, video_name: str, use_reasoning: bool = False, service_tier: str = "standard") -> Dict[str, Any]:
        """测试 amazon.nova-2-lite-v1:0 (支持 reasoning 和非 reasoning 模式)"""
        mode_label = "Reasoning" if use_reasoning else "Standard"
        print(f"\n测试 Nova 2 Lite ({mode_label}, service_tier={service_tier}) - {video_name}...")
        
        # 使用推理配置文件而不是直接的模型ID
        model_id = "us.amazon.nova-2-lite-v1:0"
        
        # Reasoning 模式需要更多 tokens
        max_tokens = 65535 if use_reasoning else 4096
        temperature = 0.0 if use_reasoning else 0.1
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "video": {
                                "format": "mp4",
                                "source": {"s3Location": {"uri": video_s3_uri}}
                            }
                        },
                        {"text": ANALYSIS_PROMPT}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": 1.0
            },
            "additionalModelRequestFields": {}
        }
        
        # 添加 service_tier 参数作为顶级参数
        if service_tier and service_tier != "standard":
            # 将 standard 映射为 default
            tier_value = "default" if service_tier == "standard" else service_tier
            request_body["serviceTier"] = {"type": tier_value}
            print(f"serviceTier: {tier_value}")
        
        # 如果启用 reasoning 模式，添加配置
        if use_reasoning:
            request_body["additionalModelRequestFields"]["reasoningConfig"] = {
                "type": "enabled",
                "maxReasoningEffort": "low"
            }
        
        start_time = time.time()
        try:
            # 统一使用非流式 converse API
            response = self.bedrock.converse(
                modelId=model_id,
                **request_body
            )
            elapsed_time = time.time() - start_time
            
            content_blocks = response['output']['message']['content']
            result_text = ""
            reasoning_text = ""
            
            for block in content_blocks:
                if 'text' in block:
                    result_text += block['text']
                elif 'reasoningText' in block:
                    reasoning_text += block['reasoningText']
            
            model_label = f"{model_id} (reasoning=low, service_tier={service_tier})" if use_reasoning else f"{model_id} (service_tier={service_tier})"
            result = {
                "model": model_label,
                "video": video_name,
                "success": True,
                "response": result_text,
                "elapsed_time": elapsed_time,
                "input_tokens": response['usage']['inputTokens'],
                "output_tokens": response['usage']['outputTokens']
            }
            
            if reasoning_text:
                result["reasoning"] = reasoning_text
            
            return result
            
        except Exception as e:
            model_label = f"{model_id} (reasoning=low, service_tier={service_tier})" if use_reasoning else f"{model_id} (service_tier={service_tier})"
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
                                "format": "mp4",
                                "source": {"s3Location": {"uri": video_s3_uri}}
                            }
                        },
                        {"text": ANALYSIS_PROMPT}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 4096,
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
        video_filename = Path(video_path).name
        
        print(f"检查文件是否已存在: {video_filename}")
        try:
            existing_files = genai.list_files()
            for file in existing_files:
                if file.display_name == video_filename and file.state.name == "ACTIVE":
                    print(f"✅ 找到已上传的文件: {file.name}")
                    return file
        except Exception as e:
            print(f"检查文件时出错: {e}")
        
        print(f"上传新文件: {video_path}")
        video_file = genai.upload_file(path=video_path)
        
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
            video_file = self.get_or_upload_video(video_path)
            response = model.generate_content([video_file, ANALYSIS_PROMPT])
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
            video_file = self.get_or_upload_video(video_path)
            response = model.generate_content([video_file, ANALYSIS_PROMPT])
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
        print("开始视频内容审核测试")
        print("=" * 80)
        
        all_results = []
        
        # 测试所有视频
        for video_key, video_config in VIDEOS.items():
            print(f"\n{'=' * 80}")
            print(f"测试 {video_key} - Amazon Nova 模型")
            print(f"{'=' * 80}")
            
            s3_uri = video_config["s3_uri"]
            local_path = video_config["local_path"]
            
            # # Amazon Nova Lite v1
            # result = self.test_nova_lite_v1(s3_uri, video_key)
            # result["expected"] = video_config["expected"]
            # all_results.append(result)
            
            # Amazon Nova 2 Lite - Standard 模式
            result = self.test_nova_2_lite(s3_uri, video_key, use_reasoning=False, service_tier="priority")
            result["expected"] = video_config["expected"]
            all_results.append(result)
            
            # Amazon Nova 2 Lite - Flex 模式
            # result = self.test_nova_2_lite(s3_uri, video_key, use_reasoning=False, service_tier="flex")
            # result["expected"] = video_config["expected"]
            # all_results.append(result)
            
            # Amazon Nova 2 Lite - Reasoning 模式
            # result = self.test_nova_2_lite(s3_uri, video_key, use_reasoning=True, service_tier="standard")
            # result["expected"] = video_config["expected"]
            # all_results.append(result)
            
            # Amazon Nova Pro v1
            # result = self.test_nova_pro_v1(s3_uri, video_key)
            # result["expected"] = video_config["expected"]
            # all_results.append(result)
            
            # Google Gemini 模型（如果提供了 API key）
            # if gemini_api_key:
            #     print(f"\n{'=' * 80}")
            #     print(f"测试 {video_key} - Google Gemini 模型")
            #     print(f"{'=' * 80}")
                
            #     # Gemini 2.5 Flash
            #     result = self.test_gemini_2_5_flash(local_path, video_key, gemini_api_key)
            #     result["expected"] = video_config["expected"]
            #     all_results.append(result)
                
            #     # Gemini 2.5 Flash Lite
            #     result = self.test_gemini_2_5_flash_lite(local_path, video_key, gemini_api_key)
            #     result["expected"] = video_config["expected"]
            #     all_results.append(result)
        
        self.results = all_results
        return all_results
    
    def save_results(self, filename: str = "audit_test_results.json"):
        """保存测试结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        print(f"\n测试结果已保存到: {filename}")
    
    def generate_report(self, output_file: str = "audit_test_report.md"):
        """生成测试报告"""
        report = []
        report.append("# 视频内容审核测试报告\n\n")
        report.append(f"**测试日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        report.append("---\n\n")
        
        report.append("## 测试概述\n\n")
        report.append("本测试评估多个模型对视频内容的理解和审核能力：\n\n")
        report.append("- amazon.nova-lite-v1:0\n")
        report.append("- amazon.nova-2-lite-v1:0 (standard mode)\n")
        report.append("- amazon.nova-2-lite-v1:0 (reasoning mode, maxReasoningEffort=low)\n")
        report.append("- amazon.nova-pro-v1:0\n")
        report.append("- gemini-2.5-flash\n")
        report.append("- gemini-2.5-flash-lite\n\n")
        
        report.append("## 测试结果汇总\n\n")
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
        
        report.append("\n## 详细结果\n\n")
        
        for i, result in enumerate(self.results, 1):
            report.append(f"\n### {i}. {result['model']} - {result['video']}\n\n")
            
            # 显示期望值
            if 'expected' in result:
                report.append("**期望值**:\n")
                expected = result['expected']
                report.append(f"- 搜索关键词: {expected['search_keyword'] or '无搜索动作'}\n")
                report.append(f"- 视频标题: {expected['title'] or '没观看视频'}\n")
                report.append(f"- 作者: {expected['creator'] or '无作者'}\n")
                report.append(f"- 观看时长: {expected['watch_duration']}分钟\n\n")
            
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
        
        report.append("\n## 评估指标\n\n")
        report.append("本测试主要评估以下指标：\n\n")
        report.append("1. **关键词搜索识别**: 模型是否能识别用户搜索的关键词\n")
        report.append("2. **视频标题识别**: 模型是否能识别用户观看的视频标题\n")
        report.append("3. **作者识别**: 模型是否能识别视频作者信息\n")
        report.append("4. **观看时长识别**: 模型是否能准确判断用户观看视频的时长\n")
        report.append("5. **响应时间**: 模型处理视频的速度\n")
        report.append("6. **输出格式**: 是否按照要求的JSON格式输出\n")
        
        report_text = "".join(report)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n测试报告已生成: {output_file}")
        return report_text


def main():
    """主函数"""
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("警告: 未设置 GEMINI_API_KEY 环境变量，将跳过 Gemini 模型测试")
        print("如需测试 Gemini 模型，请设置: export GEMINI_API_KEY='your-api-key'")
    
    tester = VideoContentAuditTest()
    results = tester.run_all_tests(gemini_api_key)
    tester.save_results("audit_test_results.json")
    tester.generate_report("audit_test_report.md")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
