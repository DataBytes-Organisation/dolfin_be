import json
import os
from Shared.errors import handle_error_response
from Shared.api import API
from Shared.basiq import Basiq



def main(event):
    print('request: {}'.format(json.dumps(event)))
    payload = API.parse_payload(event)
    # get the user details from the user table, 
    
    # get the basiq id
    basiq = Basiq(basiq_id="11103cba-4a08-4397-84a5-22ac125ed2f6")

    access_token = basiq.get_auth_token()

    response = basiq.get_accounts(access_token)

    return response


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

    resp = handler(event, context=None)
    print(resp)