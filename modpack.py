import json
import os
import base64

from mod import Mod

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

    def enable_mod(self, mod_name):
        """
        Habilita um mod, movendo-o da pasta 'mods_disabled' para 'mods_enabled'.

        Args:
            mod_name (str): Nome do mod a ser habilitado.
        """
        source_path = os.path.join(self.mods_disabled_path, mod_name)
        destination_path = os.path.join(self.mods_enabled_path, mod_name)
        
        if os.path.exists(source_path):
            os.rename(source_path, destination_path)
            self.save()

    def enable_all_mods(self):
        """
        Habilita todos os mods desabilitados, movendo-os para a pasta 'mods_enabled'.
        """
        for mod in self.list_disabled_mods():
            self.enable_mod(mod)

    def disable_all_mods(self):
        """
        Desabilita todos os mods habilitados, movendo-os para a pasta 'mods_disabled'.
        """
        for mod in self.list_enabled_mods():
            self.disable_mod(mod)

    def disable_mod(self, mod_name):
        """
        Desabilita um mod, movendo-o da pasta 'mods_enabled' para 'mods_disabled'.

        Args:
            mod_name (str): Nome do mod a ser desabilitado.
        """
        source_path = os.path.join(self.mods_enabled_path, mod_name)
        destination_path = os.path.join(self.mods_disabled_path, mod_name)
        
        if os.path.exists(source_path):
            os.rename(source_path, destination_path)
            self.save()

    def enable_mods(self, mods_to_enable):
        """
        Habilita uma lista de mods, movendo-os da pasta 'mods_disabled' para 'mods_enabled'.

        Args:
            mods_to_enable (list[str]): Lista de nomes de mods a serem habilitados.
        """
        for mod in mods_to_enable:
            self.enable_mod(mod)

    def list_enabled_mods(self):
        """
        Lista os nomes dos mods habilitados na modpack.

        Returns:
            list[str]: Uma lista de nomes de mods habilitados.
        """
        enabled_mods = []
        if os.path.exists(self.mods_enabled_path):
            enabled_mods = os.listdir(self.mods_enabled_path)
        return enabled_mods

    def list_disabled_mods(self):
        """
        Lista os nomes dos mods desabilitados na modpack.

        Returns:
            list[str]: Uma lista de nomes de mods desabilitados.
        """
        disabled_mods = []
        if os.path.exists(self.mods_disabled_path):
            disabled_mods = os.listdir(self.mods_disabled_path)
        return disabled_mods
    
    def list_all_mods(self):
        """
        Lista os nomes de todos os mods (habilitados e desabilitados) na modpack.

        Returns:
            dict: Um dicionário com duas chaves, 'enabled' e 'disabled', contendo listas de nomes de mods.
        """
        all_mods = {
            'enabled': [],
            'disabled': []
        }
        
        if os.path.exists(self.mods_enabled_path):
            all_mods['enabled'] = os.listdir(self.mods_enabled_path)
        
        if os.path.exists(self.mods_disabled_path):
            all_mods['disabled'] = os.listdir(self.mods_disabled_path)
        
        return all_mods

    def disable_mods(self, mods_to_disable):
        """
        Desabilita uma lista de mods, movendo-os da pasta 'mods_enabled' para 'mods_disabled'.

        Args:
            mods_to_disable (list[str]): Lista de nomes de mods a serem desabilitados.
        """
        for mod in mods_to_disable:
            self.disable_mod(mod)

    def get_enabled_mods(self):
        """
        Retorna uma lista de objetos da classe Mod para os mods habilitados.
        """
        enabled_mods = []
        for mod_name in self.list_enabled_mods():
            mod_folder_path = os.path.join(self.mods_enabled_path, mod_name)
            mod = Mod(mod_folder_path, self.mods_enabled_path)
            enabled_mods.append(mod)
        return enabled_mods

    def get_disabled_mods(self):
        """
        Retorna uma lista de objetos da classe Mod para os mods desabilitados.
        """
        disabled_mods = []
        for mod_name in self.list_disabled_mods():
            mod_folder_path = os.path.join(self.mods_disabled_path, mod_name)
            mod = Mod(mod_folder_path, self.mods_disabled_path)
            disabled_mods.append(mod)
        return disabled_mods

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
