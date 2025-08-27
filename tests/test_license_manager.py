import unittest
import os
import sqlite3
from datetime import datetime, timedelta
from src.models import LicenseType, LicenseStatus
from src.license_manager import LicenseManager


class TestLicenseManager(unittest.TestCase):
    def setUp(self):
        # 使用临时数据库文件进行测试
        self.test_db_path = "test_licenses.db"
        self.secret_key = "test_secret_key"
        self.manager = LicenseManager(db_path=self.test_db_path, secret_key=self.secret_key)
        self.product_id = "TEST-PROD-001"
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=30)

    def tearDown(self):
        # 测试完成后删除临时数据库文件
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_create_license(self):
        # 测试创建许可证
        user_info = {"name": "Test User", "email": "test@example.com"}
        license = self.manager.create_license(
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id,
            user_info=user_info
        )
        
        # 验证许可证是否成功创建
        self.assertIsNotNone(license)
        self.assertEqual(license.license_type, LicenseType.PROFESSIONAL)
        self.assertEqual(license.product_id, self.product_id)
        self.assertEqual(license.user_info, user_info)
        
        # 验证许可证是否保存在数据库中
        retrieved_license = self.manager.get_license_by_key(license.license_key)
        self.assertIsNotNone(retrieved_license)
        self.assertEqual(retrieved_license.license_key, license.license_key)

    def test_update_license(self):
        # 测试更新许可证
        # 首先创建一个许可证
        license = self.manager.create_license(
            license_type=LicenseType.STANDARD,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id
        )
        
        # 修改许可证的属性
        new_end_date = self.end_date + timedelta(days=30)
        new_user_info = {"name": "Updated User"}
        license.end_date = new_end_date
        license.user_info = new_user_info
        license.status = LicenseStatus.ACTIVE
        
        # 保存更新
        result = self.manager.update_license(license)
        
        # 验证更新是否成功
        self.assertTrue(result)
        
        # 从数据库中检索并验证更新后的许可证
        updated_license = self.manager.get_license_by_key(license.license_key)
        self.assertEqual(updated_license.end_date, new_end_date)
        self.assertEqual(updated_license.user_info, new_user_info)
        self.assertEqual(updated_license.status, LicenseStatus.ACTIVE)

    def test_revoke_license(self):
        # 测试吊销许可证
        # 首先创建一个许可证
        license = self.manager.create_license(
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id
        )
        
        # 激活许可证
        license.status = LicenseStatus.ACTIVE
        self.manager.update_license(license)
        
        # 吊销许可证
        result = self.manager.revoke_license(license.license_key)
        
        # 验证吊销是否成功
        self.assertTrue(result)
        
        # 从数据库中检索并验证已吊销的许可证
        revoked_license = self.manager.get_license_by_key(license.license_key)
        self.assertEqual(revoked_license.status, LicenseStatus.REVOKED)

    def test_get_all_licenses(self):
        # 测试获取所有许可证
        # 创建几个不同的许可证
        license1 = self.manager.create_license(
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id
        )
        
        license2 = self.manager.create_license(
            license_type=LicenseType.STANDARD,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id="TEST-PROD-002"
        )
        
        # 激活其中一个许可证
        license2.status = LicenseStatus.ACTIVE
        self.manager.update_license(license2)
        
        # 获取所有许可证
        all_licenses = self.manager.get_all_licenses()
        self.assertEqual(len(all_licenses), 2)
        
        # 按产品ID过滤
        prod1_licenses = self.manager.get_all_licenses(product_id=self.product_id)
        self.assertEqual(len(prod1_licenses), 1)
        self.assertEqual(prod1_licenses[0].product_id, self.product_id)
        
        # 按状态过滤
        active_licenses = self.manager.get_all_licenses(status=LicenseStatus.ACTIVE)
        self.assertEqual(len(active_licenses), 1)
        self.assertEqual(active_licenses[0].status, LicenseStatus.ACTIVE)

    def test_batch_create_licenses(self):
        # 测试批量创建许可证
        count = 5
        user_info_template = {"company": "Test Company"}
        licenses = self.manager.batch_create_licenses(
            count=count,
            license_type=LicenseType.ENTERPRISE,
            valid_years=1,
            product_id=self.product_id,
            user_info_template=user_info_template
        )
        
        # 验证创建的许可证数量
        self.assertEqual(len(licenses), count)
        
        # 验证所有许可证是否都保存在数据库中
        all_licenses = self.manager.get_all_licenses(product_id=self.product_id)
        self.assertEqual(len(all_licenses), count)
        
        # 验证每个许可证的属性
        for i, license in enumerate(all_licenses):
            self.assertEqual(license.license_type, LicenseType.ENTERPRISE)
            self.assertEqual(license.product_id, self.product_id)
            self.assertEqual(license.user_info["company"], "Test Company")
            self.assertEqual(license.user_info["batch_id"], i + 1)

    def test_get_license_usage_history(self):
        # 测试获取许可证使用历史
        # 首先创建一个许可证
        license = self.manager.create_license(
            license_type=LicenseType.PROFESSIONAL,
            start_date=self.start_date,
            end_date=self.end_date,
            product_id=self.product_id
        )
        
        # 添加一些审计日志
        self.manager.add_audit_log(
            action="首次验证",
            license_key=license.license_key,
            user_id="user1",
            details={"machine_id": "machine1"}
        )
        
        self.manager.add_audit_log(
            action="再次验证",
            license_key=license.license_key,
            user_id="user1",
            details={"machine_id": "machine1"}
        )
        
        # 获取使用历史
        history = self.manager.get_license_usage_history(license.license_key)
        
        # 验证历史记录数量（包括创建许可证的日志）
        self.assertTrue(len(history) >= 3)
        
        # 验证日志内容
        actions = [log.action for log in history]
        self.assertIn("创建许可证", actions)
        self.assertIn("首次验证", actions)
        self.assertIn("再次验证", actions)


if __name__ == "__main__":
    unittest.main()