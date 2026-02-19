# Faker-Plus

[English](#english) | [中文](#中文)

---

<h2 id="english">Faker-Plus</h2>

**Faker-Plus** is a supercharged fork of the official `Faker` (the famous Python fake data generator). It is specifically tailored for strict data testing scenarios in Mainland China (`zh_CN`) and for building highly realistic data for Large Language Model (LLM) reasoning, perfectly bridging the logic gaps found in the original Faker's localized scenarios.

From the strictly mapped "Five-Level Administrative Division Address" to the "strong correlation between phone numbers and local life trajectories", and the "seamless built-in AI model for generating highly realistic portraits and life stories", Faker-Plus provides the most robust and immersive testing data foundation.

### ✨ Core Features

1. **Absolute Objective Authenticity in Basic Persona Engine** (Offline & Ultra-fast generation):
    - **Consistent Household Register and ID Card**: The generated ID number not only passes the 18-digit verification of the `ISO 7064:1983.MOD 11-2` algorithm, but its first 6 digits are 100% strictly bound to the randomly generated `hometown_address`.
    - **High-Precision 5-Level Address Generation**: Breaking through the traditional 3-level framework. We introduced a 4/5-level dictionary engine based on Chinese administrative villages/communities/townships.
    - **Demographic Consistency**: The generated `gender` and `age` are strictly mapped to the ID card's birth date and the 17th parity bit.
    - **Phone Number Geolocation Mapping**: Automatically extracts `primary_phone` from the real network segment dictionary of the three major operators based on the hometown; `secondary_phone` matches the assigned work location.

2. **🤖 Zero-Dependency AI Empowerment** (Configurable, Direct to LLM):
    - By simply providing an `api_key`, the engine uses pure Python `urllib` to connect to any OpenAI-compatible LLM (e.g., DeepSeek / Zhipu / SiliconFlow) without installing third-party libraries.
    - **Defensive System Prompt**: Discards AI hallucinations (like inventing fake schools or time-traveling) and extracts coherent life experiences and social relations.
    - **Text-to-Image Avatar Output**: Provide an `image_api_key` (e.g., SiliconFlow) to instantly generate a high-quality real-life portrait of the persona using cutting-edge models like FLUX.1.

### 💻 Quick Start

**Installation**

Please uninstall the official `Faker` first to avoid conflicts:

```bash
pip uninstall faker
pip install faker-plus
```

**Usage**

The import syntax remains exactly the same as the official `faker`:

```python
import json
from faker import Faker
from faker.providers.persona.zh_CN import Provider as PersonaProvider

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

# 1. Generate a persona offline with specific conditions:
p_offline = fake.persona(
    gender="Female",
    age_range=(20, 30),
    hometown_province="Fujian",
    has_second_phone=True
)
print(json.dumps(p_offline, indent=2))

# -------------------------------------------------------------

# 2. Advanced: Generate logical life stories and real portraits via AI
ai_config = {
    "api_key": "YOUR_LLM_API_KEY",
    "base_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
    "image_api_key": "YOUR_SILICONFLOW_API_KEY"  # Optional: For Portrait Generation
}

p_ai = fake.persona(
    use_ai=True,
    ai_config=ai_config,
    hometown_province="Beijing"
)
```

---

<h2 id="中文">Faker-Plus (中文版)</h2>

**Faker-Plus** 是一款建立在官方 `Faker` （Python 著名假数据生成库）之上的高能增强版分支包。它专为严苛的中国大陆（zh_CN）数据测试与大模型推演数据构筑场景而生，完美弥补了原版 Faker 在深度中国本土化场景下的拼凑感与逻辑断层。

从严格映射的“五级行政区划地址”到“手机号与户籍生活轨迹强关联”，再到“无缝内置 AI 大模型直出高度拟真人物相貌与生平故事”，Faker-Plus 为你提供最坚固的、免于脱戏的测试数据底座。

### ✨ 核心特性

1. **绝对客观真实性的基础画像引擎**（脱机使用，极速生成）：
    - **户籍与身份证一致**：身份证号码不仅通过了 `ISO 7064:1983.MOD 11-2` 的 18 位校验，更做到了前 6 位数字和人物真实随机到的五级 `hometown_address` 产生 100% 强绑定。
    - **高精度五级细分网格地址生成**：突破传统框架里的“省市区”老三篇。我们引入并自研了基于中国行政村/社区/镇/乡的四、五级字典引擎。
    - **性别年龄与身份证一致**：生成的 `gender` 和 `age` 严格映射到身份证对应的日期段与校验位。
    - **主副手机号归属地映射**：引擎会自动根据设定的“籍贯/工作地”从三大运营商真实网段库中随机抽取真实归属地手机号。

2. **🤖 零网络依赖库的 AI 赋能整合**（可配置使用，直连大模型）：
    - 只需要配置 `api_key`，底层就会利用纯 Python `urllib` 封包，无第三方依赖地接入任意遵循 OpenAI 格式的大模型（例如 DeepSeek / 智谱 / SiliconFlow）。
    - **系统防御性 Prompt** 强力约束 AI，反向提取符合物理规则、地域关联的**人物一生经历**与**社会关系**，彻底杜绝大模型在造数时常见的乱盖学校和时空穿梭等幻觉。
    - **文本生图直接输出羁绊照**：如果提供 `image_api_key`，系统还能以百毫秒级的速度通过如 FLUX.1 之类的顶级模型直出该角色的高质量真实外貌照片！

### 💻 快速食用指南

**安装**

直接覆盖式兼容，请先卸载官方 `Faker` 再安装：

```bash
pip uninstall faker
pip install faker-plus
```

**使用方式**

代码层面与官方 `faker` 完全保持高度协同，**导入语法一字不差**：

```python
import json
from faker import Faker
from faker.providers.persona.zh_CN import Provider as PersonaProvider

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

# 1. 纯脱机极速生成一个有明确条件限制的全生命周期人物：
p_offline = fake.persona(
    gender="女",
    age_range=(20, 30),
    hometown_province="福建",
    has_second_phone=True
)
print(json.dumps(p_offline, ensure_ascii=False, indent=2))

# -------------------------------------------------------------

# 2. 依托 AI 引擎：提供虚构生平和个人真实照片直链
ai_config = {
    "api_key": "YOUR_LLM_API_KEY",
    "base_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
    "image_api_key": "YOUR_SILICONFLOW_API_KEY" 
}

p_ai = fake.persona(
    use_ai=True,
    ai_config=ai_config,
    hometown_province="北京"
)
```
