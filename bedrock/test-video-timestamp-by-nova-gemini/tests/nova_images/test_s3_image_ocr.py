#!/usr/bin/env python3
"""
Test script to compare OCR performance across Nova models with multiple rounds
"""
import boto3
import json
import time

MODELS = [
    "amazon.nova-pro-v1:0",
    "amazon.nova-lite-v1:0",
    "amazon.nova-2-lite-v1:0"
]

IMAGES = [
    's3://bedrock-video-generation-us-east-1-pi8hu9/iamges_undstands/20251023-174349.jpg',
    's3://bedrock-video-generation-us-east-1-pi8hu9/iamges_undstands/20251023-174354.jpg',
    's3://bedrock-video-generation-us-east-1-pi8hu9/iamges_undstands/20251023-174358.jpg',
    's3://bedrock-video-generation-us-east-1-pi8hu9/iamges_undstands/20251023-174403.jpg',
    's3://bedrock-video-generation-us-east-1-pi8hu9/iamges_undstands/20251023-174407.jpg',
]

PROMPT = "Extract all text from the image in original order and format. Output only the recognized text."
INFERENCE_CONFIG = {"temperature": 0.0, "maxTokens": 1024}
NUM_ROUNDS = 3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


def extract_text(s3_uri: str, model_id: str) -> dict:
    image_format = 'jpeg' if s3_uri.endswith('.jpg') else s3_uri.split('.')[-1]
    
    messages = [{
        "role": "user",
        "content": [
            {"text": PROMPT},
            {"image": {"format": image_format, "source": {"s3Location": {"uri": s3_uri}}}}
        ]
    }]
    
    try:
        start = time.time()
        response = bedrock.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=INFERENCE_CONFIG
        )
        elapsed = time.time() - start
        
        usage = response.get('usage', {})
        return {
            "success": True,
            "model": model_id,
            "s3_uri": s3_uri,
            "extracted_text": response['output']['message']['content'][0]['text'],
            "response_time_ms": round(elapsed * 1000),
            "usage": {
                "input_tokens": usage.get('inputTokens', 0),
                "output_tokens": usage.get('outputTokens', 0),
                "total_tokens": usage.get('totalTokens', 0)
            }
        }
    except Exception as e:
        return {"success": False, "model": model_id, "s3_uri": s3_uri, "error": str(e)}


def main():
    results = {
        "config": {
            "prompt": PROMPT,
            "inference_config": INFERENCE_CONFIG,
            "num_rounds": NUM_ROUNDS,
            "models": MODELS,
            "images": IMAGES
        },
        "rounds": [],
        "summary": {}
    }
    
    # Initialize summary
    for model in MODELS:
        results["summary"][model] = {
            "total_tokens": 0, "total_time_ms": 0, "count": 0,
            "min_time_ms": float('inf'), "max_time_ms": 0
        }
    
    # Run multiple rounds
    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n{'='*60}")
        print(f"🔄 Round {round_num}/{NUM_ROUNDS}")
        print('='*60)
        
        round_data = {"round": round_num, "images": []}
        
        for s3_uri in IMAGES:
            filename = s3_uri.split('/')[-1]
            print(f"\n📷 {filename}")
            
            image_result = {"s3_uri": s3_uri, "results": {}}
            
            for model in MODELS:
                short_name = model.split('.')[1].replace('-v1:0', '')
                print(f"  🤖 {short_name}...", end=" ", flush=True)
                result = extract_text(s3_uri, model)
                image_result["results"][model] = result
                
                if result["success"]:
                    s = results["summary"][model]
                    s["total_tokens"] += result["usage"]["total_tokens"]
                    s["total_time_ms"] += result["response_time_ms"]
                    s["count"] += 1
                    s["min_time_ms"] = min(s["min_time_ms"], result["response_time_ms"])
                    s["max_time_ms"] = max(s["max_time_ms"], result["response_time_ms"])
                    print(f"✅ {result['response_time_ms']}ms")
                else:
                    print(f"❌ {result['error']}")
            
            round_data["images"].append(image_result)
        
        results["rounds"].append(round_data)
    
    # Calculate averages
    for model in MODELS:
        s = results["summary"][model]
        if s["count"] > 0:
            s["avg_tokens"] = round(s["total_tokens"] / s["count"])
            s["avg_time_ms"] = round(s["total_time_ms"] / s["count"])
        if s["min_time_ms"] == float('inf'):
            s["min_time_ms"] = 0
    
    # Save results
    with open("ocr_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Overall Summary")
    print("=" * 60)
    for model in MODELS:
        s = results["summary"][model]
        name = model.split('.')[1].replace('-v1:0', '')
        print(f"\n{name}:")
        print(f"  Total: {s['total_tokens']} tokens, {s['total_time_ms']}ms")
        print(f"  Avg:   {s.get('avg_tokens', 0)} tokens, {s.get('avg_time_ms', 0)}ms")
        print(f"  Time:  min={s['min_time_ms']}ms, max={s['max_time_ms']}ms")
    
    print(f"\n✅ Results saved to ocr_results.json")


if __name__ == "__main__":
    main()
