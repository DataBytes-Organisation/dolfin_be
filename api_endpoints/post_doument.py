import json
import os
from Shared.errors import handle_error_response


def main(event):
    """ This endpoint runs the document processing state machine"""
    result = {}
    return result

@handle_error_response
def handler(event, context):
    return main(event)
        
    
if __name__ == "__main__":
    os.environ['userpool_id'] = "ap-southeast-2_VBY3YR6zP"
    os.environ['client_id'] = "1m2k4aevejsj37uvej971dqj55"
    os.environ['user_table'] = 'dolfinStack-DolfinUserTable9DD22DDB-ZNR23DWVVW7F'

    body = {
        "first": "fakejarrod",
        "last": "fakemccarthy",
        "nickname": "fakenickname",
        "email": "your-email",
        "password": "fakep@ssword1234",
        "role": 1
    }

    event = {
        'httpMethod': 'POST',
        'resource': '/auth/account/user',
        'queryParameters': {
            "account_id": "ts#2023-03-17 14:04:20.164224-id#071292c7-564b-46dc-ad5e-3daae4507592"
        },
        'pathParameters': {},
        'body' : json.dumps(body)
    }

    resp = handler(event, context=None)
    print(resp)