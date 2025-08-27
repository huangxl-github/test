from datetime import datetime
from enum import Enum


class LicenseType(Enum):
    TRIAL = "试用版"
    STANDARD = "正式版"
    PROFESSIONAL = "专业版"
    ENTERPRISE = "企业版"


class LicenseStatus(Enum):
    ACTIVE = "激活"
    EXPIRED = "过期"
    REVOKED = "已吊销"
    PENDING = "待激活"


class License:
    def __init__(self, license_key: str, license_type: LicenseType, start_date: datetime, end_date: datetime, 
                 product_id: str, user_info: dict = None, status: LicenseStatus = LicenseStatus.PENDING):
        self.license_key = license_key
        self.license_type = license_type
        self.start_date = start_date
        self.end_date = end_date
        self.product_id = product_id
        self.user_info = user_info or {}
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.activation_count = 0
        self.last_used = None

    def to_dict(self) -> dict:
        return {
            'license_key': self.license_key,
            'license_type': self.license_type.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'product_id': self.product_id,
            'user_info': self.user_info,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'activation_count': self.activation_count,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'License':
        license = cls(
            license_key=data['license_key'],
            license_type=LicenseType(data['license_type']),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            product_id=data['product_id'],
            user_info=data.get('user_info', {})
        )
        license.status = LicenseStatus(data.get('status', LicenseStatus.PENDING.value))
        license.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        license.updated_at = datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        license.activation_count = data.get('activation_count', 0)
        license.last_used = datetime.fromisoformat(data['last_used']) if data.get('last_used') else None
        return license


class AuditLog:
    def __init__(self, action: str, license_key: str, user_id: str, details: dict = None):
        self.action = action
        self.license_key = license_key
        self.user_id = user_id
        self.details = details or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        return {
            'action': self.action,
            'license_key': self.license_key,
            'user_id': self.user_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AuditLog':
        log = cls(
            action=data['action'],
            license_key=data['license_key'],
            user_id=data['user_id'],
            details=data.get('details', {})
        )
        log.timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        return log