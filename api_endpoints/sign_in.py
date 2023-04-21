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
    Please ignore how trash this is, it will be fixed 😂
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
        password = user["password"],
        )
    if password_attempt != user.password: raise UnAuthorisedError("Passwords dont match") # this isnt right, this should happen with a cognito method i just cant find the auth flow rn

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
    os.environ['userpool_id'] = "ap-southeast-2_VFb1ZYdES"
    os.environ['client_id'] = "2dlt20dc56pol6kdj2jhs9aogu"
    os.environ['user_table'] = 'dolfinStack-DolfinUserTable9DD22DDB-16KREE83F8Y57'

    # body = {
    #     "first": "fakefirst",
    #     "last": "fakelast",
    #     "nickname": "fakenickname",
    #     "email": "jarrodmccarthy12@gmail.com",
    #     "password": "fakep@ssword1234",
    #     "role": 0
    # }

    event = {
        'httpMethod': 'POST',
        'resource': '/auth/account',
        'queryStringParameters': {
            "email": "jarrodmccarthy12@gmail.com",
            "password": "fakep@ssword1234"
        },
        'pathParameters': {},
        #'body' : json.dumps(body)
    }

    resp = handler(event, context=None)
    print(resp)