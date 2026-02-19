import urllib.request
import json
import os
import subprocess
import sys

# ensure target directory
target_dir = os.path.join("b:\\faker-plus", "faker", "providers", "persona", "zh_CN")
os.makedirs(target_dir, exist_ok=True)

def build_areas():
    url = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/pcas-code.json"
    print("Downloading areas from GitHub raw...")
    # Add a fallback just in case
    # If GitHub is blocked, use gitee mirror or similar, but we try GitHub first
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
        areas_file = os.path.join(target_dir, "areas.json")
        with open(areas_file, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"Saved {areas_file}")
    except Exception as e:
        print(f"Warning: Failed to fetch from GitHub: {e}")
        # Try unpkg fallback
        url2 = "https://unpkg.com/china-division/dist/pcas-code.json"
        try:
            req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2, timeout=10) as r:
                data = json.loads(r.read().decode('utf-8'))
            areas_file = os.path.join(target_dir, "areas.json")
            with open(areas_file, "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"Saved {areas_file} from fallback.")
        except Exception as e2:
            print(f"Failed fallback: {e2}")

def build_phones():
    print("Installing 'phone' library from PyPI...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "phone", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
    from phone import Phone
    p = Phone()
    
    # The `phone` library usually has phone.dat containing extensive mappings.
    # In python implementation, it reads from phone.dat.
    # To reverse map it: Province -> City -> List[prefix]
    
    # We will iterate through 1300000 to 1999999 (approx valid mobile prefixes)
    # This might take a minute, so we sample known prefixes to speed it up
    print("Generating phones.json...")
    mapping = {}
    
    # Instead of full brute force, we can read the raw file if accessible, or just try common prefix ranges
    # 13x, 14x, 15x, 16x, 17x, 18x, 19x
    head_list = [
        "130","131","132","133","134","135","136","137","138","139",
        "145","147","149",
        "150","151","152","153","155","156","157","158","159",
        "166", "167", "162",
        "170","171","172","173","174","175","176","177","178","179",
        "180","181","182","183","184","185","186","187","188","189",
        "190","191","192","193","195","196","197","198","199"
    ]
    
    from collections import defaultdict
    # Structure: mapping[province][city] = [list of 7-digit prefixes]
    # Fast approach: loop 0000 to 9999 for each head
    
    # To avoid huge computation, let's just create a sparse but realistic map
    # mapping structure: { "北京": ["1301011", "1301012"...] }
    # Let's take a subset that is "good enough" for Faker
    
    cities_count = 0
    prefixes_found = 0
    
    for head in head_list:
        for mid in range(0, 10000, 111): # step by 111 to get some sparse subset (e.g. 0000, 0111, 0222)
            prefix = f"{head}{mid:04d}"
            try:
                info = p.find(prefix)
                if info and 'province' in info and 'city' in info:
                    prov = info['province']
                    city = info['city']
                    if prov not in mapping:
                        mapping[prov] = {}
                    if city not in mapping[prov]:
                        mapping[prov][city] = []
                    mapping[prov][city].append(prefix)
                    prefixes_found += 1
            except:
                pass
                
    phones_file = os.path.join(target_dir, "phones.json")
    with open(phones_file, "w", encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False)
    print(f"Saved {phones_file} with {prefixes_found} prefixes across multiple cities.")

def build_postcodes():
    url = "https://raw.githubusercontent.com/mumuy/data_post/master/list.json"
    print("Downloading postcodes from GitHub raw...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode('utf-8'))
        postcodes_file = os.path.join(target_dir, "postcodes.json")
        with open(postcodes_file, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"Saved {postcodes_file}")
    except Exception as e:
        print(f"Warning: Failed to fetch postcodes from GitHub: {e}")
        # Try unpkg fallback if possible (but mumuy might not be on unpkg)

if __name__ == "__main__":
    build_areas()
    build_phones()
    build_postcodes()
    print("Done building dictionaries.")
