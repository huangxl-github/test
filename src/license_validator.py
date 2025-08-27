import hashlib
import base64
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from .models import License, LicenseStatus


class LicenseValidator:
    def __init__(self, secret_key: str):
        # 确保密钥长度为32字节（AES-256需要）
        self.secret_key = hashlib.sha256(secret_key.encode()).digest()
        self.iv = bytes.fromhex('0123456789abcdef0123456789abcdef')  # 初始化向量
        self.license_repository = None  # 用于在线验证

    def set_license_repository(self, repository):
        """设置许可证仓库，用于在线验证"""
        self.license_repository = repository

    def validate_license_offline(self, license_key: str, product_id: str) -> tuple[bool, str]:
        """离线验证许可证"""
        try:
            # 解析许可证密钥
            encrypted_data = self._parse_license_key(license_key)
            
            # 解密许可证数据
            decrypted_data = self._decrypt_data(encrypted_data)
            
            # 验证许可证数据
            return self._verify_license_data(decrypted_data, product_id)
        except Exception as e:
            return False, f"许可证格式错误或已被篡改: {str(e)}"

    def validate_license_online(self, license_key: str, product_id: str, machine_info: dict = None) -> tuple[bool, str]:
        """在线验证许可证"""
        if not self.license_repository:
            return False, "许可证仓库未配置，无法进行在线验证"

        try:
            # 检查许可证是否存在于仓库中
            license = self.license_repository.get_license_by_key(license_key)
            if not license:
                return False, "许可证不存在"

            # 检查许可证状态
            if license.status == LicenseStatus.REVOKED:
                return False, "许可证已被吊销"
            if license.status == LicenseStatus.EXPIRED:
                return False, "许可证已过期"

            # 离线验证部分
            valid, message = self.validate_license_offline(license_key, product_id)
            if not valid:
                return False, message

            # 检查产品ID是否匹配
            if license.product_id != product_id:
                return False, "许可证与当前产品不匹配"

            # 更新许可证使用记录
            license.activation_count += 1
            license.last_used = datetime.now()
            self.license_repository.update_license(license)

            # 记录审计日志
            self.license_repository.add_audit_log(
                action="验证许可证",
                license_key=license_key,
                user_id=machine_info.get('user_id', 'unknown'),
                details={"machine_info": machine_info}
            )

            return True, "许可证验证成功"
        except Exception as e:
            return False, f"在线验证失败: {str(e)}"

    def _parse_license_key(self, license_key: str) -> bytes:
        """解析许可证密钥，移除连字符"""
        # 移除连字符
        key_without_hyphens = license_key.replace('-', '')
        
        # 计算需要添加的填充字符数量
        padding_needed = 4 - (len(key_without_hyphens) % 4)
        if padding_needed != 4:
            key_without_hyphens += '=' * padding_needed
        
        # 转换为base64编码的字节数据
        try:
            return base64.b64decode(key_without_hyphens)
        except Exception:
            raise ValueError("许可证密钥格式错误")

    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """解密许可证数据"""
        # 创建密码器并解密
        cipher = Cipher(algorithms.AES(self.secret_key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # 移除填充
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode('utf-8')

    def _verify_license_data(self, license_data: str, product_id: str) -> tuple[bool, str]:
        """验证许可证数据"""
        try:
            # 解析许可证数据
            parts = license_data.split('|')
            if len(parts) != 5:
                return False, "许可证数据格式错误"
            
            stored_product_id, license_type, start_date_str, end_date_str, unique_id = parts
            
            # 验证产品ID
            if stored_product_id != product_id:
                return False, "许可证与当前产品不匹配"
            
            # 验证有效期
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
            current_date = datetime.now()
            
            if current_date < start_date:
                return False, "许可证尚未生效"
            if current_date > end_date:
                return False, "许可证已过期"
            
            return True, "许可证验证成功"
        except Exception as e:
            return False, f"许可证数据验证失败: {str(e)}"

    def is_license_expired(self, license: License) -> bool:
        """检查许可证是否已过期"""
        return datetime.now() > license.end_date

    def is_license_revoked(self, license: License) -> bool:
        """检查许可证是否已被吊销"""
        return license.status == LicenseStatus.REVOKED