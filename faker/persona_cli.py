import argparse
import sys
import json
import csv
import os
from faker import Faker
from faker.providers.persona.zh_CN import Provider

BANNER = r"""
\033[1;36m  _____      _              _____  _             
 |  ___|    | |            |  __ \| |            
 | |__  __ _| | _____ _ __ | |__) | |_   _ ___  
 |  __|/ _` | |/ / _ \ '__||  ___/| | | | / __| 
 | |  | (_| |   <  __/ |   | |    | | |_| \__ \ 
 |_|   \__,_|_|\_\___|_|   |_|    |_|\__,_|___/ \033[0m
\033[1;30m           Realistic Chinese Persona v0.2.0\033[0m
"""

def format_persona_text(p, i, count):
    """ ANSI formatted text output for humans """
    output = []
    if count > 1:
        output.append(f"\n\033[1;37m{'='*25} Persona #{i+1} {'='*25}\033[0m")
    
    output.append(f"\033[1;34m[ 基本信息 ]\033[0m")
    output.append(f"  姓名: {p['name']} ({p['gender']}) | 年龄: {p['age']} | 民族: {p['ethnicity']}")
    output.append(f"  生日: {p['birth_date']} | 身份证: {p['ssn']}")
    
    output.append(f"\n\033[1;32m[ 地理位置 ]\033[0m")
    output.append(f"  户籍: {p['hometown']['province']} {p['hometown']['city']} {p['hometown']['area']}")
    output.append(f"  地址: {p['hometown']['address']} (邮编: {p['hometown']['postcode']})")
    output.append(f"  工作地: {p['workplace']['province']} {p['workplace']['city']} {p['workplace']['area']}")
    
    output.append(f"\n\033[1;36m[ 社会属性 ]\033[0m")
    output.append(f"  学历: {p['social']['education']} | 状态: {p['social']['employment']}")
    output.append(f"  职业: {p['social']['job']} | 薪资: {p['social']['salary']}")
    output.append(f"  手机: {p['primary_phone']['number']} ({p['primary_phone']['location']})")
    
    output.append(f"\n\033[1;35m[ 互联网账号 ]\033[0m")
    output.append(f"  用户名: {p['username']} | 密码: \033[4;37m{p['password']}\033[0m")
    output.append(f"  邮箱: {p['email']}")
    output.append(f"  临时邮箱: {p['temp_email']} ({p['temp_email_url']})")
    
    output.append(f"\n\033[1;33m[ 金融 & 心理 ]\033[0m")
    output.append(f"  MBTI: {p['mbti']} | 银行: {p['bank_name']} | 卡号: {p['bank_card']}")

    if 'ai_story' in p:
        output.append(f"\n\033[1;31m[ AI 人生轨迹 ]\033[0m")
        output.append(f"  {p['ai_story']}")
    
    return "\n".join(output)

def export_csv(personas, filename):
    if not personas: return
    keys = ["name", "gender", "age", "ssn", "username", "email", "bank_name", "bank_card", "mbti"]
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(personas)
    print(f"\033[1;32mSuccessfully exported {len(personas)} personas to {filename}\033[0m")

def export_markdown(personas, filename):
    if not personas: return
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Faker-Plus Generated Personas\n\n")
        for i, p in enumerate(personas):
            f.write(f"## {i+1}. {p['name']} ({p['gender']})\n")
            f.write(f"- **年龄**: {p['age']}\n")
            f.write(f"- **身份证**: `{p['ssn']}`\n")
            f.write(f"- **籍贯**: {p['hometown']['province']} {p['hometown']['city']}\n")
            f.write(f"- **职业**: {p['social']['job']} ({p['social']['salary']})\n")
            f.write(f"- **MBTI**: {p['mbti']}\n")
            f.write("---\n\n")
    print(f"\033[1;32mSuccessfully exported {len(personas)} personas to {filename}\033[0m")

def handle_persona(args):
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
            return

    personas = []
    for i in range(args.count):
        if args.count > 10 and not args.json:
            print(f"\rGenerating: {i+1}/{args.count}...", end="", flush=True)
            
        persona_data = fake.persona(
            gender=args.gender,
            age_range=age_range,
            hometown_province=args.province,
            mbti=args.mbti,
            education=args.degree,
            use_ai=args.ai
        )
        personas.append(persona_data)

    if args.count > 10 and not args.json:
        print("\nGeneration complete.")

    if args.json:
        print(json.dumps(personas, ensure_ascii=False, indent=2))
    elif args.format == 'csv':
        export_csv(personas, args.output or "personas.csv")
    elif args.format == 'md':
        export_markdown(personas, args.output or "personas.md")
    else:
        for i, p in enumerate(personas):
            print(format_persona_text(p, i, args.count))

def handle_sync(args):
    print("\033[1;36mStarting data synchronization...\033[0m")
    try:
        from build_dicts import build_postcodes
        build_postcodes()
        print("\033[1;32mSuccessfully syncronized postcode database.\033[0m")
    except Exception as e:
        print(f"\033[1;31mSync failed: {e}\033[0m")

def main():
    parser = argparse.ArgumentParser(prog="faker-plus", description="Faker-Plus Full-Featured CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Persona Subcommand
    persona_parser = subparsers.add_parser("persona", help="Generate realistic Chinese personas")
    persona_parser.add_argument("-c", "--count", type=int, default=1, help="Number of personas to generate")
    persona_parser.add_argument("-g", "--gender", choices=['男', '女', 'M', 'F'], help="Filter by gender")
    persona_parser.add_argument("-a", "--age", type=str, help="Age range (e.g. 18-35)")
    persona_parser.add_argument("-p", "--province", type=str, help="Hometown province filter")
    persona_parser.add_argument("--mbti", type=str, help="Specific MBTI type")
    persona_parser.add_argument("--degree", type=str, help="Education level")
    persona_parser.add_argument("--ai", action="store_true", help="Enable AI Life Story")
    persona_parser.add_argument("-j", "--json", action="store_true", help="Output in JSON to stdout")
    persona_parser.add_argument("-f", "--format", choices=['text', 'csv', 'md'], default='text', help="Output format")
    persona_parser.add_argument("-o", "--output", type=str, help="Output file path (for csv/md)")

    # Sync Subcommand
    subparsers.add_parser("sync", help="Synchronize and update offline dictionary data")

    # Config Subcommand (Placeholder)
    config_parser = subparsers.add_parser("config", help="Manage tool configurations (e.g. API keys)")
    config_parser.add_argument("--set-key", nargs=2, metavar=('KEY', 'VALUE'), help="Set a configuration key")

    args = parser.parse_args()

    if args.command == "persona":
        if not args.json:
            print(BANNER)
        handle_persona(args)
    elif args.command == "sync":
        handle_sync(args)
    elif args.command == "config":
        if args.set_key:
            print(f"Config set: {args.set_key[0]} = {args.set_key[1]} (Mocked)")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
