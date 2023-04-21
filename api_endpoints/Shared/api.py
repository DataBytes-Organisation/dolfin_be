from typing import Optional, Dict, Any
import json

class API:
    def response(code: int, body: Optional[str] = None):
        return {
            "statusCode": code, 
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": body,
        }

    def parse_payload(event: Dict[str, Any]):
        payload = {}
        if event.get("queryStringParameters"): payload["queryStringParameters"] = event["queryStringParameters"]
        if event.get("pathParameters"): payload["pathParameters"] = event["pathParameters"]
        if event.get("body"): payload["body"] = json.loads(event["body"])
        return payload
