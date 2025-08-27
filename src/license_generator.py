import uuid
import hashlib
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from .models import License, LicenseType, LicenseStatus


class LicenseGenerator:
    def __init__(self, secret_key: str):
        # 确保密钥长度为32字节（AES-256需要）
        self.secret_key = hashlib.sha256(secret_key.encode()).digest()
        self.iv = bytes.fromhex('0123456789abcdef0123456789abcdef')  # 初始化向量（实际应用中应使用随机IV）

    def generate_license_key(self, license_type: LicenseType, start_date: datetime, end_date: datetime, 
                           product_id: str, user_info: dict = None) -> License:
        # 生成唯一标识
        unique_id = str(uuid.uuid4())
        
        # 创建许可证数据字符串
        license_data = f"{product_id}|{license_type.value}|{start_date.isoformat()}|{end_date.isoformat()}|{unique_id}"
        
        # 加密许可证数据
        encrypted_data = self._encrypt_data(license_data)
        
        # 生成许可证密钥
        license_key = self._format_license_key(encrypted_data)
        
        # 创建许可证对象
        license = License(
            license_key=license_key,
            license_type=license_type,
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            user_info=user_info
        )
        
        return license

    def generate_trial_license(self, product_id: str, days: int = 30, user_info: dict = None) -> License:
        """生成试用版许可证"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        return self.generate_license_key(
            license_type=LicenseType.TRIAL,
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            user_info=user_info
        )

    def generate_standard_license(self, product_id: str, valid_years: int = 1, user_info: dict = None) -> License:
        """生成正式版许可证"""
        start_date = datetime.now()
        end_date = datetime(start_date.year + valid_years, start_date.month, start_date.day)
        return self.generate_license_key(
            license_type=LicenseType.STANDARD,
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            user_info=user_info
        )

    def generate_professional_license(self, product_id: str, valid_years: int = 1, user_info: dict = None) -> License:
        """生成专业版许可证"""
        start_date = datetime.now()
        end_date = datetime(start_date.year + valid_years, start_date.month, start_date.day)
        return self.generate_license_key(
            license_type=LicenseType.PROFESSIONAL,
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            user_info=user_info
        )

    def batch_generate_licenses(self, count: int, license_type: LicenseType, valid_years: int, 
                               product_id: str, user_info_template: dict = None) -> list[License]:
        """批量生成许可证"""
        licenses = []
        user_info_template = user_info_template or {}
        
        for i in range(count):
            user_info = user_info_template.copy()
            user_info['batch_id'] = i + 1
            
            start_date = datetime.now()
            end_date = datetime(start_date.year + valid_years, start_date.month, start_date.day)
            
            license = self.generate_license_key(
                license_type=license_type,
                start_date=start_date,
                end_date=end_date,
                product_id=product_id,
                user_info=user_info
            )
            licenses.append(license)
        
        return licenses

    def _encrypt_data(self, data: str) -> bytes:
        # 填充数据
        padder = padding.PKCS7(128).padder()
        data_bytes = data.encode()
        padded_data = padder.update(data_bytes) + padder.finalize()
        
        # 创建密码器并加密
        cipher = Cipher(algorithms.AES(self.secret_key), modes.CBC(self.iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data

    def _format_license_key(self, encrypted_data: bytes) -> str:
        # 将加密数据转换为base64编码
        base64_data = base64.b64encode(encrypted_data).decode('utf-8')
        
        # 移除base64中的特殊字符
        formatted = base64_data.replace('+', '').replace('/', '').replace('=', '')
        
        # 按照8个字符一组进行分组，并添加连字符
        chunks = [formatted[i:i+8] for i in range(0, len(formatted), 8)]
        
        # 确保许可证密钥长度适中
        if len(chunks) > 5:
            chunks = chunks[:5]
        
        return '-'.join(chunks)