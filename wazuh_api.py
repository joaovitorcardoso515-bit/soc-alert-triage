import requests
from requests.auth import HTTPBasicAuth

from config import WAZUH_HOST, WAZUH_USER, WAZUH_PASSWORD


class WazuhAPI:

    def __init__(self):
        self.base_url = WAZUH_HOST
        self.token = None

    def authenticate(self):

        url = f"{self.base_url}/security/user/authenticate"

        response = requests.get(
            url,
            auth=HTTPBasicAuth(WAZUH_USER, WAZUH_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            self.token = response.json()["data"]["token"]
            print("✅ Autenticado com sucesso!")
            return True

        print("❌ Erro ao autenticar")
        print(response.text)
        return False