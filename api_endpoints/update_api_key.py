import json
import os
from Shared.errors import ClientError, NotFoundError, ServerError
from Shared.api import API
from Shared.auth import Authorizer

def main(event):
    payload = API.parse_payload(event)
    q_params = payload["query_parameters"]
    body = payload["body"]
    if ('key_id' in q_params.keys()):
        result = Authorizer.update_key(key_id=q_params['key_id'], attributes=body)
    return result


def handler(event, context):
    try:
        response = main(event)        
        return API.response(
            code = 200, 
            body = json.dumps(response) 
        )
    except ClientError as e:
        return API.response(
            code = 400, 
            body = json.dumps({"Error": f"{e}"}) 
        )
    except NotFoundError as e:
        return API.response(
            code = 404, 
            body = json.dumps({"Error": f"{e}"}) 
        )
    except ServerError as e:
        return API.response(
            code = 500, 
            body = json.dumps({"Error": f"{e}"}) 
        )
    except Exception as e:
        return API.response(
            code = 500, 
            body = json.dumps({"Error": f"{e}"}) 
        )
        
    
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