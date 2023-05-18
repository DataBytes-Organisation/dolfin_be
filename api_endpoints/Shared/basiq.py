import requests
import json

class Basiq:
    def __init__(self, basiq_id: str) -> None:
        self.basiq_id = basiq_id
        self.KEY = "NDNmNTczMGQtZjJhZC00ODQ4LTkxZDUtN2VhMDMyNzgyZmIyOjNiM2MwMjFlLTUzZDMtNDg3MC04MjU3LTk1YzRkNWI2MmU5Mg==" #does not belong here
        self.base_url = "https://au-api.basiq.io/"

    def get_auth_token(self):
        url = self.base_url+"token"
        payload = "scope=SERVER_ACCESS"
        headers = {
            "accept": "application/json",
            "basiq-version": "3.0",
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.KEY}"
        }

        response = requests.post(url, data=payload, headers=headers)
        json_response = response.json()
        access_token = "Bearer " + json_response["access_token"]
        return access_token
    
    def get_accounts(self, access_token):
        

        url = f"{self.base_url}users/{self.basiq_id}/accounts"

        headers = {
            "accept": "application/json",
            "authorization": access_token,
            }

        response = requests.get(url, headers=headers)
        return json.loads(response.text)

    def get_all_transactions_for_user(self, access_token):
        url = f"{self.base_url}users/{self.basiq_id}/transactions"

        headers = {
            "accept": "application/json",
            "authorization": access_token,
            }
        
        response = requests.get(url, headers=headers)
        return json.loads(response.text)