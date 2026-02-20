# Faker-Plus 🚀

[中文](#-中文) | [English](#-english)

---

<p align="center">
  
  <br>
  <b>Faker-Plus: The Most Realistic Chinese Persona Generator</b>
  <br>
  <i>Empowering test data with deep logic consistency and AI soul.</i>
</p>

---

<h2 id="-中文">🇨🇳 中文</h2>

**Faker-Plus** 是一款建立在官方 `Faker` 之上的高能增强版包装。它专为严苛的中国大陆数据测试场景而生，通过建立**全层级逻辑耦合**（地理、生理、社会、金融），提供最坚固的仿真数据底座。

### ✨ 核心特性

- **🌍 全量区县级地理仿真**：集成数万条真实邮编记录，实现“省-市-区”降级匹配与邮编精准绑定。
- **🧬 生效逻辑闭环 (Logic-Coupling)**：
    - **互联网身份对齐**：用户名与邮箱关联姓名拼音（如：`wang.82@gmail.com`）。
    - **生长发育曲线**：未成年人（0-18岁）体征严格对准科学发育规律。
    - **职业-薪资链路**：高管不出现在农村，首席专家强制本科以上学历。
- **🤖 零依赖 AI 赋能**：无需安装第三方 SDK，通过 `urllib` 直连大模型，一键生成拟真人生故事与头像 Prompt。
- **⌨️ 生产力 CLI 工具**：全功能命令行交互，支持批量生成、参数滤波及 CSV/Markdown 导出。

---

### ⌨️ 命令行交互指南 (CLI Manual)

安装后，你可以通过 `faker-plus` 指令全局调用：

```bash
# 1. 基础生成 (指定性别与年龄)
faker-plus persona --gender 女 --age 18-30

# 2. 精准滤波 (INTJ 人格且月薪 50k 以上)
faker-plus persona --mbti INTJ --salary-min 50000

# 3. 批量生成并导出为 CSV
faker-plus persona --count 50 --format csv --output test_data.csv

# 4. 同步最新离线数据
faker-plus sync
```

---

<h2 id="-english">🇺🇸 English</h2>

**Faker-Plus** is a supercharged wrapper for the official `Faker`. It is specifically designed for high-fidelity Mainland China data generation, bridging logic gaps between geographical, biometric, social, and financial attributes.

### ✨ Core Features

- **🌍 County-level Geo Precision**: Integrated tens of thousands of real postal codes with smart fallback matching.
- **🧬 Deep Relationship Consistency**:
    - **Identity Alignment**: Usernames/Emails are semantically linked to name Pinyin.
    - **Pediatric Growth Curves**: Minors' height/weight follow scientific growth patterns.
    - **Vertical Scaling**: Job titles, education, and salaries are logically coupled by social status.
- **🤖 Zero-Dependency AI**: Direct connection to LLMs via `urllib` for generating coherent life stories and FLUX-ready image prompts.
- **⌨️ Powerful CLI**: Full-featured command-line tool for batch generation, advanced filtering, and CSV/MD export.

---

### 💻 Quick Start

**Installation**
```bash
pip install faker-plus
```

**Python API**
```python
from faker import Faker
from faker.providers.persona.zh_CN import Provider

fake = Faker('zh_CN')
fake.add_provider(Provider)

# Generate a high-fidelity persona
p = fake.persona(mbti="INTJ", age_range=(25, 30))
print(p['name'], p['mbti'], p['social']['job'])
```

---

### 📄 License
Distributed under the MIT License. See `LICENSE.txt` for more information.

---
<p align="center">Made with ❤️ by LING71671</p>
