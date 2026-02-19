import argparse
import sys
import json
from faker import Faker
from faker.providers.persona.zh_CN import Provider

def main():
    parser = argparse.ArgumentParser(description="Faker-Plus Persona CLI Tool - Generate realistic Chinese personas.")
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of personas to generate (default: 1)")
    parser.add_argument("-g", "--gender", choices=['男', '女', 'M', 'F'], help="Filter by gender")
    parser.add_argument("-a", "--age", type=str, help="Age range, e.g. '18-35'")
    parser.add_argument("-p", "--province", type=str, help="Hometown province filter")
    parser.add_argument("-j", "--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--ai", action="store_true", help="Include AI Life Story (requires API_KEY configuration)")

    args = parser.parse_args()

    fake = Faker('zh_CN')
    fake.add_provider(Provider)

    # Parse age range
    age_range = None
    if args.age:
        try:
            if '-' in args.age:
                low, high = map(int, args.age.split('-'))
                age_range = (low, high)
            else:
                val = int(args.age)
                age_range = (val, val)
        except ValueError:
            print(f"Error: Invalid age format '{args.age}'. Use 'min-max' or 'exact_age'.")
            sys.exit(1)

    personas = []
    for _ in range(args.count):
        persona_data = fake.persona(
            gender=args.gender,
            age_range=age_range,
            hometown_province=args.province,
            use_ai=args.ai
        )
        personas.append(persona_data)

    if args.json:
        print(json.dumps(personas, ensure_ascii=False, indent=2))
    else:
        for i, p in enumerate(personas):
            if args.count > 1:
                print(f"\n{'='*20} Persona #{i+1} {'='*20}")
            
            print(f"\033[1;34m[ 基本信息 ]\033[0m")
            print(f"  姓名: {p['name']} ({p['gender']}) | 年龄: {p['age']} | 民族: {p['ethnicity']}")
            print(f"  生日: {p['birth_date']} | 身份证: {p['ssn']}")
            
            print(f"\n\033[1;32m[ 地理位置 ]\033[0m")
            print(f"  户籍: {p['hometown']['province']} {p['hometown']['city']} {p['hometown']['area']}")
            print(f"  地址: {p['hometown']['address']} (邮编: {p['hometown']['postcode']})")
            print(f"  工作: {p['workplace']['province']} {p['workplace']['city']} {p['workplace']['area']}")
            
            print(f"\n\033[1;36m[ 社会属性 ]\033[0m")
            print(f"  学历: {p['social']['education']} | 状态: {p['social']['employment']}")
            print(f"  职业: {p['social']['job']} | 薪资: {p['social']['salary']}")
            print(f"  手机: {p['primary_phone']['number']} ({p['primary_phone']['location']})")
            
            print(f"\n\033[1;35m[ 互联网账号 ]\033[0m")
            print(f"  用户名: {p['username']} | 密码: {p['password']}")
            print(f"  邮箱: {p['email']}")
            print(f"  临时邮箱: {p['temp_email']} ({p['temp_email_url']})")
            
            print(f"\n\033[1;33m[ 金融 & 心理 ]\033[0m")
            print(f"  MBTI: {p['mbti']} | 银行: {p['bank_name']} | 卡号: {p['bank_card']}")

            if args.ai and 'ai_story' in p:
                print(f"\n\033[1;31m[ AI 人生轨迹 ]\033[0m")
                print(f"  {p['ai_story']}")

if __name__ == "__main__":
    main()
