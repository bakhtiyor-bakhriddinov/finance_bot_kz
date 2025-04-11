from datetime import date
from typing import Optional
from uuid import UUID
import requests
import httpx
from urllib.parse import quote
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
                                params={'tg_id': tg_id})
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

    def get_departments(self, name: Optional[str] = None, id: Optional[UUID] = None):
        if name is not None:
            response = requests.get(f"{self.base_url}/departments", headers=self.headers, params={'name': name})
        elif id is not None:
            response = requests.get(f"{self.base_url}/departments/{id}", headers=self.headers)
        else:
            response = requests.get(f"{self.base_url}/departments", headers=self.headers)
        return response.json()

    def get_budget_balance(self, department_id, expense_type_id):
        response = requests.get(f"{self.base_url}/budget-balance", headers=self.headers,
                                params={'department_id': department_id, 'expense_type_id': expense_type_id}
                                )
        return response.json()

    def get_expense_types(
            self,
            name: Optional[str] = None,
            department_id: Optional[UUID] = None,
            start_date: Optional[date] = None,
            finish_date: Optional[date] = None
    ):
        if name is not None:
            response = requests.get(f"{self.base_url}/expense-types", headers=self.headers, params={'name': name})
        else:
            # response = requests.get(f"{self.base_url}/expense-types", headers=self.headers)
            response = requests.get(
                f"{self.base_url}/budgets",
                headers=self.headers,
                params={
                    'department_id': department_id,
                    'start_date': start_date,
                    'finish_date': finish_date
                }
            )

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

    def upload_files(self, files,file_name):
        # self.headers["Content-Type"] = "multipart/form-data"
        self.headers["Content-Type"] = None
        self.headers['filename'] = quote(file_name)
        response = requests.post(f"{self.base_url}/files/upload/bot/2", headers=self.headers, files=files)
        return response

    def create_request(self, body):
        self.headers["Content-Type"] = "application/json"
        response = requests.post(f"{self.base_url}/requests", headers=self.headers, json=body)
        return response

    def create_transaction(self, body):
        self.headers["Content-Type"] = "application/json"
        response = requests.post(f"{self.base_url}/transactions", headers=self.headers, json=body)
        return response

    def get_requests(self, client_id: Optional[str]=None, status: Optional[str]=None, number: Optional[int]=None):
        params = {}
        if client_id is not None:
            params['client_id'] = client_id
        if status is not None:
            params['status'] = status
        if number is not None:
            params['number'] = number

        response = requests.get(f"{self.base_url}/requests", headers=self.headers,
                                params=params)
        return response

    def update_request(self, body):
        self.headers["Content-Type"] = "application/json"
        response = requests.put(f"{self.base_url}/requests", headers=self.headers, json=body)
        return response


api_routes = ApiRoutes()
api_routes.login()
