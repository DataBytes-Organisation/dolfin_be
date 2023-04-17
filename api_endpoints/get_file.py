import json
import os
from Shared.errors import ClientError, NotFoundError, ServerError
from Shared.api import API
from Shared.s3 import S3

def main(event):
    s3 = S3()
    some_s3_location = event["file_location"]
    result = s3.get_file(some_s3_location)
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
        'queryStringParameters': {
            "file_location": "some_location"
        },
        'pathParameters': {},
        'body' : json.dumps(body)
    }

    handler(event, context=None)