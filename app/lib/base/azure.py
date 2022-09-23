import msal
import requests


class AzureManager:
    __scope: list = ["User.Read"]
    __authority: str = "https://login.microsoftonline.com/{0}"
    __graph_endpoint: str = 'https://graph.microsoft.com/v1.0'
    __tenant_id: str = ''
    __client_id: str = ''
    __client_secret: str = ''
    __redirect_to: str = ''

    @property
    def tenant_id(self) -> str:
        return self.__tenant_id

    @property
    def client_id(self) -> str:
        return self.__client_id

    @property
    def client_secret(self) -> str:
        return self.__client_secret

    @property
    def redirect_to(self) -> str:
        return self.__redirect_to

    def __init__(self, tenant_id, client_id: str, client_secret: str, redirect_to: str):
        self.__tenant_id = tenant_id
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_to = redirect_to

    def client_app(self) -> msal.ConfidentialClientApplication:
        return msal.ConfidentialClientApplication(
            client_id=self.__client_id,
            authority=self.__authority.format(self.__tenant_id),
            client_credential=self.__client_secret
        )

    def build_auth_code_flow(self):
        return self.client_app().initiate_auth_code_flow(
            scopes=self.__scope,
            redirect_uri=self.__redirect_to
        )

    def process_response(self, flow: dict, args: dict):
        result = self.client_app().acquire_token_by_auth_code_flow(flow, args)
        return result

    def get_logout_url(self, redirect_to: str) -> str:
        return self.__authority.format(self.__tenant_id) + "/oauth2/v2.0/logout?post_logout_redirect_uri={0}".format(
            redirect_to)

    def get_user_info(self, access_token: str) -> dict:
        try:
            url = "{0}/me".format(self.__graph_endpoint)
            return requests.get(url, headers={'Authorization': 'Bearer {0}'.format(access_token)}).json()
        except Exception as e:
            return {}
