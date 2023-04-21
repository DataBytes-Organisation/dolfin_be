from datetime import datetime
from uuid import uuid4

class Account:
    def __init__(self, 
                record_type: str = "type#account", 
                account_id: str = f"ts#{datetime.now()}-id#{uuid4()}",
                payment_due: datetime = None,
            ) -> None:
        self.record_type = record_type
        self.record_ts_id = account_id
        self.payment_due = payment_due

class Role:
    def __init__(self, role: int) -> None:
        self.allowed_roles = {
            0: "admin",
            1: "read-write",
            2: "read"
        }
        self.role = self.set_role(role)
    
    def set_role(self, role: int) -> str:
        try:
            return self.allowed_roles[role]
        except Exception as e:
            raise Exception(f"Error: There are only {len(self.allowed_roles)} roles, pass a valid role id")

class User:
    def __init__(self, 
                account: Account, 
                role: Role,
                first: str,
                last: str,
                nickname: str, 
                email: str,
                password: str,
                record_type: str = "type#user",
            ) -> None:
        self.record_type = record_type
        self.record_ts_id = f"{account.record_ts_id}-{email}"
        self.role = role.role
        self.first = first
        self.last = last
        self.fullname = first+last
        self.nickname = nickname 
        self.email = email
        self.password = password


        