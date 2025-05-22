import json
import os
from langchain_aws import ChatBedrock

def translate_text(text_list, target_language="zh-CN", model="us.amazon.nova-lite-v1:0"):
    """
    Translate a list of texts to the target language using AWS Bedrock.
    
    Args:
        text_list: List of texts to translate
        target_language: Target language code (default: zh-CN for Chinese)
        model: AWS Bedrock model to use
        
    Returns:
        Translated texts
    """
    # Initialize the Bedrock chat model
    chat_model = ChatBedrock(
        model=model,
        region="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    
    # Define the structured output format
    translate_output_schema = {
        "name": "translate_texts_result",
        "description": "Translate the input texts into the target language",
        "parameters": {
            "type": "object",
            "properties": {
                "translated_texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The translated texts",
                },
            },
            "required": ["translated_texts"],
        },
    }
    
    # Create a simple prompt
    system_prompt = f"""Translate the following texts to {target_language}.
Rules:
1. Translate accurately without losing content
2. Don't translate links or code
3. Return translations in the same order as input"""
    
    # Format the input for the model
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Texts to translate: {json.dumps(text_list, ensure_ascii=False)}"}
    ]
    
    # Get the translation
    result = chat_model.with_structured_output(translate_output_schema).invoke(messages)
    return result

if __name__ == "__main__":
    # Text to translate
    texts = [["请帮我翻译成中文"]]
    
    # Optional: Change model if needed
    # model = "us.amazon.nova-pro-v1:0"
    
    # Perform translation
    result = translate_text(texts)
    print(result)
