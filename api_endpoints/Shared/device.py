from Shared.account import Account
from uuid import uuid4

class Device:
    def __init__(self, 
                account: Account, 
                record_type: str = "type#device", 
                device_id: str = f"id#{uuid4()}",
                name: str = None,
            ) -> None:
        self.record_type = record_type
        self.record_ts_id = f"{account.record_ts_id}-{device_id}"
        self.name = name

class RecordType:
    def __init__(self,
                account: Account, 
                type_name: str,
                record_type: str = "type#recordtype", 
                record_type_id: str = f"id#{uuid4()}",
                template_location: str = None #this is an s3 location that holds a blank calibration sheet
            ) -> None:
        self.record_type = record_type
        self.record_ts_id = f"{account.record_ts_id}-{record_type_id}"
        self.type_name = type_name #calibration sheet, test sheet, whatever
        self.template_location = template_location

class Record:
    def __init__(self, 
                device: Device,
                type_name: str,
                template_location: str, #this is an s3 location that holds a complete calibration sheet
                record_type: str = "type#record", 
                record_id: str = f"id#{uuid4()}",
            ) -> None:
        self.record_type = record_type
        self.record_ts_id = f"{device.record_ts_id}-{record_id}"
        self.type_name = type_name #calibration sheet, test sheet, whatever
        self.template_location = template_location


        
        