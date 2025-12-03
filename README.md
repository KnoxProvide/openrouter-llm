# OpenRouter 图像识别示例

使用 OpenRouter API 和 Google Gemma 模型进行图像内容分析的 Python 示例项目。

## 功能特性

- ✅ 使用 OpenRouter API 访问多种 AI 模型
- ✅ 支持图像 URL 分析
- ✅ 使用免费的 Google Gemma 3 4B 模型
- ✅ 环境变量配置管理
- ✅ 完善的错误处理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`:

```bash
cp .env.example .env
```

编辑 `.env` 文件,填入你的 OpenRouter API 密钥:

```env
OPENROUTER_API_KEY=your_actual_api_key_here
YOUR_SITE_URL=http://localhost:3000
YOUR_SITE_NAME=My OpenRouter App
MODEL=google/gemma-3-4b-it:free
```

> 💡 **获取 API 密钥**: 访问 [OpenRouter](https://openrouter.ai/) 注册并获取你的 API 密钥。

## 项目结构

```
openrouter-llm/
├── image_recognition.py   # 主程序文件
├── example_usage.py       # 证件信息提取示例
├── run.sh                # 便捷运行脚本
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── .env                  # 环境变量配置(需自行创建)
├── .gitignore           # Git 忽略文件
└── README.md            # 项目说明
```

## 支持的模型

当前默认使用 `google/gemma-3-4b-it:free` 模型,这是一个免费的视觉语言模型。

### 切换模型

你可以通过修改 `.env` 文件中的 `MODEL` 环境变量来切换模型:

```env
MODEL=google/gemini-flash-1.5
```

其他支持图像的模型:
- `google/gemini-flash-1.5` - Google Gemini Flash
- `anthropic/claude-3-haiku` - Claude 3 Haiku
- `openai/gpt-4-vision-preview` - GPT-4 Vision
- `google/gemma-3-4b-it:free` - Gemma 3 4B (免费)

查看更多模型: [OpenRouter Models](https://openrouter.ai/models)

## 注意事项

⚠️ **重要提示**:
- 确保 `.env` 文件不要提交到 Git 仓库
- API 密钥应妥善保管,不要泄露
- 免费模型可能有使用限制

## 常见问题

### Q: 如何获取 OpenRouter API 密钥?
A: 访问 [OpenRouter](https://openrouter.ai/),注册账号后在设置页面生成 API 密钥。

### Q: 支持本地图像吗?
A: 当前版本仅支持图像 URL。如需支持本地图像,需要先将图像转换为 base64 编码。

## 许可证

MIT License

## 相关链接

- [OpenRouter 官网](https://openrouter.ai/)
- [OpenRouter API 文档](https://openrouter.ai/docs)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
