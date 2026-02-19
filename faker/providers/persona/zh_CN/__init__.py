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
    _villages_data = None

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
        ai_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a Chinese virtual persona strictly adhering to geographic, logical and ID verification constraints.
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

        # 4. Generate Primary Phone
        def get_phone_number(p_name: str, c_name: str) -> str:
            # handle cases like "北京" vs "北京市"
            p_key = p_name.replace("市", "").replace("省", "").replace("自治区", "")
            matched_prov = next((k for k in phones.keys() if p_key in k or k in p_key), None)
            if matched_prov:
                city_dict = phones[matched_prov]
                c_key = c_name.replace("市", "").replace("地区", "").replace("盟", "")
                
                # Special handling for direct-administered municipalities
                if p_key in ["北京", "上海", "天津", "重庆"] and c_key in ["辖区", "市辖区", "县"]:
                    c_key = p_key
                    
                matched_city = next((k for k in city_dict.keys() if c_key in k or k in c_key), None)
                if matched_city:
                    prefixes = city_dict[matched_city]
                    if prefixes:
                        prefix = self.random_element(prefixes)
                        suffix = f"{self.random_int(min=0, max=9999):04d}"
                        return f"{prefix}{suffix}"
            try:
                return self.generator.phone_number()
            except AttributeError: # in case we fallback without generic provider
                return f"13{self.random_int(min=0,max=9)}{self.random_int(min=0,max=99999999):08d}"

        primary_phone = get_phone_number(prov_name, city_name)

        # 5. Determine Name
        if is_male:
            try:
                name = getattr(self.generator, "name_male")()
            except AttributeError:
                name = self.generator.name()
        else:
            try:
                name = getattr(self.generator, "name_female")()
            except AttributeError:
                name = self.generator.name()

        # 6. Build base persona
        is_urban = False
        villages = self._load_villages()
        real_villages = villages.get(town_code, []) if town_code else []
        
        if town_name:
            if any(t in town_name for t in ["街道", "地区", "社区"]):
                is_urban = True
            elif any(t in town_name for t in ["乡", "镇", "外围", "林场", "农场"]):
                is_urban = False
            else:
                is_urban = "市" in area_name or "区" in area_name
        else:
            is_urban = "区" in area_name or "街道" in area_name or ("市" in area_name and not area_name.endswith("市"))

        if is_urban:
            base_estate_name = ""
            if real_villages:
                urban_vp = [v for v in real_villages if "社区" in v or "居委会" in v]
                if not urban_vp:
                    urban_vp = real_villages
                base_estate_name = self.random_element(urban_vp)
                for suffix in ["居民委员会", "社区居委会", "居委会", "社区", "村民委员会", "村委会"]:
                    base_estate_name = base_estate_name.replace(suffix, "")
                    
            if not base_estate_name or len(base_estate_name) < 2:
                base_estate_name = self.random_element(["阳光", "时代", "世纪", "国际", "理想", "中心", "滨江", "半岛", "水岸", "绿洲", "星河", "华府", "帝景", "云顶", "紫金", "御景", "东方", "金地", "碧桂园", "万科", "融创"])
            
            estate_suffix = self.random_element(["小区", "花园", "苑", "家园", "新村", "公馆", "府"])
            estate_name = f"{base_estate_name}{estate_suffix}"

            try:
                road_name = getattr(self.generator, "street_name")()
            except AttributeError:
                road_name = self.random_element(["朝阳", "建设", "胜利", "光明", "人民", "中山", "解放", "新华", "和平", "建国", "黄河", "长城"]) + self.random_element(["路", "街"])

            if not road_name.endswith("路") and not road_name.endswith("街") and not road_name.endswith("巷"):
                road_name += self.random_element(["路", "街"])
            
            bldg = self.random_int(min=1, max=50)
            unit = self.random_int(min=1, max=5)
            floor = self.random_int(min=1, max=30)
            room = self.random_int(min=1, max=4)
            street = f"{town_name}{road_name}{estate_name}{bldg}号楼{unit}单元{floor}0{room}室"
        else:
            if real_villages:
                rural_vp = []
                for v in real_villages:
                    for suffix in ["居民委员会", "社区居委会", "居委会", "社区", "村民委员会", "村委会"]:
                        v = v.replace(suffix, "")
                    rural_vp.append(v)
                village_name = self.random_element(rural_vp) if rural_vp else ""
                
                if village_name and not village_name.endswith("村") and not village_name.endswith("庄") and not village_name.endswith("队"):
                    village_name += "村"
            else:
                village_name = ""
                
            if not village_name:
                v_prefix = self.random_element(["张家", "李家", "王家", "赵家", "刘家", "周家", "吴家", "郑家", "上", "下", "前", "后", "东", "西", "南", "北", "大", "小", "新", "老"])
                v_suffix = self.random_element(["村", "庄", "屯", "营", "堡", "沟", "湾", "坪", "桥"])
                village_name = f"{v_prefix}{v_suffix}村" if v_suffix != "村" else f"{v_prefix}{v_suffix}"
            
            num = self.random_int(min=1, max=100)
            street = f"{town_name}{village_name}{num}号"

        addr_prov_key = prov_name.replace("市", "").replace("省", "").replace("自治区", "")
        addr_city = city_name
        if addr_prov_key in ["北京", "上海", "天津", "重庆"] and city_name in ["市辖区", "县"]:
            addr_city = ""
        elif city_name in ["省直辖县级行政区划", "自治区直辖县级行政区划"]:
            addr_city = ""

        result = {
            "name": name,
            "gender": gender_val,
            "age": age,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "ssn": ssn,
            "hometown": {
                "province": prov_name,
                "city": city_name,
                "area": area_name,
                "address": f"{prov_name}{addr_city}{area_name}{street}"
            },
            "primary_phone": {
                "number": primary_phone,
                "location": f"{prov_name}{addr_city}" if addr_city else prov_name
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

        return result
