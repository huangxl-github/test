import sqlite3
import json
from datetime import datetime
from .models import License, LicenseType, LicenseStatus, AuditLog
from .license_generator import LicenseGenerator
from .license_validator import LicenseValidator


class LicenseManager:
    def __init__(self, db_path: str = 'licenses.db', secret_key: str = 'default_secret_key'):
        self.db_path = db_path
        self.secret_key = secret_key
        self.generator = LicenseGenerator(secret_key)
        self.validator = LicenseValidator(secret_key)
        self.validator.set_license_repository(self)
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建许可证表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT UNIQUE NOT NULL,
                    license_type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    user_info TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    activation_count INTEGER DEFAULT 0,
                    last_used TEXT
                )
            ''')
            
            # 创建审计日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    license_key TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            conn.commit()

    def create_license(self, license_type: LicenseType, start_date: datetime, end_date: datetime, 
                      product_id: str, user_info: dict = None) -> License:
        """创建许可证"""
        license = self.generator.generate_license_key(
            license_type=license_type,
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            user_info=user_info
        )
        
        self._save_license(license)
        
        # 记录审计日志
        self.add_audit_log(
            action="创建许可证",
            license_key=license.license_key,
            user_id="system",
            details={"license_type": license_type.value, "product_id": product_id}
        )
        
        return license

    def batch_create_licenses(self, count: int, license_type: LicenseType, valid_years: int, 
                             product_id: str, user_info_template: dict = None) -> list[License]:
        """批量创建许可证"""
        licenses = self.generator.batch_generate_licenses(
            count=count,
            license_type=license_type,
            valid_years=valid_years,
            product_id=product_id,
            user_info_template=user_info_template
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for license in licenses:
                self._save_license(license, conn, cursor)
            conn.commit()
        
        # 记录审计日志
        self.add_audit_log(
            action="批量创建许可证",
            license_key="batch",
            user_id="system",
            details={"count": count, "license_type": license_type.value, "product_id": product_id}
        )
        
        return licenses

    def get_license_by_key(self, license_key: str) -> License:
        """根据许可证密钥获取许可证"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_license(row)
            return None

    def update_license(self, license: License) -> bool:
        """更新许可证信息"""
        license.updated_at = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    '''
                    UPDATE licenses 
                    SET license_type = ?, start_date = ?, end_date = ?, product_id = ?, user_info = ?, 
                        status = ?, updated_at = ?, activation_count = ?, last_used = ?
                    WHERE license_key = ?
                    ''',
                    (
                        license.license_type.value,
                        license.start_date.isoformat(),
                        license.end_date.isoformat(),
                        license.product_id,
                        json.dumps(license.user_info),
                        license.status.value,
                        license.updated_at.isoformat(),
                        license.activation_count,
                        license.last_used.isoformat() if license.last_used else None,
                        license.license_key
                    )
                )
                conn.commit()
                
                # 记录审计日志
                self.add_audit_log(
                    action="更新许可证",
                    license_key=license.license_key,
                    user_id="system",
                    details={"status": license.status.value}
                )
                
                return cursor.rowcount > 0
            except Exception:
                return False

    def revoke_license(self, license_key: str) -> bool:
        """吊销许可证"""
        license = self.get_license_by_key(license_key)
        if license:
            license.status = LicenseStatus.REVOKED
            result = self.update_license(license)
            
            # 记录审计日志
            if result:
                self.add_audit_log(
                    action="吊销许可证",
                    license_key=license_key,
                    user_id="system",
                    details={}
                )
            
            return result
        return False

    def get_all_licenses(self, product_id: str = None, status: LicenseStatus = None) -> list[License]:
        """获取所有许可证，可以按产品ID和状态过滤"""
        query = "SELECT * FROM licenses"
        params = []
        
        if product_id or status:
            query += " WHERE"
            conditions = []
            
            if product_id:
                conditions.append(" product_id = ?")
                params.append(product_id)
            
            if status:
                if conditions:
                    conditions.append(" AND")
                conditions.append(" status = ?")
                params.append(status.value)
            
            query += ''.join(conditions)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_license(row) for row in rows]

    def get_license_usage_history(self, license_key: str) -> list[AuditLog]:
        """获取许可证的使用历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM audit_logs WHERE license_key = ? ORDER BY timestamp DESC",
                (license_key,)
            )
            rows = cursor.fetchall()
            
            return [self._row_to_audit_log(row) for row in rows]

    def add_audit_log(self, action: str, license_key: str, user_id: str, details: dict = None):
        """添加审计日志"""
        log = AuditLog(action=action, license_key=license_key, user_id=user_id, details=details)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_logs (action, license_key, user_id, details, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    log.action,
                    log.license_key,
                    log.user_id,
                    json.dumps(log.details),
                    log.timestamp.isoformat()
                )
            )
            conn.commit()

    def _save_license(self, license: License, conn=None, cursor=None):
        """保存许可证到数据库"""
        is_external_conn = conn is not None
        if not is_external_conn:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO licenses (
                license_key, license_type, start_date, end_date, product_id, user_info, 
                status, created_at, updated_at, activation_count, last_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                license.license_key,
                license.license_type.value,
                license.start_date.isoformat(),
                license.end_date.isoformat(),
                license.product_id,
                json.dumps(license.user_info),
                license.status.value,
                license.created_at.isoformat(),
                license.updated_at.isoformat(),
                license.activation_count,
                license.last_used.isoformat() if license.last_used else None
            )
        )
        
        if not is_external_conn:
            conn.commit()
            conn.close()

    def _row_to_license(self, row: sqlite3.Row) -> License:
        """将数据库行转换为许可证对象"""
        data = dict(row)
        data['user_info'] = json.loads(data['user_info']) if data['user_info'] else {}
        return License.from_dict(data)

    def _row_to_audit_log(self, row: sqlite3.Row) -> AuditLog:
        """将数据库行转换为审计日志对象"""
        data = dict(row)
        data['details'] = json.loads(data['details']) if data['details'] else {}
        return AuditLog.from_dict(data)