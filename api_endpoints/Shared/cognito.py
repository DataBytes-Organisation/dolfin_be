import boto3
from authlib.jose import jwt
import requests
import json
from Shared.account import Account, User, Role

class Cognito:
    def __init__(self, pool_id: str, client_id: str) -> None:
        self.pool_id = pool_id
        self.client_id = client_id
        self.client = boto3.client('cognito-idp')
        self.cognito_pool_domain_url = None
        self.cognito_known_tokens_url = None

    def delete_user(self, username: str):
        try:
            response = self.client.admin_delete_user(
            UserPoolId=self.pool_id,
            Username=username
            )
            return response
        except Exception as e:
            raise Exception(f"Error {e}: Failed to delete User {username}")

    def create_user(self, user: User):
        try:
            response = self.client.admin_create_user(
                UserPoolId= self.pool_id,
                Username = user.email,
                UserAttributes=[
                    {
                        'Name': 'Given Name',
                        'Value': user.first,
                        'Name': 'Family Name',
                        'Value': user.last,
                        'Name': 'Full Name',
                        'Value': user.fullname,
                        'Name': 'name',
                        'Value': user.fullname,
                        'Name': 'nickname',
                        'Value': user.nickname,
                        'Name': 'email',
                        'Value': user.email
                    },
                ],
                ValidationData=[
                     {
                        'Name': 'Given Name',
                        'Value': user.first,
                        'Name': 'Family Name',
                        'Value': user.last,
                        'Name': 'Full Name',
                        'Value': user.fullname,
                        'Name': 'name',
                        'Value': user.fullname,                        
                        'Name': 'nickname',
                        'Value': user.nickname,
                        'Name': 'email',
                        'Value': user.email
                    },
                ],
                TemporaryPassword=user.password, #should come from user
                ForceAliasCreation=False,
                MessageAction='SUPPRESS',
                DesiredDeliveryMediums=[
                    'EMAIL',
                ],
                ClientMetadata={
                    'string': 'string'
                }
            )
            return response
        except Exception as e:
            raise Exception(f"Error {e}: Could not create user {user.fullname}")

    def _init_auth(self, cognito_username: str, user: User):
        """Initiate Auth (SRP) -> Returns Challenge"""
        try:
            response = self.client.initiate_auth(            
                AuthFlow='USER_PASSWORD_AUTH', #'USER_SRP_AUTH'|'REFRESH_TOKEN_AUTH'|'REFRESH_TOKEN'|'CUSTOM_AUTH'|'ADMIN_NO_SRP_AUTH'| 'USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': user.email,
                    'name': user.fullname,
                    'email':user.email,
                    'PASSWORD': user.password
                },
                ClientId=self.client_id,
            )
            return response
        except Exception as e:
            raise Exception(f"Error {e}: Issue with Authentication for {cognito_username}, likely incorrect credentials")

    def _respond_to_auth_challenge(self, init_auth_response, user: User, cognito_username: str): 
        """Respond to Auth Challenge -> Cognito Tokens"""
        try:
            cognito_username = init_auth_response["ChallengeParameters"].get('USER_ID_FOR_SRP') #needs testing
            cn = init_auth_response["ChallengeName"]
            sess = init_auth_response["Session"]
            challenge_params = init_auth_response["ChallengeParameters"]
            challenge_resp = {
                    'USERNAME': user.email,
                    'userAttributes.name': user.fullname,
                    'NEW_PASSWORD':user.password
                }
            response = self.client.respond_to_auth_challenge(
                ClientId=self.client_id,
                ChallengeName=cn,
                Session=sess,
                ChallengeResponses=challenge_resp
            )
            return response
        except Exception as e:
             raise Exception(f"Error {e}: Issue responding to auth challenge for user {user.email}")
        
    def get_token(self, user: User, cognito_username: str):
        init_auth_response = self._init_auth(cognito_username, user)
        if init_auth_response.get('ChallengeName') is None:
            return init_auth_response #no challenge was issued
        response = self._respond_to_auth_challenge(init_auth_response, user, cognito_username)
        return response
        
    def refresh_token(self, refresh_token: str):
        try:
            result = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token,
                }
            )
            return result
        except Exception as e:
            raise Exception(f"Error: {e}")
        
    def sign_in(self, user: User):
        get_token_response = self.get_token(user, user.email)
        return get_token_response

    def sign_up(self, user: User): 
        response = self.create_user(user)
        #cognito_username = response['User'].get('Username')
        return self.sign_in(user)


    def get_JWT_from_code(self, code):
        try:
            payload=f'grant_type=authorization_code&client_id={self.client_id}&code={code}'#&redirect_uri={call_back_uri}
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            }
            response = requests.request("POST", self.cognito_pool_domain, headers=headers, data=payload)
            tokens = json.loads(response.text)
            return tokens
        except Exception as e:
            raise Exception(f"Error {e}: Couldn't get JWT from auth code")

    # def code_to_jwt_dict(self, code):
    #     tokens = self.get_JWT_from_code(code)
    #     refresh_token = tokens['refresh_token']
    #     access_token = tokens['access_token']
    #     JWT = tokens['id_token']
    #     response = requests.request("GET", self.cognito_known_tokens_url, headers={}, data={})
    #     public = json.loads(response.text) #loads a json str into dict
    #     return jwt.decode(JWT, public) #decode jwt 
