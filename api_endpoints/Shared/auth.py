import boto3
import uuid
from datetime import datetime

class Authorizer:
    def __init__(self, access_table: str, endpoint_arn: str):#
        self.endpoint_arn = endpoint_arn 
        print("ENDPOINT ARN : {}".format(self.endpoint_arn))
        ddb = boto3.resource('dynamodb')
        self.access_table = ddb.Table(access_table)
        
    def get_key_by_value(self, value):
        print("Attempting to get {} from {}".format(value, self.access_table))
        items = self.access_table.query(
            IndexName='key_value_index',
            KeyConditionExpression="#key_value=:key_value",
            ExpressionAttributeValues={
                ':key_value': "KEYVALUE#{}".format(str(value).upper()),
            },
            ExpressionAttributeNames= { "#key_value": "key_value" }
        ).get('Items')
        return items 

    def get_key_by_id(self, id):
        print("Attempting to get {} from {}".format(id, self.access_table))
        items = self.access_table.query(
            #IndexName='type-brand-index',
            KeyConditionExpression="#key_id=:key_id",
            ExpressionAttributeValues={
                ':key_id': "KEYID#{}".format(str(id).upper()),
            },
            ExpressionAttributeNames= { "#key_id": "key_id" }
        ).get('Items')
        return items

    def check_enabled(self, items):
        print("ITEMS IN CHECKED ENABLED: {}".format(items))
        if items['enabled'] == "ENABLED#TRUE":
            return True
        else:
            return False

    def _check_token(self, token):
        items = self.get_key_by_value(value=token)
        print(items)
        if len(items) > 0:
            print("ITEM 0  IN CHECK Token: {}".format(items[0]))
            if self.check_enabled(items[0]):
                return "Allow" #, "Deny"
            else:
                return "Deny"
        return "Deny"

    def build_response(self, auth):
        authResponse = { 
            "principalId": "abc123", 
            "policyDocument": 
                { "Version": "2012-10-17", 
                    "Statement": [
                        {   
                            "Action": "execute-api:Invoke", 
                            "Resource": ["{}/*/*".format(self.endpoint_arn)], 
                            "Effect": auth
                        }
                    ] 
                }
            }
        return authResponse
    
    def create_api_key(self, key_request: object):
        print(key_request)
        required_attrs = ['key_id']
        for attr in required_attrs: 
            if attr not in key_request: raise KeyError(attr)
        
        key_id = str(key_request.pop('key_id')).upper()
        key_value = str(uuid.uuid4()).upper()
        
        item = {
            'key_id': "KEYID#{}".format(key_id),
            'key_value': "KEYVALUE#{}".format(key_value),
            'enabled': "ENABLED#TRUE",
            'created': "CREATED#{}".format(datetime.now()),
            'lastEdited': f"{datetime.now()}",
        } 
        # Add the remaining keys
        if len(key_request.keys()) > 0:
            for key in key_request:
                item[key] = '{}#{}'.format(str(key).upper(), str(key_request[key]).upper())
            
        self.access_table.put_item(
            Item=item
        )
        result = self.get_key_by_id(id=key_id)
        return result
    
    def update_key(self, key_id, attributes):
        key = self._get_key_by_id(key_id)
        try:
            if ('key_id' in key[0].keys() and 'key_value' in key[0].keys()):
                return self.patch_key(key_id=key[0]['key_id'], attributes=attributes)
            else:
                return {'msg': 'There was an issue updating key'}
        except Exception as e:
            raise e

    def build_update_expression(self, params):
        '''Constructs the update expression
        Input of params = { 'att1': 'val1', 'att2': 'val2' }
        becomes
            update_expression = 'set #att1 = :att1, #att2 = :att2'
            update_names = { '#att1': 'att1', '#att2': 'att2' }
            update_values = { ':att1': 'val1', ':att2': 'val2' }
            
        returned as (update_expression, update_names, update_values)
        '''
        update_names = dict()
        update_values = dict()
        update_expression = ["set "]
        
        for key,val in params.items():
            update_names[f"#{key}"] = key # To avoid 'reserved word' conflicts
            update_values[f":{key}"] = val # To avoid 'reserved word' conflicts
            update_expression.append(f" #{key} = :{key},")
        
        return "".join(update_expression)[:-1], update_names, update_values

    def _update_enable(self, key, enabled):
        if enabled:
            key['enabled'] = "ENABLED#TRUE"
        else:
            key['enabled'] = "ENABLED#FALSE"
        return key

    def patch_key(self, key_id, attributes):
        update_expression, update_names, update_values = self.build_update_expression(attributes)
        r = self.access_table.update_item(
            Key={
                'key_id': key_id,
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=update_names,
            ExpressionAttributeValues=update_values,
            ConditionExpression='attribute_exists(key_id)'
        )
        if 'error' in r:
            raise Exception
        result = self._get_key_by_id(id=key_id.replace('KEYID#', ''))
        return result