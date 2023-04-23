import json
import os
from Shared.errors import handle_error_response
from Shared.api import API
from Shared.cognito import Cognito
from Shared.dynamo import Dynamo
from Shared.account import User, Role, Account

def main(event):
    """ This endpoint assumes you already have an account and are creating new users
    in that account"""

    payload = API.parse_payload(event)

    #account_id = payload['queryParameters']['account_id']
    
    account = Account()
    user_pool = Cognito(pool_id=os.environ['userpool_id'], client_id = os.environ['client_id'])
    dynamo = Dynamo(table_name=os.environ['user_table'])
    
    role = payload["body"]["role"] #0, 1, 2
    role = Role(role)

    user = User(
        account = account,
        role = role,
        first = payload["body"]["first"],
        last = payload["body"]["last"],
        nickname = payload["body"]["nickname"],
        email = payload["body"]["email"],
        password = payload["body"]["password"],
        )
    
    sign_up_result = user_pool.sign_up(user)
    
    dynamo = Dynamo(table_name=os.environ['user_table'])

    dynamo.put_item(user.to_dynamo())

    result = dict(
        auth = sign_up_result.get('AuthenticationResult'),
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

    body = {
        "first": "fakejarrod",
        "last": "fakemccarthy",
        "nickname": "fakenickname",
        "email": "jmdifferent@gmail.com",
        "password": "fakep@ssword1234",
        "role": 1
    }

    event = {
        'httpMethod': 'POST',
        'resource': '/auth/account/user',
        'queryParameters': {
            #"account_id": "ts#2023-03-17 14:04:20.164224-id#071292c7-564b-46dc-ad5e-3daae4507592"
        },
        'pathParameters': {},
        'body' : json.dumps(body)
    }

    resp = handler(event=event, context=None)
    print(resp)