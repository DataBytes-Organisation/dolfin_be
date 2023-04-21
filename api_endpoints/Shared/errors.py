import json
from Shared.api import API
class ClientError(Exception):
    pass

class NotFoundError(Exception):
    pass

class ServerError(Exception):
    pass

def handle_error_response(func):
    def wrapper(event, context):
        try:
            response = func(event, context)        
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
    return wrapper