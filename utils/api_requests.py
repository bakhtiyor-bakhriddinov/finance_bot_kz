from typing import Optional
from uuid import UUID
import requests
from configs.variables import BASE_URL, BOT_USER, BOT_PASSWORD



class ApiRoutes:
    access_token = None
    headers = None
    base_url = str(BASE_URL)

    def login(self):
        url = f"{self.base_url}/login"
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'password',
            'username': BOT_USER,
            'password': BOT_PASSWORD,
            'scope': '',
            'client_id': 'string',
            'client_secret': 'string'
        }
        response = requests.post(url=url, headers=headers, data=body)
        response_data = response.json()
        # print("access_token: ", self.access_token)
        self.access_token = response_data
        # print("access_token: ", self.access_token)
        self.headers = {
            "accept": "application/json",
            "Authorization": f"{self.access_token['token_type']} {self.access_token['access_token']}"
        }
        # return response_data

    def get_client(self, tg_id):
        response = requests.get(f"{self.base_url}/clients", headers=self.headers,
                                params={'tg_id': tg_id, 'is_active': True})
        return response

    def edit_user(self, tg_id, group_id: Optional[int] = None, branch_id: Optional[UUID] = None):
        body = {
            "telegram_id": tg_id
        }
        if group_id:
            body["group_id"] = group_id
        if branch_id:
            body["branch_id"] = branch_id

        response = requests.put(f"{self.base_url}/collector/user/", headers=self.headers, json=body)
        return response.json()

    def create_client(self, body):
        response = requests.post(f"{self.base_url}/clients", headers=self.headers, json=body)
        return response

    def get_departments(self, name: Optional[str] = None):
        if name is not None:
            response = requests.get(f"{self.base_url}/departments", headers=self.headers, params={'name': name})
        else:
            response = requests.get(f"{self.base_url}/departments", headers=self.headers)
        return response.json()

    def get_expense_types(self, name: Optional[str] = None):
        if name is not None:
            response = requests.get(f"{self.base_url}/expense-types", headers=self.headers, params={'name': name})
        else:
            response = requests.get(f"{self.base_url}/expense-types", headers=self.headers)
        return response.json()

    def get_buyers(self, name: Optional[str] = None):
        if name is not None:
            response = requests.get(f"{self.base_url}/buyers", headers=self.headers, params={'name': name})
        else:
            response = requests.get(f"{self.base_url}/buyers", headers=self.headers)
        return response.json()

    def get_suppliers(self, name: Optional[str] = None):
        if name is not None:
            response = requests.get(f"{self.base_url}/suppliers", headers=self.headers, params={'name': name})
        else:
            response = requests.get(f"{self.base_url}/suppliers", headers=self.headers)
        return response.json()

    def get_payment_types(self, name: Optional[str] = None):
        if name is not None:
            response = requests.get(f"{self.base_url}/payment-types", headers=self.headers, params={'name': name})
        else:
            response = requests.get(f"{self.base_url}/payment-types", headers=self.headers)
        return response.json()

    def upload_files(self, files):
        response = requests.post(f"{self.base_url}/files/upload", headers=self.headers, files=files)
        return response

    def create_request(self, body):
        self.headers["Content-Type"] = "application/json"
        response = requests.post(f"{self.base_url}/requests", headers=self.headers, json=body)
        return response

    def get_requests(self, client_id, status):
        response = requests.get(f"{self.base_url}/requests", headers=self.headers,
                                params={'client_id': client_id, 'status': status})
        return response

    def update_request(self, body):
        self.headers["Content-Type"] = "application/json"
        response = requests.put(f"{self.base_url}/requests", headers=self.headers, json=body)
        return response


api_routes = ApiRoutes()
api_routes.login()
