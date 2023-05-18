import json
import os
from Shared.errors import handle_error_response, UnAuthorisedError
from Shared.api import API
from Shared.cognito import Cognito


def main(event):
    """This endpoint is the sign ui end point
    you must use the sign up end point before this will work
    """
    payload = API.parse_payload(event)
    user_pool = Cognito(pool_id=os.environ['userpool_id'], client_id = os.environ['client_id'])

    refresh_token = payload["queryStringParameters"]['refresh_token']

    new_tokens = user_pool.refresh_token(refresh_token) # working 

    result = dict(
        auth = new_tokens.get('AuthenticationResult'),
    )

    return result
        

@handle_error_response
def handler(event, context):
    return main(event)

if __name__ == "__main__":
    os.environ['userpool_id'] = "ap-southeast-2_abacxPAir"
    os.environ['client_id'] = "1b3lr4kahlvadej6mvcmadqpdt"
    os.environ['user_table'] = 'dolfinStack-DolfinUserTable9DD22DDB-4TY81U3ZTMUZ'

    event = {
        'httpMethod': 'POST',
        'resource': '/auth/account',
        'queryStringParameters': {
            "refresh_token": ""
        },
        'pathParameters': {},
    }

    resp = handler(event, context=None)
    print(resp)