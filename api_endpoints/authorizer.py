import os
from Shared.errors import handle_error_response
from Shared.auth import Authorizer
import json 


def main(event):
    try:
        arn = event['methodArn']
        method_arn = "{}".format(str(arn).split('/')[0])
        Auth = Authorizer(access_table=os.environ['ACCESS_TABLE'], endpoint_arn=method_arn)
        auth = Auth._check_token(token=event['authorizationToken'])
    except Exception as e:
        auth = "Deny"
    auth_response = Auth.build_response(auth = auth)
    return auth_response

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