#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证系统演示脚本
此脚本用于在无法安装依赖的情况下，模拟展示许可证系统的核心功能
"""

import os
import sys
import time
import json
import base64
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("="*50)
print("许可证系统演示程序")
print("(此演示在未安装依赖的环境中运行，使用模拟功能)")
print("="*50)
print()

# 模拟加密模块
class MockCrypto:
    @staticmethod
    def encrypt(data, key):
        # 模拟加密过程
        print("[模拟] 使用AES-256加密数据")
        # 将数据转为JSON字符串
        data_str = json.dumps(data)
        # 简单的Base64编码作为模拟加密
        encrypted_data = base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
        return encrypted_data
    
    @staticmethod
    def decrypt(encrypted_data, key):
        # 模拟解密过程
        print("[模拟] 使用AES-256解密数据")
        # 简单的Base64解码作为模拟解密
        try:
            data_str = base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
            return json.loads(data_str)
        except:
            return None

# 模拟许可证生成器
def generate_license(product_id, license_type="standard", duration_days=30):
    print(f"\n[许可证生成] 为产品ID: {product_id} 生成 {license_type} 类型的许可证，有效期 {duration_days} 天")
    
    # 生成许可证数据
    issue_date = datetime.now()
    expire_date = issue_date + timedelta(days=duration_days)
    
    license_data = {
        "product_id": product_id,
        "license_type": license_type,
        "issue_date": issue_date.isoformat(),
        "expire_date": expire_date.isoformat(),
        "license_key": f"LIC-{product_id}-{license_type.upper()}-{int(time.time())}",
        "status": "active"
    }
    
    # 模拟加密生成许可证密钥
    mock_crypto = MockCrypto()
    encrypted_key = mock_crypto.encrypt(license_data, "mock_encryption_key")
    
    print(f"[许可证生成] 成功生成许可证密钥")
    print(f"[许可证生成] 许可证类型: {license_type}")
    print(f"[许可证生成] 颁发日期: {issue_date.strftime('%Y-%m-%d')}")
    print(f"[许可证生成] 过期日期: {expire_date.strftime('%Y-%m-%d')}")
    
    return license_data, encrypted_key

# 模拟许可证验证器
def validate_license(license_key, product_id=None):
    print(f"\n[许可证验证] 验证许可证密钥")
    
    # 模拟解密许可证数据
    mock_crypto = MockCrypto()
    
    # 模拟成功验证的情况
    if license_key.startswith("LIC-") or license_key:  # 简单的格式检查
        # 模拟许可证数据
        license_data = {
            "product_id": product_id or "PROD-123",
            "license_type": "standard",
            "issue_date": (datetime.now() - timedelta(days=10)).isoformat(),
            "expire_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "license_key": license_key,
            "status": "active"
        }
        
        # 检查产品ID匹配
        if product_id and license_data["product_id"] != product_id:
            print(f"[许可证验证] 失败: 产品ID不匹配")
            return False, "产品ID不匹配"
        
        # 检查是否在有效期内
        expire_date = datetime.fromisoformat(license_data["expire_date"])
        if expire_date < datetime.now():
            print(f"[许可证验证] 失败: 许可证已过期")
            return False, "许可证已过期"
        
        print(f"[许可证验证] 成功: 许可证有效")
        print(f"[许可证验证] 许可证类型: {license_data['license_type']}")
        print(f"[许可证验证] 过期日期: {expire_date.strftime('%Y-%m-%d')}")
        
        return True, "许可证验证成功"
    else:
        print(f"[许可证验证] 失败: 无效的许可证格式")
        return False, "无效的许可证格式"

# 模拟许可证管理
def manage_license(license_data, action="update"):
    print(f"\n[许可证管理] 执行 {action} 操作")
    
    if action == "update":
        print(f"[许可证管理] 更新许可证信息")
        print(f"[许可证管理] 产品ID: {license_data['product_id']}")
        print(f"[许可证管理] 许可证类型: {license_data['license_type']}")
        print(f"[许可证管理] 更新成功")
        return True
    elif action == "revoke":
        print(f"[许可证管理] 吊销许可证")
        print(f"[许可证管理] 产品ID: {license_data['product_id']}")
        print(f"[许可证管理] 许可证密钥: {license_data['license_key']}")
        print(f"[许可证管理] 吊销成功")
        return True
    else:
        print(f"[许可证管理] 未知操作: {action}")
        return False

# 主演示函数
def main():
    print("1. 演示许可证生成功能")
    license_data, encrypted_key = generate_license("PROD-2024", "professional", 90)
    print(f"许可证密钥(加密后): {encrypted_key[:30]}...")
    
    print("\n2. 演示许可证验证功能")
    success, message = validate_license(license_data["license_key"], "PROD-2024")
    print(f"验证结果: {message}")
    
    print("\n3. 演示许可证管理功能")
    manage_license(license_data, "update")
    manage_license(license_data, "revoke")
    
    print("\n4. 演示批量生成许可证")
    products = ["PROD-001", "PROD-002", "PROD-003"]
    batch_licenses = []
    
    for product in products:
        lic_data, enc_key = generate_license(product, "standard", 30)
        batch_licenses.append({
            "product_id": product,
            "license_key": lic_data["license_key"]
        })
    
    print(f"\n批量生成结果: 共生成 {len(batch_licenses)} 个许可证")
    for lic in batch_licenses:
        print(f"- 产品ID: {lic['product_id']}, 许可证密钥: {lic['license_key']}")
    
    print("\n" + "="*50)
    print("许可证系统演示完成")
    print("注意: 完整系统需要安装以下依赖包:")
    print("- cryptography: 用于加密和解密许可证数据")
    print("- pycryptodome: 提供额外的加密算法支持")
    print("- python-dateutil: 处理日期和时间")
    print("- pysqlite3: 数据库支持")
    print("="*50)

if __name__ == "__main__":
    main()