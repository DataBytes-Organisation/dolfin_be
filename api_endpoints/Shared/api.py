from typing import Optional

class API:
    def response(code: int, body: Optional[str] = None):
        return {
            "statusCode": code, 
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": body,
        }
