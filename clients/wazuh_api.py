import requests
import urllib3
from requests.auth import HTTPBasicAuth

from config import WAZUH_HOST, WAZUH_USER, WAZUH_PASSWORD

# Remove o aviso de certificado autoassinado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    def get_alerts(self, limit=10):

    if not self.token:
        self.authenticate()

    url = f"{self.base_url}/alerts?limit={limit}"

    headers = {
        "Authorization": f"Bearer {self.token}"
    }

    response = requests.get(
        url,
        headers=headers,
        verify=False
    )

    if response.status_code == 200:
        return response.json()

    print(f"Erro: {response.status_code}")
    print(response.text)

    return None