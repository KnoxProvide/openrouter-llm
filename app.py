#!/usr/bin/env python3
"""
OpenRouter 图像识别 HTTP API 服务
使用 FastAPI 提供 RESTful API 接口
"""

import os
import json
import re
import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from openai import OpenAI
from dotenv import load_dotenv

# 配置日志格式 - 添加时间戳
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(
    title="OpenRouter Image Recognition API",
    description="图像识别和证件信息提取 API 服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求模型
class ImageAnalyzeRequest(BaseModel):
    image_url: HttpUrl
    question: Optional[str] = "What is in this image?"
    model: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg",
                "question": "What is in this image?",
                "model": "google/gemma-3-4b-it:free"
            }
        }


class IDCardRequest(BaseModel):
    image_url: HttpUrl
    model: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/id-card.jpg",
                "model": "google/gemma-3-4b-it:free"
            }
        }


# 响应模型
class ImageAnalyzeResponse(BaseModel):
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None


class IDCardResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


def get_openai_client():
    """获取 OpenAI 客户端实例"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="未配置 OPENROUTER_API_KEY 环境变量"
        )
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def analyze_image(image_url: str, question: str, model: Optional[str] = None) -> str:
    """
    使用 OpenRouter API 分析图像内容
    
    Args:
        image_url: 图像的 URL 地址
        question: 要问的问题
        model: 使用的模型,如果为 None 则使用环境变量中的默认模型
    
    Returns:
        模型的响应内容
    """
    logger.info(f"开始分析图像: {image_url[:50]}... 问题: {question[:30]}...")
    client = get_openai_client()
    
    # 获取配置
    site_url = os.getenv("YOUR_SITE_URL", "http://localhost:8000")
    site_name = os.getenv("YOUR_SITE_NAME", "OpenRouter Image Recognition API")
    default_model = os.getenv("MODEL", "google/gemma-3-4b-it:free")
    
    model_to_use = model if model else default_model
    
    try:
        # 调用 API
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": site_url,
                "X-Title": site_name,
            },
            model=model_to_use,
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
        
        result = completion.choices[0].message.content
        logger.info(f"图像分析完成，响应长度: {len(result)} 字符")
        return result
        
    except Exception as e:
        logger.error(f"API 调用失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"API 调用失败: {str(e)}"
        )


@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "name": "OpenRouter Image Recognition API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze - 通用图像分析",
            "id_card": "/api/id-card - 证件信息提取",
            "health": "/health - 健康检查"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return {
        "status": "healthy",
        "api_configured": bool(api_key)
    }


@app.post("/api/analyze", response_model=ImageAnalyzeResponse)
async def analyze_image_endpoint(request: ImageAnalyzeRequest):
    """
    通用图像分析接口
    
    分析图像内容并返回描述
    """
    logger.info(f"收到图像分析请求 - URL: {str(request.image_url)[:50]}...")
    try:
        result = analyze_image(
            str(request.image_url),
            request.question,
            request.model
        )
        
        return ImageAnalyzeResponse(
            success=True,
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return ImageAnalyzeResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/id-card", response_model=IDCardResponse)
async def extract_id_card_endpoint(request: IDCardRequest):
    """
    证件信息提取接口
    
    从证件照片中提取结构化信息,返回 JSON 格式
    """
    logger.info(f"收到证件识别请求 - URL: {str(request.image_url)[:50]}...")
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
        result = analyze_image(
            str(request.image_url),
            question,
            request.model
        )
        
        # 尝试提取和解析 JSON
        json_match = re.search(r'```json\s*\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = result
        
        try:
            data = json.loads(json_str)
            logger.info(f"证件信息提取成功，包含 {len(data)} 个字段")
            return IDCardResponse(
                success=True,
                data=data
            )
        except json.JSONDecodeError as e:
            # 如果 JSON 解析失败,返回原始文本
            logger.warning(f"JSON 解析失败: {str(e)}")
            return IDCardResponse(
                success=False,
                error="无法解析为 JSON 格式",
                data={"raw_response": result}
            )
    
    except HTTPException:
        raise
    except Exception as e:
        return IDCardResponse(
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )