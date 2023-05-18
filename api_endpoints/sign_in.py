import json
import os
from Shared.errors import handle_error_response, UnAuthorisedError
from Shared.api import API
from Shared.cognito import Cognito
from Shared.dynamo import Dynamo
from Shared.account import User, Role, Account


def main(event):
    """This endpoint is the sign ui end point
    you must use the sign up end point before this will work
    """
    payload = API.parse_payload(event)
    account = Account()
    user_pool = Cognito(pool_id=os.environ['userpool_id'], client_id = os.environ['client_id'])
    dynamo = Dynamo(table_name=os.environ['user_table'])

    user = dynamo.get_user(email=payload["queryStringParameters"]['email'])
    password_attempt = payload["queryStringParameters"]['password']

    role = Role(role=0) # 0 is admin
    user = User(
        account = account,
        role = role,
        first = user["first"],
        last = user["last"],
        nickname = user["nickname"],
        email = user["email"],
        password = password_attempt,
        )

    # create Admin user in Cognito
    sign_in_result = user_pool.sign_in(user) # working 

    result = dict(
        auth = sign_in_result.get('AuthenticationResult'),
        account_id = account.record_ts_id,
        username = user.nickname,
        first = user.first,
        last = user.last,
        role = user.role
    )

    return result
        

@handle_error_response
def handler(event, context):
    return main(event)

if __name__ == "__main__":
    os.environ['userpool_id'] = "ap-southeast-2_k6FlfaME8"
    os.environ['client_id'] = "1sgt1t8bga7a6ohmd35j77oltj"
    os.environ['user_table'] = 'dolfinStack-DolfinUserTable9DD22DDB-18YAIXIZDEQ14'

    event = {
        'httpMethod': 'POST',
        'resource': '/auth/account',
        'queryStringParameters': {
            "email": "jmdifferent@gmail.com",
            "password": "fakep@ssword123"
        },
        'pathParameters': {},
        #'body' : json.dumps(body)
    }

    resp = handler(event, context=None)
    print(resp)