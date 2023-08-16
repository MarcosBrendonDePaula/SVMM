import json
import os
import base64

class Modpack:
    """Classe para representar e gerenciar modpacks do jogo."""

    def __init__(self, name, image="", base_directory=""):
        """Inicializa uma instância da classe Modpack."""
        self.name = name
        self.image = image

        folder_path = os.path.join(base_directory, 'modpacks', name)
        self.folder_path = folder_path

        self.mods_enabled_path = os.path.join(self.folder_path, 'mods_enabled')
        self.mods_disabled_path = os.path.join(self.folder_path, 'mods_disabled')
        self.saves_path = os.path.join(self.folder_path, 'saves')

        os.makedirs(self.mods_enabled_path, exist_ok=True)
        os.makedirs(self.mods_disabled_path, exist_ok=True)
        os.makedirs(self.saves_path, exist_ok=True)

        # Load default image as base64 if no image is provided
        if not self.image:
            default_image_path = os.path.join(base_directory, 'resources', 'img', 'default_thumb.png')
            with open(default_image_path, 'rb') as image_file:
                default_image_data = image_file.read()
                self.image = base64.b64encode(default_image_data).decode('utf-8')
        
        # Check if the modpack is new and automatically save its data
        if not os.path.exists(os.path.join(self.folder_path, 'modpack.json')):
            self.save()

    def to_dict(self):
        """Converte a modpack em um dicionário."""
        return {
            'name': self.name,
            'image': self.image
        }
    
    def mods_folder(self):
        return self.mods_enabled_path

    def save(self):
        """
        Salva os dados da modpack em um arquivo JSON no diretório da modpack.
        """

        modpack_data = self.to_dict()
        filename = os.path.join(self.folder_path, 'modpack.json')

        with open(filename, 'w') as json_file:
            json.dump(modpack_data, json_file, indent=4)

    @classmethod
    def load_from_json(cls, name, base_directory=""):
        """
        Carrega uma modpack a partir de um arquivo JSON no diretório.

        Args:
            name (str): Nome da modpack.
            base_directory (str): Caminho para o diretório da modpack.

        Returns:
            Modpack: Instância da classe Modpack com os dados carregados.
        """
        json_filename = os.path.join(base_directory, 'modpacks', name, 'modpack.json')
        if os.path.exists(json_filename):
            with open(json_filename, 'r') as json_file:
                modpack_data = json.load(json_file)

            modpack = cls(name, modpack_data['image'], base_directory=base_directory)
            return modpack

        return None  # Retorna None se o arquivo JSON não existir
    
    @staticmethod
    def get_all_modpacks(base_directory=""):
        """
        Carrega todas as modpacks já criadas a partir dos arquivos JSON.

        Args:
            base_directory (str): Caminho para o diretório base das modpacks.

        Returns:
            list[Modpack]: Uma lista de instâncias da classe Modpack.
        """
        modpacks = []
        modpacks_directory = os.path.join(base_directory, 'modpacks')
        
        if os.path.exists(modpacks_directory):
            for modpack_name in os.listdir(modpacks_directory):
                modpack = Modpack.load_from_json(modpack_name, base_directory)
                if modpack:
                    modpacks.append(modpack)
        return modpacks

    @staticmethod
    def list_modpacks(base_directory=""):
        """
        Lista os nomes de todas as modpacks válidas existentes.

        Args:
            base_directory (str): Caminho para o diretório base das modpacks.

        Returns:
            list[str]: Uma lista de nomes de modpacks válidas.
        """
        valid_modpack_names = []
        modpacks_directory = os.path.join(base_directory, 'modpacks')
        
        if os.path.exists(modpacks_directory):
            for modpack_name in os.listdir(modpacks_directory):
                modpack_path = os.path.join(modpacks_directory, modpack_name)
                modpack_json_path = os.path.join(modpack_path, 'modpack.json')
                
                if os.path.exists(modpack_json_path):
                    try:
                        with open(modpack_json_path, 'r') as json_file:
                            modpack_data = json.load(json_file)
                        
                        # Check if the modpack data is valid
                        if 'name' in modpack_data and 'image' in modpack_data:
                            valid_modpack_names.append(modpack_name)
                    except (json.JSONDecodeError, KeyError):
                        pass  # Ignore invalid JSON or missing keys
        
        return valid_modpack_names
