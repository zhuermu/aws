#!/usr/bin/env python3
"""
Test script for Gemini 2.5 Flash image OCR - reads local images
Output format matches ocr_results.json for HTML integration

Usage: python test_gemini_image_ocr.py <GOOGLE_API_KEY>
"""
import google.generativeai as genai
import json
import time
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python test_gemini_image_ocr.py <GOOGLE_API_KEY>")
    sys.exit(1)

genai.configure(api_key=sys.argv[1])

IMAGES_DIR = Path(__file__).parent / "images"
MODEL_ID = "gemini-2.5-flash"

PROMPT = """
Extract all text from the image in original order and format. Output only the recognized text.
"""

INFERENCE_CONFIG = {"topP": 0.9, "temperature": 0.7, "maxTokens": 1024}
NUM_ROUNDS = 3

def extract_text(image_path: Path) -> dict:
    model = genai.GenerativeModel(MODEL_ID, generation_config={
        "top_p": INFERENCE_CONFIG["topP"],
        "temperature": INFERENCE_CONFIG["temperature"],
        "max_output_tokens": INFERENCE_CONFIG["maxTokens"]
    })
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    mime_type = 'image/jpeg' if image_path.suffix.lower() in ['.jpg', '.jpeg'] else f'image/{image_path.suffix[1:]}'
    
    try:
        start = time.time()
        response = model.generate_content([PROMPT, {"mime_type": mime_type, "data": image_data}])
        elapsed = time.time() - start
        
        usage = response.usage_metadata
        return {
            "success": True,
            "model": MODEL_ID,
            "s3_uri": f"images/{image_path.name}",
            "extracted_text": response.text,
            "response_time_ms": round(elapsed * 1000),
            "usage": {
                "input_tokens": usage.prompt_token_count,
                "output_tokens": usage.candidates_token_count,
                "total_tokens": usage.total_token_count
            }
        }
    except Exception as e:
        return {"success": False, "model": MODEL_ID, "s3_uri": f"images/{image_path.name}", "error": str(e)}


def main():
    images = sorted(IMAGES_DIR.glob("*.jpg"))
    print(f"Found {len(images)} images in {IMAGES_DIR}")
    
    results = {
        "config": {
            "prompt": PROMPT,
            "inference_config": INFERENCE_CONFIG,
            "num_rounds": NUM_ROUNDS,
            "models": [MODEL_ID],
            "images": [f"images/{img.name}" for img in images]
        },
        "rounds": [],
        "summary": {
            MODEL_ID: {"total_tokens": 0, "total_time_ms": 0, "count": 0, "min_time_ms": float('inf'), "max_time_ms": 0}
        }
    }
    
    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n{'='*60}\n🔄 Round {round_num}/{NUM_ROUNDS}\n{'='*60}")
        round_data = {"round": round_num, "images": []}
        
        for img in images:
            print(f"\n📷 {img.name}...", end=" ", flush=True)
            result = extract_text(img)
            
            image_result = {
                "s3_uri": f"images/{img.name}",
                "results": {MODEL_ID: result}
            }
            round_data["images"].append(image_result)
            
            if result["success"]:
                s = results["summary"][MODEL_ID]
                s["total_tokens"] += result["usage"]["total_tokens"]
                s["total_time_ms"] += result["response_time_ms"]
                s["count"] += 1
                s["min_time_ms"] = min(s["min_time_ms"], result["response_time_ms"])
                s["max_time_ms"] = max(s["max_time_ms"], result["response_time_ms"])
                print(f"✅ {result['response_time_ms']}ms, {result['usage']['total_tokens']} tokens")
            else:
                print(f"❌ {result['error']}")
        
        results["rounds"].append(round_data)
    
    # Calculate averages
    s = results["summary"][MODEL_ID]
    if s["count"] > 0:
        s["avg_tokens"] = round(s["total_tokens"] / s["count"])
        s["avg_time_ms"] = round(s["total_time_ms"] / s["count"])
    if s["min_time_ms"] == float('inf'):
        s["min_time_ms"] = 0
    
    # Save results
    with open("gemini_ocr_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*60}\n📊 Gemini 2.5 Flash Summary\n{'='*60}")
    print(f"Total: {s['total_tokens']} tokens, {s['total_time_ms']}ms")
    print(f"Avg:   {s.get('avg_tokens', 0)} tokens, {s.get('avg_time_ms', 0)}ms")
    print(f"Time:  min={s['min_time_ms']}ms, max={s['max_time_ms']}ms")
    print(f"\n✅ Results saved to gemini_ocr_results.json")


if __name__ == "__main__":
    main()
