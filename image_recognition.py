#!/usr/bin/env python3
"""
OpenRouter 图像识别示例
使用 OpenRouter API 和 Google Gemma 模型进行图像内容分析
"""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def analyze_image(image_url: str, question: str = "What is in this image?") -> str:
    """
    使用 OpenRouter API 分析图像内容
    
    Args:
        image_url: 图像的 URL 地址
        question: 要问的问题,默认为 "What is in this image?"
    
    Returns:
        模型的响应内容
    """
    # 从环境变量获取配置
    api_key = os.getenv("OPENROUTER_API_KEY")
    site_url = os.getenv("YOUR_SITE_URL", "http://localhost:3000")
    site_name = os.getenv("YOUR_SITE_NAME", "OpenRouter Image Recognition")
    model = os.getenv("MODEL", "google/gemma-3-4b-it:free")
    
    if not api_key:
        raise ValueError(
            "未找到 OPENROUTER_API_KEY 环境变量。\n"
            "请创建 .env 文件并设置你的 API 密钥。"
        )
    
    # 初始化 OpenAI 客户端,指向 OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    print(f"正在分析图像: {image_url}")
    # print(f"问题: {question}\n")
    print(f"模型: {model}\n")
    
    try:
        # 调用 API
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": site_url,
                "X-Title": site_name,
            },
            extra_body={},
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )
        
        # 提取响应内容
        response = completion.choices[0].message.content
        return response
        
    except Exception as e:
        raise Exception(f"API 调用失败: {str(e)}")


def extract_ug_id_card_info(image_url: str) -> dict:
    """
    提取证件照信息并返回 JSON 对象
    
    Args:
        image_url: 证件照的 URL 地址
    
    Returns:
        包含证件信息的字典对象,如果解析失败则返回 None
    """
    question = """Please extract all information from this ID card/document and return it in JSON format.
Required fields:
- document type
- surname
- given name
- nationality
- sex
- date of birth
- nin
- card no
- date of expiry
- portrait
Return ONLY valid JSON, without any additional text or explanation."""
    
    try:
        # 调用分析函数
        result = analyze_image(image_url, question)
        
        # 提取 JSON
        json_match = re.search(r'```json\s*\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = result
        
        # 解析并返回
        data = json.loads(json_str)
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return None
    except Exception as e:
        print(f"提取失败: {e}")
        return None



def main():
    """主函数 - 演示图像识别功能"""
    
    # 示例图像 URL
    image_url = "https://nanoloans.obs.af-south-1.myhuaweicloud.com/2024-08-22%2F1724355272696.jpg?x-image-process=image/resize,w_700/quality,Q_80"
    
    print("=" * 60)
    print("OpenRouter 图像识别示例")
    print("=" * 60)
    print()

    try:
        result = extract_ug_id_card_info(image_url)
        
        print("原始响应:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    print("\n✓ 分析完成!")
    return 0


if __name__ == "__main__":
    exit(main())
