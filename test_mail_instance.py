from faker import Faker
from faker.providers.persona.zh_CN import Provider
import json

fake = Faker('zh_CN')
fake.add_provider(Provider)

p = fake.persona()

print(f"姓名: {p['name']}")
print(f"临时邮箱: {p['temp_email']}")
print(f"跳转链接 (点击直达收件箱): {p['temp_email_url']}")

print("-" * 30)
print("完整数据如下:")
print(json.dumps(p, ensure_ascii=False, indent=2))
