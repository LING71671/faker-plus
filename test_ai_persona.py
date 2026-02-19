import json
import time
from faker import Faker
from faker.providers.persona.zh_CN import Provider as PersonaProvider

import os

# 配置 AI (以DeepSeek为例)
ai_config = {
    "api_key": os.environ.get("DEEPSEEK_API_KEY", "your-deepseek-api-key-here"),
    "model": "deepseek-chat",
    "image_api_key": os.environ.get("SILICONFLOW_API_KEY", "your-siliconflow-api-key-here")
}

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

print('=' * 60)
print('--- FULL VIRTUAL PERSONA WITH AI TEST ---')
print('=' * 60)
print("开始生成全维度带 AI 故事与画像Prompt的角色...\n(请稍候，由于涉及文字和图片两种大模型接口，约需5-10秒)")

start_t = time.time()
p = fake.persona(
    use_ai=True,
    ai_config=ai_config
)
end_t = time.time()

print(f"\n生成完毕！耗时: {end_t - start_t:.2f} 秒\n")

# 输出基础信息
print("[1] 基础信息框架：")
base_info = {k: v for k, v in p.items() if k not in ["life_story", "image_prompt", "avatar_url"]}
print(json.dumps(base_info, indent=2, ensure_ascii=False))

# 输出核心经历
print("\n[2] 虚拟人生履历 (AI生成)：")
print("-" * 40)
print(p.get("life_story", "生成失败"))
print("-" * 40)

# 输出人脸描绘Prompt
print("\n[3] SD/Midjourney 高级外貌提示词 (AI生成)：")
print("-" * 40)
print(p.get("image_prompt", "生成失败"))
print("-" * 40)

# 输出生成的照片
print("\n[4] AI 头像生成直链 (SiliconFlow FLUX.1)：")
print("-" * 40)
print(p.get("avatar_url", "抱歉，生图请求失败。"))
print("-" * 40)
print("\n" + '=' * 60)
