from datetime import datetime, timedelta
from .models import LicenseType, LicenseStatus
from .license_manager import LicenseManager


def main():
    # 初始化许可证管理器
    print("初始化许可证系统...")
    license_manager = LicenseManager(db_path='licenses.db', secret_key='my_secure_secret_key_123')
    print("许可证系统初始化完成。")

    # 示例1：创建单个许可证
    print("\n示例1：创建单个许可证")
    product_id = "PROD-001"
    start_date = datetime.now()
    end_date = start_date + timedelta(days=365)  # 有效期1年
    user_info = {"company": "示例公司", "contact": "张三", "email": "zhangsan@example.com"}
    
    # 创建专业版许可证
    license = license_manager.create_license(
        license_type=LicenseType.PROFESSIONAL,
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        user_info=user_info
    )
    
    print(f"创建的许可证信息：")
    print(f"- 许可证密钥: {license.license_key}")
    print(f"- 许可证类型: {license.license_type.value}")
    print(f"- 有效期: {license.start_date.strftime('%Y-%m-%d')} 至 {license.end_date.strftime('%Y-%m-%d')}")
    print(f"- 产品ID: {license.product_id}")
    print(f"- 状态: {license.status.value}")

    # 示例2：验证许可证
    print("\n示例2：验证许可证")
    machine_info = {"user_id": "user123", "machine_id": "machine456"}
    
    # 在线验证
    valid, message = license_manager.validator.validate_license_online(
        license_key=license.license_key,
        product_id=product_id,
        machine_info=machine_info
    )
    print(f"在线验证结果: {'成功' if valid else '失败'}")
    print(f"验证消息: {message}")
    
    # 离线验证
    valid, message = license_manager.validator.validate_license_offline(
        license_key=license.license_key,
        product_id=product_id
    )
    print(f"离线验证结果: {'成功' if valid else '失败'}")
    print(f"验证消息: {message}")

    # 示例3：批量创建许可证
    print("\n示例3：批量创建许可证")
    count = 5
    batch_licenses = license_manager.batch_create_licenses(
        count=count,
        license_type=LicenseType.STANDARD,
        valid_years=1,
        product_id="PROD-002",
        user_info_template={"department": "测试部门"}
    )
    print(f"成功创建 {len(batch_licenses)} 个许可证")
    print("前3个许可证密钥:")
    for i, lic in enumerate(batch_licenses[:3]):
        print(f"- {i+1}: {lic.license_key}")

    # 示例4：查询和管理许可证
    print("\n示例4：查询和管理许可证")
    
    # 获取所有许可证
    all_licenses = license_manager.get_all_licenses()
    print(f"系统中共有 {len(all_licenses)} 个许可证")
    
    # 按产品ID查询
    prod_licenses = license_manager.get_all_licenses(product_id=product_id)
    print(f"产品 {product_id} 的许可证数量: {len(prod_licenses)}")
    
    # 按状态查询
    active_licenses = license_manager.get_all_licenses(status=LicenseStatus.ACTIVE)
    print(f"激活状态的许可证数量: {len(active_licenses)}")

    # 示例5：吊销许可证
    print("\n示例5：吊销许可证")
    # 先激活一个许可证以便后续吊销
    if license.status == LicenseStatus.PENDING:
        license.status = LicenseStatus.ACTIVE
        license_manager.update_license(license)
        print(f"许可证 {license.license_key} 已激活")
    
    # 吊销许可证
    revoked = license_manager.revoke_license(license.license_key)
    print(f"许可证吊销{'成功' if revoked else '失败'}")
    
    # 验证被吊销的许可证
    valid, message = license_manager.validator.validate_license_online(
        license_key=license.license_key,
        product_id=product_id,
        machine_info=machine_info
    )
    print(f"验证被吊销的许可证: {'成功' if valid else '失败'}")
    print(f"验证消息: {message}")

    # 示例6：查看许可证使用历史
    print("\n示例6：查看许可证使用历史")
    usage_history = license_manager.get_license_usage_history(license.license_key)
    print(f"许可证 {license.license_key} 的使用历史记录数量: {len(usage_history)}")
    print("最近3条记录:")
    for i, log in enumerate(usage_history[:3]):
        print(f"- {i+1}: {log.action} (时间: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")


if __name__ == "__main__":
    main()