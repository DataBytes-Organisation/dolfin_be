import json
import os
from Shared.errors import ClientError, NotFoundError, ServerError
from Shared.api import API

def main(event):
    print('request: {}'.format(json.dumps(event)))
    query_params = event.get('queryStringParameters')
    path_params = event.get('pathParameters')
    request_body = {}
    if 'body' in event and event['body'] != None:
        request_body = json.loads(event['body']) # only works for json.dumps(body)

    result = {} #do stuff here to get result
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