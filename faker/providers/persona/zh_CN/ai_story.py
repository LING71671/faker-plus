import json
import urllib.request
from typing import Any, Dict, Optional


def generate_ai_story(persona: Dict[str, Any], config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate an AI life story and image prompt based on the provided persona dictionary.
    No extra dependencies: purely uses urllib.request to hit OpenAI-compatible endpoints.
    """
    api_key = config.get("api_key")
    if not api_key:
        print("Warning: use_ai=True but no api_key provided. Skipping AI generation.")
        return None

    base_url = config.get("base_url", "https://api.deepseek.com/chat/completions")
    model = config.get("model", "deepseek-chat")

    # Strict system prompt to avoid hallucinations
    system_prompt = (
        "你是一个极其严格的虚拟人物画像生成引擎的后台节点。请基于用户上传的核心设定字典（JSON形式），"
        "为该人物生成一段符合社会发展客观规律的人生经历/故事（不多于200字）。"
        "绝对规则："
        "1. 绝不允许编造不存在的学校、公司、或者地理位置（例如不存在的街道）。"
        "2. 不要出现时空错乱（如07年在北京奥运当旗手等违背物理规律的事件）。"
        "3. 户籍地必须和人生早期轨迹或籍贯吻合。如果有主手机号（primary_phone）和所在地，必须体现出他在该地生活过。"
        "如果有副手机号（secondary_phone）和工作地，必须让该地成为他人生的重要轨迹（如读大学或当前长期工作）。"
        "4. 从故事中提取一段稳定的 midjourney 可用的英文 Prompt，描述其外貌风格（符合年龄和职业，不带复杂背景）。"
        "5. 返回纯 JSON 格式（不带任何 markdown 标记如 ```json ），包含且仅包含两个字段：'life_story' (字符串), 'image_prompt' (字符串)。"
    )

    user_prompt = json.dumps(persona, ensure_ascii=False)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"}
    }

    try:
        req = urllib.request.Request(
            base_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=40) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result["choices"][0]["message"]["content"]
            # Basic cleanup in case the model returns markdown codeblocks anyway
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
    except Exception as e:
        print(f"Warning: AI generation failed request: {e}")
        return None


def generate_ai_image(prompt: str, api_key: str) -> Optional[str]:
    """
    Generate an AI image using SiliconFlow API with FLUX.1-schnell
    """
    if not api_key:
        return None
        
    url = "https://api.siliconflow.cn/v1/images/generations"
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell",
        "prompt": prompt,
        "image_size": "1024x1024"
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "images" in result and len(result["images"]) > 0:
                return result["images"][0].get("url")
            elif "data" in result and len(result["data"]) > 0:
                return result["data"][0].get("url")
            return None
    except Exception as e:
        print(f"Warning: Image generation failed: {e}")
        return None
