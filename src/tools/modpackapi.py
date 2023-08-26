import requests
from src.config import Config
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

    def create_modpack_directory(self, uuid, token):
        """
        Cria um diretório para uma nova modpack.
        
        :param uuid: O UUID da modpack.
        :param token: O token de autenticação.
        :return: Um dicionário contendo a resposta da API.
        """
        url = f"{self.base_url}/createModpackDirectory/{uuid}/{token}"
        response = requests.post(url)
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

# Exemplo de uso da classe ModpackApi
if __name__ == "__main__":
    api = ModpackApi("http://localhost:3000")  # Substitua pela URL real da sua API

    # Criar um diretório para uma nova modpack
    create_response = api.create_modpack_directory("ihuhyuighyugyu", "4a5cbd28f070c2cf241648e6f9bf2e2b7bd3285e508a4c2526b4892e0da6ea95d5aa0453629011835cc9f10b81bab145ecad720372843db6a3209144d4e51f72")
    info_response = api.get_modpack_info("ihuhyuighyugyu")
    print(info_response)
    # # Enviar um arquivo para a pasta da modpack
    with open("modpacks/asdasd/modpack.json", "rb") as file:
        upload_response = api.upload_file("ihuhyuighyugyu", 
                                          "4a5cbd28f070c2cf241648e6f9bf2e2b7bd3285e508a4c2526b4892e0da6ea95d5aa0453629011835cc9f10b81bab145ecad720372843db6a3209144d4e51f72", 
                                          "modpack.json", 
                                          file)
        print(upload_response)

    # # Obter informações sobre uma modpack

