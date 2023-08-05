import json
import os
from Shared.errors import handle_error_response
from Shared.api import API
from Shared.auth import Authorizer

def main(event):
    payload = API.parse_payload(event)
    result = Authorizer.create_api_key(key_request=payload["body"])
    return result

@handle_error_response
def handler(event, context):
    return main(event)

        
    
if __name__ == "__main__":
    os.environ["some_env_var"] = "env_var_value"

    body = {
        "attribute1": "value1",
        "attribute2": "value2",
    }

    event = {
        'httpMethod': 'GET',
        'resource': '/example',
        'queryStringParameters': {},
        'pathParameters': {},
        'body' : json.dumps(body)
    }

    handler(event, context=None)