import pytest

from faker import Faker
from faker.providers.persona.zh_CN import Provider as PersonaProvider


@pytest.fixture(scope="module")
def faker_zh_CN():
    fake = Faker('zh_CN')
    fake.add_provider(PersonaProvider)
    return fake


class TestZhCNPersona:
    def test_random_persona(self, faker_zh_CN):
        p = faker_zh_CN.persona()
        assert "name" in p
        assert "gender" in p
        assert p["gender"] in ["男", "女"]
        assert "age" in p
        assert "ssn" in p
        assert len(p["ssn"]) == 18
        
        # Check SSN length and basic rules
        ssn = p["ssn"]
        assert ssn.isdigit() or (ssn[:17].isdigit() and ssn[17] in '0123456789X')
        
    def test_gender_constraint(self, faker_zh_CN):
        p_male = faker_zh_CN.persona(gender="M")
        assert p_male["gender"] == "男"
        # 17th digit of SSN must be odd for male
        assert int(p_male["ssn"][16]) % 2 != 0
        
        p_female = faker_zh_CN.persona(gender="女")
        assert p_female["gender"] == "女"
        assert int(p_female["ssn"][16]) % 2 == 0

    def test_age_constraint(self, faker_zh_CN):
        p = faker_zh_CN.persona(age_range=(20, 25))
        assert 20 <= p["age"] <= 25

    def test_geographic_constraint(self, faker_zh_CN):
        p = faker_zh_CN.persona(
            hometown_province="广东", 
            hometown_city="广州",
            has_second_phone=True,
            work_province="北京"
        )
        assert "广东" in p["hometown"]["province"]
        assert "广州" in p["hometown"]["city"]
        
        # Phone numbers
        assert "广东" in p["primary_phone"]["location"]
        assert "北京" in p["secondary_phone"]["location"]

    def test_ssn_checksum(self, faker_zh_CN):
        p = faker_zh_CN.persona()
        ssn = p["ssn"]
        
        # Calculate checksum
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = "10X98765432"
        total = sum(int(ssn[i]) * factors[i] for i in range(17))
        expected_checksum = check_codes[total % 11]
        
        assert ssn[17] == expected_checksum
        
    def test_ai_story_empty_without_key(self, faker_zh_CN):
        p = faker_zh_CN.persona(use_ai=True, ai_config={})
        assert "life_story" not in p

    def test_detailed_fields(self, faker_zh_CN):
        p = faker_zh_CN.persona()
        # Physical
        assert "physical" in p
        assert "height" in p["physical"]
        assert "weight" in p["physical"]
        assert "blood_type" in p["physical"]
        
        # Social
        assert "social" in p
        assert p["social"]["education"] in ["高中", "大专", "本科", "硕士", "博士", "MBA", "职业技能培训"]
        assert "salary" in p["social"]
        assert "security_question" in p["social"]
        
        # Internet
        assert "internet" in p
        assert "guid" in p["internet"]
        assert "user_agent" in p["internet"]
        assert "os" in p["internet"]
        
        # Misc
        assert "temp_email" in p
        assert "temp_email_url" in p
        assert "mbti" in p
        assert "bank_card" in p
        assert "bank_name" in p
        assert "@" in p["temp_email"]
        assert p["temp_email_url"].startswith("http")
        assert len(p["mbti"]) == 4
        assert len(p["bank_card"]) >= 16

    def test_custom_kwargs(self, faker_zh_CN):
        custom_height = "200cm"
        custom_job = "宇宙飞行员"
        p = faker_zh_CN.persona(height=custom_height, job=custom_job)
        
        assert p["physical"]["height"] == custom_height
        assert p["social"]["job"] == custom_job
