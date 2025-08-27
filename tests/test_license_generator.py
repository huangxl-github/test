import unittest
from datetime import datetime, timedelta
from src.models import LicenseType
from src.license_generator import LicenseGenerator


class TestLicenseGenerator(unittest.TestCase):
    def setUp(self):
        self.secret_key = "test_secret_key"
        self.generator = LicenseGenerator(self.secret_key)
        self.product_id = "TEST-PROD-001"
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=30)

    def test_generate_license_key(self):
        # 测试生成许可证密钥
        license = self.generator.generate_license_key(
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id,
            user_info={"name": "Test User"}
        )
        
        # 验证许可证对象的属性
        self.assertIsNotNone(license.license_key)
        self.assertEqual(license.license_type, LicenseType.PROFESSIONAL)
        self.assertEqual(license.product_id, self.product_id)
        self.assertEqual(license.user_info, {"name": "Test User"})
        
        # 验证许可证密钥的格式
        self.assertTrue(len(license.license_key) > 0)
        self.assertTrue("-" in license.license_key)
        
    def test_generate_trial_license(self):
        # 测试生成试用版许可证
        license = self.generator.generate_trial_license(
            product_id=self.product_id,
            days=15,
            user_info={"name": "Trial User"}
        )
        
        # 验证许可证类型为试用版
        self.assertEqual(license.license_type, LicenseType.TRIAL)
        
        # 验证有效期为15天
        expected_end_date = self.start_date + timedelta(days=15)
        self.assertTrue(abs((license.end_date - expected_end_date).days) <= 1)

    def test_generate_standard_license(self):
        # 测试生成正式版许可证
        license = self.generator.generate_standard_license(
            product_id=self.product_id,
            valid_years=2,
            user_info={"name": "Standard User"}
        )
        
        # 验证许可证类型为正式版
        self.assertEqual(license.license_type, LicenseType.STANDARD)
        
        # 验证有效期为2年
        expected_end_date = datetime(self.start_date.year + 2, self.start_date.month, self.start_date.day)
        self.assertEqual(license.end_date.year, expected_end_date.year)

    def test_generate_professional_license(self):
        # 测试生成专业版许可证
        license = self.generator.generate_professional_license(
            product_id=self.product_id,
            valid_years=1,
            user_info={"name": "Professional User"}
        )
        
        # 验证许可证类型为专业版
        self.assertEqual(license.license_type, LicenseType.PROFESSIONAL)
        
        # 验证有效期为1年
        expected_end_date = datetime(self.start_date.year + 1, self.start_date.month, self.start_date.day)
        self.assertEqual(license.end_date.year, expected_end_date.year)

    def test_batch_generate_licenses(self):
        # 测试批量生成许可证
        count = 5
        licenses = self.generator.batch_generate_licenses(
            count=count,
            license_type=LicenseType.ENTERPRISE,
            valid_years=3,
            product_id=self.product_id,
            user_info_template={"company": "Test Company"}
        )
        
        # 验证生成的许可证数量
        self.assertEqual(len(licenses), count)
        
        # 验证每个许可证的类型和属性
        for i, license in enumerate(licenses):
            self.assertEqual(license.license_type, LicenseType.ENTERPRISE)
            self.assertEqual(license.product_id, self.product_id)
            self.assertEqual(license.user_info["company"], "Test Company")
            self.assertEqual(license.user_info["batch_id"], i + 1)
            
            # 验证每个许可证的密钥都是唯一的
            other_keys = [l.license_key for j, l in enumerate(licenses) if j != i]
            self.assertNotIn(license.license_key, other_keys)


if __name__ == "__main__":
    unittest.main()