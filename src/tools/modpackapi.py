import requests
from src.tools import JasonAutoFix
import logging
class ModpackApi:
    """
    Uma classe que oferece métodos para interagir com uma API de modpacks.
    
    A classe fornece funcionalidades para criar diretórios de modpacks, fazer upload e download de arquivos,
    obter informações sobre modpacks e muito mais.
    
    :param base_url: A URL base da API.
    """
    
    def __init__(self, base_url):
        """
        Inicializa uma nova instância da classe ModpackApi.
        
        :param base_url: A URL base da API.
        """
        self.base_url = base_url
        self.logger = logging.getLogger(f'Sync-Api')

    def create_modpack_directory(self, uuid, token):
        """
        Cria um diretório para uma nova modpack.
        
        :param uuid: O UUID da modpack.
        :param token: O token de autenticação.
        :return: Um dicionário contendo a resposta da API.
        """
        url = f"{self.base_url}/createModpackDirectory/{uuid}/{token}"
        response = requests.post(url)
        self.logger.debug(f'Creating directory for the modpack (UUID: {uuid}, Token: {token})')
        self.logger.debug(f'Request status: {response.status_code}')
        return {'status': response.status_code , 'json':response.json(), 'response':response}
    
    def upload_file(self, uuid, token, remoteDirfile, file):
        """
        Faz upload de um arquivo para a pasta da modpack.
        
        :param uuid: O UUID da modpack.
        :param token: O token de autenticação.
        :param file: O arquivo a ser enviado.
        :param remoteDirfile: O caminho do arquivo, que pode ser absoluto ou relativo à pasta da modpack.
        :return: Um dicionário contendo a resposta da API.
        """
        # Constrói a URL de upload com base no UUID e no caminho do arquivo remoto
        url = f"{self.base_url}/uploadFile/{uuid}/{remoteDirfile}"
        # Define os cabeçalhos da requisição
        headers = {"token": f"{token}"}
        # Cria um dicionário de arquivos para enviar na requisição
        files = {"file": file}
        # Envia a requisição POST para a API de upload
        response = requests.post(url, files=files, headers=headers)
        self.logger.debug(f'Uploading a file to the modpack (UUID: {uuid}, Token: {token})')
        self.logger.debug(f'Remote file path: {remoteDirfile}')
        self.logger.debug(f'Request status: {response.status_code}')
        try:
            json = response.json()
        except:
            json = {}
        return {'status': response.status_code, 'json': json, 'response': response}
    
    
    def upload_modpack_zip(self, uuid, token, zip_file_path):
        """
        Faz upload de um arquivo ZIP para a pasta da modpack e realiza a descompactação.
        
        :param uuid: O UUID da modpack.
        :param token: O token de autenticação.
        :param zip_file_path: O caminho para o arquivo ZIP a ser enviado.
        :return: Um dicionário contendo a resposta da API.
        """
        # Constrói a URL de upload com base no UUID
        url = f"{self.base_url}/uploadAndUnzip/{uuid}"
        # Define os cabeçalhos da requisição
        headers = {"token": f"{token}"}
        # Lê o conteúdo do arquivo ZIP
        with open(zip_file_path, "rb") as zip_file:
            # Cria um dicionário de arquivos para enviar na requisição
            files = {"file": zip_file}
            # Envia a requisição POST para a API de upload e descompactação
            response = requests.post(url, files=files, headers=headers)
            self.logger.debug(f'Checking ownership (UUID: {uuid}, Token: {token})')
            self.logger.debug(f'Request status: {response.status_code}')

        try:
            json = response.json()
        except:
            json = {}
        return {'status': response.status_code, 'json': json, 'response': response}
    
    def get_modpack_info(self, uuid):
        """
        Obtém informações sobre uma modpack com base no UUID.
        
        :param uuid: O UUID da modpack.
        :return: Um dicionário contendo as informações da modpack.
        """
        url = f"{self.base_url}/getModpackInfo/{uuid}"
        response = requests.get(url)
        return {'status': response.status_code , 'json':response.json(), 'response':response}
    
    def get_modpack_hash_map(self, uuid):
        """
        Obtém o mapa de hash de uma modpack com base no UUID.

        :param uuid: O UUID da modpack.
        :return: Um dicionário contendo as informações do mapa de hash da modpack.
        """
        url = f"{self.base_url}/getModpackHashMap/{uuid}"
        response = requests.get(url)
        return {'status': response.status_code , 'json':response.json(), 'response':response}

    def download_modpack_file(self, uuid, file_path):
        """
        Faz o download de um arquivo da pasta da modpack.
        
        :param uuid: O UUID da modpack.
        :param file_path: O caminho do arquivo na modpack.
        :return: O conteúdo do arquivo baixado (bytes) ou None em caso de erro.
        """
        url = f"{self.base_url}/getModpackFile/{uuid}/{file_path}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return {'status': response.status_code , 'content':response.content, 'response':response}
        else:
            return {'status': response.status_code , 'content':None, 'response':response}
        
    def remove_modpack_file(self, uuid, file_path):
        """
        Remove um arquivo da pasta da modpack.

        :param uuid: O UUID da modpack.
        :param file_path: O caminho do arquivo a ser removido.
        :return: Um dicionário contendo a resposta da API.
        """
        url = f"{self.base_url}/removeModpackFile/{uuid}/{file_path}"
        response = requests.delete(url)
        return {'status': response.status_code, 'json': response.json(), 'response': response}

    def delete_modpack(self, uuid):
        """
        Remove completamente uma modpack, incluindo todos os arquivos e pastas.

        :param uuid: O UUID da modpack.
        :return: Um dicionário contendo a resposta da API.
        """
        url = f"{self.base_url}/removeModpack/{uuid}"
        response = requests.delete(url)
        return {'status': response.status_code, 'json': response.json(), 'response': response}

    def is_owner(self, uuid, token):
        """
        Verifica se um token é do dono da modpack com o UUID fornecido.
        
        :param uuid: O UUID da modpack.
        :param token: O token de autenticação.
        :return: True se o token corresponder ao dono da modpack, False caso contrário ou em caso de erro.
        """
        url = f"{self.base_url}/isOwner/{uuid}"
        try:
            response = requests.post(url, json={"token": token}, timeout=(3, 3))
            if response.json()['code'] == -1:
                return True
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.Timeout:
            self.logger.error("The request timed out after 2 seconds")
            return False  # A solicitação atingiu o tempo limite de 2 segundos
        except Exception as e:
            self.logger.error(f"HTTP request error: {e}")
            return False
