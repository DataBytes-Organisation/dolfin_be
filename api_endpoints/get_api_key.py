import json
import os
from Shared.errors import handle_error_response
from Shared.api import API
from Shared.auth import Authorizer


def main(event):
    payload = API.parse_payload(event)
    q_params = payload["query_parameters"]
    if ('key_id' in q_params.keys()):
        result = Authorizer.get_key_by_id(id=q_params['key_id'])
    elif ('key_value' in q_params.keys()):
        result = Authorizer.get_key_by_value(value=q_params['key_value'])
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