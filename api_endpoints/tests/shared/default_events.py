import json
def get_example_event():
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
    return event