import unittest
import os
from datetime import datetime, timedelta
from src.models import LicenseType, LicenseStatus, License
from src.license_generator import LicenseGenerator
from src.license_validator import LicenseValidator


class MockLicenseRepository:
    """模拟许可证仓库，用于测试在线验证"""
    def __init__(self):
        self.licenses = {}
        self.audit_logs = []

    def get_license_by_key(self, license_key):
        return self.licenses.get(license_key)

    def update_license(self, license):
        self.licenses[license.license_key] = license
        return True

    def add_audit_log(self, action, license_key, user_id, details=None):
        self.audit_logs.append({
            "action": action,
            "license_key": license_key,
            "user_id": user_id,
            "details": details,
            "timestamp": datetime.now()
        })


class TestLicenseValidator(unittest.TestCase):
    def setUp(self):
        self.secret_key = "test_secret_key"
        self.generator = LicenseGenerator(self.secret_key)
        self.validator = LicenseValidator(self.secret_key)
        self.product_id = "TEST-PROD-001"
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=30)
        
        # 创建一个有效的许可证
        self.valid_license = self.generator.generate_license_key(
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id
        )
        
        # 设置模拟仓库用于在线验证
        self.mock_repository = MockLicenseRepository()
        self.mock_repository.licenses[self.valid_license.license_key] = self.valid_license
        self.validator.set_license_repository(self.mock_repository)

    def test_validate_license_offline_valid(self):
        # 测试离线验证有效的许可证
        valid, message = self.validator.validate_license_offline(
            license_key=self.valid_license.license_key,
            product_id=self.product_id
        )
        
        self.assertTrue(valid)
        self.assertEqual(message, "许可证验证成功")

    def test_validate_license_offline_invalid_product_id(self):
        # 测试产品ID不匹配的情况
        valid, message = self.validator.validate_license_offline(
            license_key=self.valid_license.license_key,
            product_id="WRONG-PRODUCT"
        )
        
        self.assertFalse(valid)
        self.assertEqual(message, "许可证与当前产品不匹配")

    def test_validate_license_offline_expired(self):
        # 测试过期的许可证
        past_date = datetime.now() - timedelta(days=1)
        expired_license = self.generator.generate_license_key(
            license_type=LicenseType.PROFESSIONAL,
            start_date=past_date - timedelta(days=30),
            end_date=past_date,
            product_id=self.product_id
        )
        
        valid, message = self.validator.validate_license_offline(
            license_key=expired_license.license_key,
            product_id=self.product_id
        )
        
        self.assertFalse(valid)
        self.assertEqual(message, "许可证已过期")

    def test_validate_license_offline_not_yet_valid(self):
        # 测试尚未生效的许可证
        future_date = datetime.now() + timedelta(days=10)
        future_license = self.generator.generate_license_key(
            license_type=LicenseType.PROFESSIONAL,
            start_date=future_date,
            end_date=future_date + timedelta(days=30),
            product_id=self.product_id
        )
        
        valid, message = self.validator.validate_license_offline(
            license_key=future_license.license_key,
            product_id=self.product_id
        )
        
        self.assertFalse(valid)
        self.assertEqual(message, "许可证尚未生效")

    def test_validate_license_offline_invalid_format(self):
        # 测试无效格式的许可证密钥
        valid, message = self.validator.validate_license_offline(
            license_key="INVALID-LICENSE-KEY",
            product_id=self.product_id
        )
        
        self.assertFalse(valid)
        self.assertTrue("许可证格式错误" in message or "许可证数据验证失败" in message)

    def test_validate_license_online_valid(self):
        # 测试在线验证有效的许可证
        machine_info = {"user_id": "test_user", "machine_id": "test_machine"}
        valid, message = self.validator.validate_license_online(
            license_key=self.valid_license.license_key,
            product_id=self.product_id,
            machine_info=machine_info
        )
        
        self.assertTrue(valid)
        self.assertEqual(message, "许可证验证成功")
        
        # 验证许可证使用次数增加
        updated_license = self.mock_repository.get_license_by_key(self.valid_license.license_key)
        self.assertEqual(updated_license.activation_count, 1)
        self.assertIsNotNone(updated_license.last_used)

    def test_validate_license_online_revoked(self):
        # 测试在线验证已吊销的许可证
        revoked_license = self.generator.generate_license_key(
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id
        )
        revoked_license.status = LicenseStatus.REVOKED
        self.mock_repository.licenses[revoked_license.license_key] = revoked_license
        
        machine_info = {"user_id": "test_user", "machine_id": "test_machine"}
        valid, message = self.validator.validate_license_online(
            license_key=revoked_license.license_key,
            product_id=self.product_id,
            machine_info=machine_info
        )
        
        self.assertFalse(valid)
        self.assertEqual(message, "许可证已被吊销")

    def test_validate_license_online_nonexistent(self):
        # 测试在线验证不存在的许可证
        machine_info = {"user_id": "test_user", "machine_id": "test_machine"}
        valid, message = self.validator.validate_license_online(
            license_key="NONEXISTENT-LICENSE-KEY",
            product_id=self.product_id,
            machine_info=machine_info
        )
        
        self.assertFalse(valid)
        self.assertEqual(message, "许可证不存在")

    def test_is_license_expired(self):
        # 测试许可证过期检查
        # 有效的许可证不应被标记为过期
        self.assertFalse(self.validator.is_license_expired(self.valid_license))
        
        # 过期的许可证应被标记为过期
        past_date = datetime.now() - timedelta(days=1)
        expired_license = License(
            license_key="expired-key",
            license_type=LicenseType.PROFESSIONAL,
            start_date=past_date - timedelta(days=30),
            end_date=past_date,
            product_id=self.product_id
        )
        self.assertTrue(self.validator.is_license_expired(expired_license))

    def test_is_license_revoked(self):
        # 测试许可证吊销检查
        # 有效的许可证不应被标记为吊销
        self.assertFalse(self.validator.is_license_revoked(self.valid_license))
        
        # 吊销的许可证应被标记为吊销
        revoked_license = License(
            license_key="revoked-key",
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id,
            status=LicenseStatus.REVOKED
        )
        self.assertTrue(self.validator.is_license_revoked(revoked_license))


if __name__ == "__main__":
    unittest.main()