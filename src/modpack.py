import json
import os
import base64
import shutil
import uuid
import secrets
import tempfile
import re
from pyunpack import Archive

from src.tools import Extractor

from src.mod import Mod

class Modpack:
    """Classe para representar e gerenciar modpacks do jogo."""

    def __init__(self, name, image="", _uuid="", token="", hash="", version="0.0.0", base_directory=""):
        """Inicializa uma instância da classe Modpack."""
        
        f_save = False
        if _uuid == "":
            _uuid = uuid.uuid4().hex
            f_save = True
        if token == "":
            token = secrets.token_hex(64)
            f_save = True
        
        self.name    = name
        self.image   = image
        self._uuid   = _uuid
        self.token   = token
        self.hash    = hash
        self.version = version
        
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
        if f_save:
            self.save()
        
    def to_dict(self):
        """Converte a modpack em um dicionário."""
        return {
            'name': self.name,
            'image': self.image,
            'token': self.token,
            'uuid' : self._uuid,
            'hash' : self.hash,
            'version': self.version
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

    def rename_modpack(self, new_name):
        """
        Renomeia a modpack e atualiza a pasta correspondente.

        Args:
            new_name (str): Novo nome da modpack.
        """
        # Verifique se o novo nome é diferente do atual
        if new_name != self.name:
            # Determine o diretório base das modpacks
            base_directory = os.path.dirname(self.folder_path)
            print(base_directory)
            # Calcule o novo caminho para a pasta da modpack
            new_folder_path = os.path.join(base_directory, new_name)
            print(new_folder_path )
            # Renomeie a pasta da modpack
            os.rename(self.folder_path, new_folder_path)
            self.folder_path = new_folder_path

            # Atualize o nome da modpack
            self.name = new_name
            self.save()
    
    #auto instalador de mods zip e rar --------------------------
    def install_mod(self, file):
        #Criar pasta oculta temporaria para instalar os mods
        temp_dir = os.path.join(os.getcwd(), 'temp_files') 
       
        os.makedirs(temp_dir, exist_ok=True)
        os.system(f'attrib +h "{temp_dir}"')
        
        try:
            Extractor.extract(file, os.path.join(temp_dir, ''))
        except Exception as e:
            print(e)
            return
        
        self._fix_folder_names(temp_dir)
        mods = self.find_installed_mods(temp_dir)
        destination_folder = self.mods_enabled_path
        
        for mod_path in mods:
            mod_name = os.path.basename(mod_path)
            mod_destination = os.path.join(destination_folder, mod_name)
            
            if not os.path.exists(mod_destination):
                shutil.move(mod_path, mod_destination)
            else:
                print(f"O mod '{mod_name}' já está instalado.")
        
        # Remover a pasta pai onde os mods estavam originalmente
        try:
            shutil.rmtree(temp_dir)
            print(f"Diretório '{temp_dir}' removido após a instalação dos mods.")
        except Exception as e:
            print(f"Erro ao remover pasta temporária '{temp_dir}':", e)

    def _fix_folder_names(self, source_folder):

        """
        Corrige os nomes de pastas inválidos.

        Args:
            source_folder (str): Caminho para a pasta com os nomes inválidos.
        """
        for root, dirs, files in os.walk(source_folder):
            for dir_name in dirs:
                valid_folder_name = re.sub(r'[<>:"/\\|?*]', '_', dir_name)
                valid_folder_name = valid_folder_name.replace(' ', '_')
                source_dir = os.path.join(root, dir_name)
                destination_dir = os.path.join(root, valid_folder_name)  # Caminho completo sem mover
                os.rename(source_dir, destination_dir)
                self._fix_folder_names(destination_dir)

    def find_installed_mods(self, folder):
        """
        Localiza os mods instalados em uma pasta.

        Args:
            folder (str): Caminho para a pasta onde os mods estão instalados.

        Returns:
            list[str]: Lista com os caminhos dos mods instalados.
        """
        installed_mods = []
        for root, dirs, files in os.walk(folder, topdown=False):  # Percorre os subdiretórios de baixo para cima
            for file_name in files:
                if file_name == "manifest.json":
                    mod_path = root
                    installed_mods.append(mod_path)
                    break
        return installed_mods
    #auto instalador de mods zip e rar --------------------------
    
    def mod_dependencies_complete(self, mod):
        """
        Verifica se as dependências do mod estão completas na lista de mods da modpack.

        Args:
            mod (Mod): O objeto Mod cujas dependências devem ser verificadas.

        Returns:
            bool: True se todas as dependências estiverem completas, False caso contrário.
        """
        mods_enabled = self.get_enabled_mods()
        missing_dependencies = []
        
        for dependency in mod.dependencies:
            dependency_unique_id = dependency.get("UniqueID")
            is_required = dependency.get("IsRequired", False)
            
            if dependency_unique_id:
                found_dependency = False
                for _mod in mods_enabled:
                    if _mod.unique_id.lower() == dependency_unique_id.lower():
                        found_dependency = True
                        break
                
                if is_required and not found_dependency:
                    missing_dependencies.append(dependency_unique_id)
        
        if missing_dependencies:
            print(f"Missing dependencies for mod '{mod.name}': {', '.join(missing_dependencies)}")
            return False
            
        return True

    
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
            if not "uuid" in modpack_data:
                modpack_data['uuid'] = ""
            if not "token" in modpack_data:
                modpack_data['token'] = ""
            if not "hash" in modpack_data:
                modpack_data['hash'] = ""
            if not "version" in modpack_data:
                modpack_data['version'] = "0.0.0"
            modpack = cls(name, modpack_data['image'], modpack_data['uuid'], modpack_data['token'], modpack_data['hash'], modpack_data['version'], base_directory=base_directory)
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