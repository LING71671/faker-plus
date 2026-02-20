import json
import os
import random
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from .. import Provider as PersonaProvider


class Provider(PersonaProvider):
    """
    Provider for generating a logically consistent Chinese Persona.
    """
    _areas_data = None
    _phones_data = None
    _postcodes_data = None
    _villages_data = None
    _pinyin_map = {
        "王": "wang", "李": "li", "张": "zhang", "刘": "liu", "陈": "chen",
        "杨": "yang", "黄": "huang", "赵": "zhao", "吴": "wu", "周": "zhou",
        "徐": "xu", "孙": "sun", "马": "ma", "朱": "zhu", "胡": "hu",
        "林": "lin", "郭": "guo", "何": "he", "高": "gao", "罗": "luo",
        "郑": "zheng", "梁": "liang", "谢": "xie", "唐": "tang", "宋": "song",
        "韩": "han", "曹": "cao", "许": "xu", "邓": "deng", "萧": "xiao",
        "冯": "feng", "曾": "zeng", "程": "cheng", "蔡": "cai", "潘": "pan",
        "袁": "yuan", "于": "yu", "董": "dong", "余": "yu", "苏": "su",
        "叶": "ye", "吕": "lv", "魏": "wei", "蒋": "jiang", "田": "tian",
        "杜": "du", "丁": "ding"
    }

    def _filter_by_fields(self, data: dict, fields: list) -> dict:
        """
        根据用户指定的 fields 列表过滤生成的画像字典，支持诸如 'hometown.postcode' 等嵌套路径。
        """
        filtered_p = {}
        for f in fields:
            f = f.strip()
            if not f:
                continue
            
            parts = f.split('.')
            current_src = data
            current_dest = filtered_p
            
            valid = True
            for i, part in enumerate(parts):
                if isinstance(current_src, dict) and part in current_src:
                    if i == len(parts) - 1:
                        current_dest[part] = current_src[part]
                    else:
                        if part not in current_dest:
                            current_dest[part] = {}
                        current_dest = current_dest[part]
                        current_src = current_src[part]
                else:
                    valid = False
                    break
        return filtered_p

    @classmethod
    def _load_areas(cls) -> List[Dict]:
        if cls._areas_data is None:
            path = os.path.join(os.path.dirname(__file__), 'areas.json')
            with open(path, 'r', encoding='utf-8') as f:
                cls._areas_data = json.load(f)
        return cls._areas_data

    @classmethod
    def _load_phones(cls) -> Dict:
        if cls._phones_data is None:
            path = os.path.join(os.path.dirname(__file__), 'phones.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cls._phones_data = json.load(f)
            except FileNotFoundError:
                cls._phones_data = {}
        return cls._phones_data

    @classmethod
    def _load_postcodes(cls):
        if cls._postcodes_data is None:
            import os, json
            path = os.path.join(os.path.dirname(__file__), "postcodes.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                index = {}
                for pc, addr in raw_data.items():
                    index[addr] = pc
                cls._postcodes_data = index
            else:
                cls._postcodes_data = {}
        return cls._postcodes_data

    @classmethod
    def _load_villages(cls) -> Dict:
        if cls._villages_data is None:
            import gzip
            path = os.path.join(os.path.dirname(__file__), 'villages.json.gz')
            try:
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    cls._villages_data = json.load(f)
            except FileNotFoundError:
                cls._villages_data = {}
        return cls._villages_data

    def _ssn_checksum(self, ssn_17_digits: str) -> str:
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = "10X98765432"
        total = sum(int(ssn_17_digits[i]) * factors[i] for i in range(17))
        return check_codes[total % 11]

    def _random_date_between(self, min_age: int, max_age: int) -> date:
        today = date.today()
        start = today.replace(year=today.year - max_age)
        end = today.replace(year=today.year - min_age)
        delta = end - start
        random_days = self.random_int(min=0, max=delta.days)
        return start + timedelta(days=random_days)

    def persona(
        self,
        gender: Optional[str] = None,
        age_range: Optional[tuple] = None,
        hometown_province: Optional[str] = None,
        hometown_city: Optional[str] = None,
        has_second_phone: bool = False,
        work_province: Optional[str] = None,
        work_city: Optional[str] = None,
        use_ai: bool = False,
        ai_config: Optional[Dict] = None,
        fields: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a Chinese virtual persona strictly adhering to geographic, logical and ID verification constraints.
        Supports extensive detail fields via kwargs: 
        (height, weight, blood_type, username, password, education, job, salary, security_question, security_answer, etc.)
        """
        areas = self._load_areas()
        phones = self._load_phones()

        # 1. Resolve geographic constraints (Hometown)
        prov_list = areas
        if hometown_province:
            filtered = [p for p in prov_list if hometown_province in p['name']]
            if filtered:
                prov_list = filtered

        prov_data = self.random_element(prov_list)
        prov_name = prov_data['name']

        city_list = prov_data.get('children', [])
        if not city_list:
            city_list = [prov_data]

        if hometown_city:
            filtered = [c for c in city_list if hometown_city in c['name']]
            if filtered:
                city_list = filtered

        city_data = self.random_element(city_list)
        city_name = city_data['name']

        area_list = city_data.get('children', [])
        if not area_list:
            area_list = [city_data]

        area_data = self.random_element(area_list)
        area_code = area_data['code']
        area_name = area_data['name']

        town_list = area_data.get('children', [])
        if town_list:
            town_data = self.random_element(town_list)
            town_name = town_data['name']
            town_code = town_data.get('code', '')
        else:
            town_name = ""
            town_code = ""

        # 2. Resolve Gender and Age
        if gender not in ['男', '女', 'M', 'F']:
            gender_val = self.random_element(['男', '女'])
        else:
            gender_val = '男' if gender in ['男', 'M'] else '女'

        is_male = gender_val == '男'

        if not age_range or len(age_range) != 2:
            age_range = (18, 65)

        birth_date = self._random_date_between(age_range[0], age_range[1])
        age = date.today().year - birth_date.year - ((date.today().month, date.today().day) < (birth_date.month, birth_date.day))

        # 3. Generate SSN
        date_str = birth_date.strftime('%Y%m%d')
        seq_code = f"{self.random_int(min=0, max=99):02d}"
        gender_digit = self.random_element([1, 3, 5, 7, 9]) if is_male else self.random_element([0, 2, 4, 6, 8])

        ssn_17 = f"{area_code}{date_str}{seq_code}{gender_digit}"
        checksum = self._ssn_checksum(ssn_17)
        ssn = f"{ssn_17}{checksum}"

        # 4. Define Address Generation Logic (Internal to support separation)
        def generate_full_address(p_data, c_data, a_data, f_urban=False):
            t_list = a_data.get('children', [])
            if f_urban and t_list:
                urban_t = [t for t in t_list if any(kw in t['name'] for kw in ["街道", "地区", "开发区"])]
                if urban_t: t_list = urban_t

            if not t_list:
                t_n, t_c = "", ""
            else:
                t_obj = self.random_element(t_list)
                t_n, t_c = t_obj['name'], t_obj.get('code', '')

            is_u = False
            if t_n:
                if any(kw in t_n for kw in ["街道", "地区", "社区", "开发区"]): is_u = True
                elif any(kw in t_n for kw in ["乡", "镇", "林场", "农场"]): is_u = False
                else: is_u = "区" in a_data['name'] or "市" in a_data['name']
            else:
                is_u = "区" in a_data['name'] or "街道" in a_data['name']

            # Town-level villages logic
            v_list = villages.get(t_c, []) if t_c else []
            if is_u:
                b_estate = ""
                if v_list:
                    u_vp = [v for v in v_list if any(kw in v for kw in ["社区", "居委会"])]
                    if not u_vp: u_vp = v_list
                    b_estate = self.random_element(u_vp)
                    for s in ["居民委员会", "社区居委会", "居委会", "社区", "村民委员会", "村委会"]:
                        b_estate = b_estate.replace(s, "")
                if not b_estate or len(b_estate) < 2:
                    b_estate = self.random_element(["阳光", "时代", "世纪", "国际", "理想", "中心", "滨江", "华府", "万科", "金地"])
                e_suffix = self.random_element(["小区", "花园", "苑", "家园", "新村", "府"])
                e_name = f"{b_estate}{e_suffix}"
                r_name = self.random_element(["朝阳", "建设", "胜利", "解放", "中山", "人民", "新华"]) + self.random_element(["路", "街"])
                full_street = f"{t_n}{r_name}{e_name}{self.random_int(1,50)}号楼{self.random_int(1,5)}单元{self.random_int(1,30)}0{self.random_int(1,4)}室"
            else:
                v_name = ""
                if v_list:
                    r_vp = [v.replace("村民委员会", "").replace("村委会", "").replace("居委会", "") for v in v_list]
                    v_name = self.random_element(r_vp)
                    if v_name and not any(v_name.endswith(s) for s in ["村", "庄", "队"]): v_name += "村"
                if not v_name:
                    v_name = f"{self.random_element(['张家', '李家', '王家', '赵家', '大', '小', '新'])}{self.random_element(['村', '庄', '屯'])}"
                    if not v_name.endswith("村"): v_name += "村"
                full_street = f"{t_n}{v_name}{self.random_int(1,100)}号"

            return {
                "province": p_data['name'],
                "city": c_data['name'],
                "area": a_data['name'],
                "town": t_n,
                "is_urban": is_u,
                "address": f"{p_data['name']}{c_data['name']}{a_data['name']}{full_street}"
            }

        # Generate Hometown
        villages = self._load_villages()
        hometown_data = generate_full_address(prov_data, city_data, area_data)

        # 5. Resolve Social/Job constraints to determine Workplace
        job_val_pre = kwargs.get("job") or ""
        is_high_end = any(kw in job_val_pre for kw in ["总", "CEO", "CTO", "高管", "总裁", "架构师", "专家"])

        if work_province:
            w_prov_list = [p for p in areas if work_province in p['name']] if work_province else areas
            wp_data = self.random_element(w_prov_list)
            wc_list = wp_data.get('children', [wp_data])
            wc_data = self.random_element([c for c in wc_list if work_city in c['name']]) if work_city else self.random_element(wc_list)
            wa_list = wc_data.get('children', [wc_data])
            wa_data = self.random_element(wa_list)
        elif is_high_end and not hometown_data['is_urban']:
            t1_provs = ["北京", "上海", "广东", "江苏", "浙江"]
            wp_data = self.random_element([p for p in areas if any(t1 in p['name'] for t1 in t1_provs)])
            wc_data = self.random_element(wp_data.get('children', [wp_data]))
            wa_data = self.random_element(wc_data.get('children', [wc_data]))
        else:
            wp_data, wc_data, wa_data = prov_data, city_data, area_data

        workplace_data = generate_full_address(wp_data, wc_data, wa_data, f_urban=is_high_end)

        # 6. Generate Primary Phone based on Workplace
        def get_phone_number(p_name: str, c_name: str) -> str:
            p_key = p_name.replace("市", "").replace("省", "").replace("自治区", "")
            matched_prov = next((k for k in phones.keys() if p_key in k or k in p_key), None)
            if matched_prov:
                city_dict = phones[matched_prov]
                c_key = c_name.replace("市", "").replace("地区", "").replace("盟", "")
                if p_key in ["北京", "上海", "天津", "重庆"] and c_key in ["辖区", "市辖区", "县"]:
                    c_key = p_key
                matched_city = next((k for k in city_dict.keys() if c_key in k or k in c_key), None)
                if matched_city:
                    prefixes = city_dict[matched_city]
                    if prefixes:
                        prefix = self.random_element(prefixes)
                        suffix = f"{self.random_int(min=0, max=9999):04d}"
                        return f"{prefix}{suffix}"
            try: return self.generator.phone_number()
            except AttributeError: return f"13{self.random_int(min=0,max=9)}{self.random_int(min=0,max=99999999):08d}"

        # 6. Generate Primary Phone based on Workplace
        primary_phone = get_phone_number(str(workplace_data['province']), str(workplace_data['city']))

        # 7. Determine Name (Gender already known)
        if is_male:
            try: name = kwargs.get("name") or getattr(self.generator, "name_male")()
            except AttributeError: name = kwargs.get("name") or self.generator.name()
        else:
            try: name = kwargs.get("name") or getattr(self.generator, "name_female")()
            except AttributeError: name = kwargs.get("name") or self.generator.name()

        # 8. Ethnicity and Identity (Geo-aware distribution)
        ethnicity = kwargs.get("ethnicity")
        if not ethnicity:
            e_weights = {"汉族": 91}
            p_n = str(prov_name)
            if "西藏" in p_n: e_weights["藏族"] = 50
            elif "新疆" in p_n: e_weights["维吾尔族"] = 45; e_weights["哈萨克族"] = 5
            elif "内蒙古" in p_n: e_weights["蒙古族"] = 20
            elif "宁夏" in p_n: e_weights["回族"] = 30
            elif "广西" in p_n: e_weights["壮族"] = 35
            elif "云南" in p_n: e_weights["傣族"] = 10; e_weights["彝族"] = 10; e_weights["白族"] = 5
            elif "吉林" in p_n or "辽宁" in p_n: e_weights["满族"] = 15; e_weights["朝鲜族"] = 5
            
            others = ["苗族", "回族", "土家族", "彝族", "满族", "壮族", "布依族"]
            for o in others:
                if o not in e_weights: e_weights[o] = 1
            
            total_w = sum(e_weights.values())
            r_val = random.uniform(0, total_w)
            cursor = 0
            for e_name, w in e_weights.items():
                cursor += w
                if r_val <= cursor:
                    ethnicity = e_name
                    break
        
        # Postcode Logic: Load Full Database
        full_pc_index = self._load_postcodes()
        
        def generate_realistic_postcode(p_n, c_n, a_n):
            # Precision candidates (Specific to General)
            # Handle Municipality redundancy (e.g., Beijing Beijing)
            clean_p = p_n.replace('省','').replace('市','').replace('自治区','')
            clean_c = c_n.replace('市','').replace('地区','').replace('盟','')
            
            candidates = [
                f"{p_n}{c_n}{a_n}",
                f"{clean_p}{c_n}{a_n}",
                f"{c_n}{a_n}",
                a_n, # Direct County/District match (vulnerable to duplicate names, but usually fine in context)
                f"{p_n}{c_n}",
                p_n
            ]
            for cand in candidates:
                if cand in full_pc_index:
                    return full_pc_index[cand]
            
            # Fallback to prefix-based random generation if not in DB
            prefix = "00"
            postcode_map = {
                "北京": "10", "上海": "20", "天津": "30", "重庆": "40",
                "辽宁": "11", "吉林": "13", "黑龙江": "15", "江苏": "21",
                "浙江": "31", "安徽": "23", "福建": "35", "内蒙古": "01",
                "江西": "33", "山东": "25", "河南": "45", "湖北": "43",
                "湖南": "41", "广东": "51", "广西": "53", "海南": "57",
                "四川": "61", "贵州": "55", "云南": "65", "西藏": "85",
                "陕西": "71", "甘肃": "73", "青海": "81", "宁夏": "75",
                "新疆": "83", "河北": "05", "山西": "03"
            }
            for k, v in postcode_map.items():
                if k in p_n:
                    prefix = v
                    break
            return f"{prefix}{self.random_int(min=0, max=9999):04d}"

        # 8. Physical attributes with realistic distributions
        # Blood types in China: O~32%, A~28%, B~30%, AB~10%
        # Rh- is rare in China: ~0.3%
        def get_realistic_blood():
            bt = self.random_element(["O"] * 32 + ["A"] * 28 + ["B"] * 30 + ["AB"] * 10)
            rh = "-" if random.random() < 0.003 else "+"
            return f"{bt}{rh}"

        # 8. Physical attributes with realistic distributions (分段式生长曲线)
        # Pediatric Growth Curve (18.5 - 27 BMI for adults, specific for minors)
        if age < 3:
            h_min, h_max = 50, 100
            bmi_min, bmi_max = 14, 19
        elif age < 7:
            h_min, h_max = 90, 130
            bmi_min, bmi_max = 13, 18
        elif age < 13:
            h_min, h_max = 120, 165
            bmi_min, bmi_max = 14, 21
        elif age < 18:
            h_min, h_max = (155, 185) if is_male else (150, 175)
            bmi_min, bmi_max = 16, 24
        else: # Adult
            h_min, h_max = (165, 190) if is_male else (155, 175)
            bmi_min, bmi_max = 18.5, 27
            
        h_val = self.random_int(min=h_min, max=h_max)
        bmi = random.uniform(bmi_min, bmi_max)
        w_val = int(bmi * (h_val/100)**2)
            
        height = kwargs.get("height") or f"{h_val}cm"
        weight = kwargs.get("weight") or f"{w_val}kg"
        blood_type = kwargs.get("blood_type") or get_realistic_blood()

        # Web / Account attributes (姓名-账号耦合)
        # Simple name-based username logic
        def get_linked_identity(full_name: str):
            # If name is '张三', try 'zhangsan', 'san.zhang', etc.
            surname = full_name[0]
            pinyin_prefix = self._pinyin_map.get(surname, "")
            if pinyin_prefix:
                variant = self.random_element([
                    f"{pinyin_prefix}.{self.random_int(10, 999)}",
                    f"{pinyin_prefix}{self.random_int(1980, 2010)}",
                    f"{self.generator.user_name()[:3]}.{pinyin_prefix}"
                ])
                return variant
            return self.generator.user_name()

        username = kwargs.get("username") or get_linked_identity(name)
        password = kwargs.get("password") or self.generator.password()
        guid = kwargs.get("guid") or str(self.generator.uuid4())
        ua = kwargs.get("user_agent") or self.generator.user_agent()
        os_name = kwargs.get("os") or self.random_element(["Windows 10", "Windows 11", "macOS Sonoma", "Ubuntu 22.04", "Android 14", "iOS 17"])
        web_home = kwargs.get("web_home") or self.generator.url()
        
        temp_mail_configs = {
            'yopmail.com': 'https://yopmail.com/zh/?',
            'yopmail.net': 'https://yopmail.com/zh/?',
            'cool.fr.nf': 'https://yopmail.com/zh/?',
            'jetable.fr.nf': 'https://yopmail.com/zh/?'
        }
        temp_domain = self.random_element(list(temp_mail_configs.keys()))
        temp_email = kwargs.get("temp_email") or f"{username}@{temp_domain}"
        temp_email_url = f"{temp_mail_configs[temp_domain]}{username}"

        # Social / background with age constraints
        if age < 7:
            education_opts = ["幼儿"]
            employment_opts = ["在读"]
            job_val = "无"
            salary_val = "￥0"
        elif age < 13:
            education_opts = ["小学"]
            employment_opts = ["在读"]
            job_val = "学生"
            salary_val = "￥0"
        elif age < 16:
            education_opts = ["初中"]
            employment_opts = ["在读"]
            job_val = "学生"
            salary_val = "￥0"
        elif age < 19:
            education_opts = ["高中", "中专"]
            employment_opts = ["在读"]
            job_val = "学生"
            salary_val = "￥0"
        elif age < 23:
            education_opts = ["大专", "本科", "职业技能培训"]
            employment_opts = ["在读", "在职", "待业"]
            job_val = "学生" if random.random() < 0.8 else self.generator.job()
            salary_val = "￥0" if "在读" in employment_opts else f"￥{self.random_int(min=30, max=80) * 100}"
        elif age < 60:
            education_opts = ["大专", "本科", "硕士", "博士", "MBA", "职业技能培训"]
            employment_opts = ["在职", "待业", "自由职业"]
            job_val = self.generator.job()
            salary_val = f"￥{self.random_int(min=50, max=500) * 100}"
        else: # 60+
            education_opts = ["高中", "大专", "本科", "硕士", "博士"]
            employment_opts = ["退休", "自由职业"]
            job_val = self.generator.job() if random.random() < 0.2 else "退休人员"
            salary_val = f"￥{self.random_int(min=30, max=120) * 100}"

        education = kwargs.get("education") or self.random_element(education_opts)
        employment = kwargs.get("employment") or self.random_element(employment_opts)
        job = kwargs.get("job") or job_val

        # Logic Hardening: Education/Age Door for Specific Jobs
        if any(kw in job for kw in ["总", "CEO", "总裁", "主任"]):
            if age < 30: age = 30 + (age % 10) # Enforce age
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专"]: 
                education = self.random_element(["本科", "硕士", "MBA"])
        if any(kw in job for kw in ["架构师", "专家", "研究员", "科学家"]):
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专"]:
                education = self.random_element(["本科", "硕士", "博士"])
        
        # New: Salary constraint based on Job
        job_salary_mapping = [
            (["总", "高管", "CEO", "CTO", "CFO", "总裁", "主任"], (30000, 150000)),
            (["经理", "总监", "经理", "主管"], (12000, 45000)),
            (["架构师", "专家", "科学家"], (25000, 80000)),
            (["工程师", "开发", "程序员", "技术"], (10000, 40000)),
            (["教师", "老师", "教授", "讲师", "教员"], (5000, 25000)),
            (["医生", "护士", "医疗"], (6000, 40000)),
            (["销售", "业务", "代理"], (4000, 35000)),
            (["客服", "行政", "文员", "专员"], (4000, 12000)),
            (["司机", "快递", "外卖", "配送"], (5000, 15000)),
            (["厨师", "服务员", "营业员", "保安"], (3500, 10000)),
            (["保洁", "家政", "保姆"], (3000, 7000)),
            (["退休"], (3000, 12000)),
            (["学生", "小学", "初中", "高中", "幼儿", "无"], (0, 0))
        ]

        # New: Geo-Salary Multiplier based on Job Location
        tier1_cities = ["北京", "上海", "广州", "深圳"]
        new_tier1_cities = ["成都", "杭州", "武汉", "南京", "天津", "西安", "苏州", "郑州", "长沙", "东莞", "沈阳", "青岛", "合肥", "佛山", "宁波"]
        
        # Determine City Tier Factor for Workplace
        city_factor = 1.0
        loc_prov = str(workplace_data.get('province', ''))
        loc_city = str(workplace_data.get('city', ''))

        if any(c in loc_prov or c in loc_city for c in tier1_cities):
            city_factor = random.uniform(1.3, 1.6)
        elif any(c in loc_prov or c in loc_city for c in new_tier1_cities):
            city_factor = random.uniform(1.1, 1.3)
        elif "省" in loc_prov or "自治区" in loc_prov:
            city_factor = random.uniform(0.8, 1.0)
        else:
            city_factor = random.uniform(0.6, 0.8)

        # Rural factor (based on workplace environment)
        rural_factor = random.uniform(0.6, 0.8) if not workplace_data.get('is_urban', True) else 1.0

        def get_salary_by_job(job_name):
            base_val = 8000
            for keywords, range_vals in job_salary_mapping:
                if any(kw in job_name for kw in keywords):
                    base_val = self.random_int(min=range_vals[0], max=range_vals[1])
                    break
            
            # Apply multipliers
            final_val = float(base_val) * city_factor * rural_factor
            return f"￥{int(final_val // 100 * 100)}"

        if "在读" in employment or "待业" in employment or job in ["无", "幼儿", "学生"]:
            salary = "￥0"
        else:
            salary = kwargs.get("salary") or get_salary_by_job(job)
        
        # MBTI personality type
        mbti_list = [
            "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"
        ]
        mbti = kwargs.get("mbti") or self.random_element(mbti_list)

        # Bank Card (Luhn standard)
        def generate_luhn(prefix, length=19):
            digits = [int(d) for d in str(prefix)]
            while len(digits) < length - 1:
                digits.append(self.random_int(0, 9))
            
            # Luhn calculation
            checksum = 0
            for i, d in enumerate(reversed(digits)):
                if i % 2 == 0:
                    d *= 2
                    if d > 9: d -= 9
                checksum += d
            check_digit = (10 - (checksum % 10)) % 10
            digits.append(check_digit)
            return "".join(map(str, digits))

        bank_name = "无"
        bank_card = "无"
        if age >= 10:
            bank_bins = {
                "中国工商银行": ["622202", "621226", "622208"],
                "中国农业银行": ["622848", "622845", "622822"],
                "中国银行": ["621661", "621660", "456350"],
                "中国建设银行": ["621700", "621081", "623668"]
            }
            bank_name = self.random_element(list(bank_bins.keys()))
            bin_val = self.random_element(bank_bins[bank_name])
            bank_card = kwargs.get("bank_card") or generate_luhn(bin_val)

        # Contextual Security Question/Answer
        sec_pairs = [
            ("你母亲的名字叫什么？", self.random_element(["王淑芳", "李美玲", "张爱华", "刘兰英"])),
            ("你出生在哪个城市？", hometown_data['city']),
            ("你的首只宠物的中文名字？", self.random_element(["小花", "大黄", "球球", "皮皮"])),
            ("你的小学老师姓什么？", self.random_element(["陈", "周", "吴", "郑", "何"]))
        ]
        chosen_pair = self.random_element(sec_pairs)
        sec_q = kwargs.get("security_question") or chosen_pair[0]
        sec_a = kwargs.get("security_answer") or chosen_pair[1]

        result = {
            "name": name,
            "gender": gender_val,
            "age": age,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "ssn": ssn,
            "email": f"{username}@{self.generator.free_email_domain()}",
            "temp_email": temp_email,
            "temp_email_url": temp_email_url,
            "username": username,
            "password": password,
            "ethnicity": ethnicity,
            "bank_card": bank_card,
            "bank_name": bank_name,
            "mbti": mbti,
            "physical": {
                "height": height,
                "weight": weight,
                "blood_type": blood_type
            },
            "hometown": {
                "province": hometown_data['province'],
                "city": hometown_data['city'],
                "area": hometown_data['area'],
                "address": hometown_data['address'],
                "postcode": generate_realistic_postcode(
                    hometown_data['province'], 
                    hometown_data['city'], 
                    hometown_data['area']
                )
            },
            "workplace": {
                "province": workplace_data['province'],
                "city": workplace_data['city'],
                "area": workplace_data['area'],
                "address": workplace_data['address']
            },
            "primary_phone": {
                "number": primary_phone,
                "location": workplace_data['city'] if workplace_data['city'] not in ["市辖区", "县", "省直辖县级行政区划"] else workplace_data['province']
            },
            "social": {
                "education": education,
                "employment": employment,
                "job": job,
                "salary": salary,
                "security_question": sec_q,
                "security_answer": sec_a
            },
            "internet": {
                "guid": guid,
                "user_agent": ua,
                "os": os_name,
                "web_home": web_home
            }
        }

        # 7. Secondary Phone / Work location
        if has_second_phone:
            if not work_province:
                other_provs = [p for p in areas if p['name'] != prov_name]
                if not other_provs:
                    other_provs = areas
                w_prov = self.random_element(other_provs)
                work_prov_name = w_prov['name']
                w_city_list = w_prov.get('children', [w_prov])
                w_city = self.random_element(w_city_list)['name']
            else:
                work_prov_name = work_province
                work_city_list = next((p.get('children', [p]) for p in areas if work_province in p['name']), areas)
                w_city = work_city if work_city else self.random_element(work_city_list)['name']

            w_addr_prov_key = work_prov_name.replace("市", "").replace("省", "").replace("自治区", "")
            w_addr_city = w_city
            if w_addr_prov_key in ["北京", "上海", "天津", "重庆"] and w_city in ["市辖区", "县"]:
                w_addr_city = ""
            elif w_city in ["省直辖县级行政区划", "自治区直辖县级行政区划"]:
                w_addr_city = ""

            secondary_phone = get_phone_number(work_prov_name, w_city)
            result["secondary_phone"] = {
                "number": secondary_phone,
                "location": f"{work_prov_name}{w_addr_city}" if w_addr_city else work_prov_name
            }
            result["work_location"] = {
                "province": work_prov_name,
                "city": w_city
            }
        elif not has_second_phone and "secondary_phone" in result:
            del result["secondary_phone"]

        # 8. Add AI story
        if use_ai:
            from .ai_story import generate_ai_story, generate_ai_image
            config = ai_config or {}
            ai_data = generate_ai_story(result, config)
            if ai_data:
                result.update(ai_data)
                
            # 9. Optional: Generate AI Avatar Image
            img_key = config.get("image_api_key")
            if img_key and "image_prompt" in result:
                img_url = generate_ai_image(result["image_prompt"], img_key)
                if img_url:
                    result["avatar_url"] = img_url

        if fields:
            return self._filter_by_fields(result, fields)

        return result
