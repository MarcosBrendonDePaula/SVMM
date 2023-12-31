import os
import json , re

from src.tools import (JasonAutoFix)
# Classe personalizada para decodificação JSON
class CustomJSONDecoder(json.JSONDecoder):
    """
    Uma classe personalizada que estende json.JSONDecoder para fornecer decodificação JSON com modificações específicas.
    """
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        """
        Decodifica uma string JSON com a remoção de vírgulas inválidas.
        
        Args:
            s (str): A string JSON para decodificar.
        
        Returns:
            dict: O objeto Python correspondente aos dados JSON decodificados.
        """
        s = self._remove_comments(s)
        s = self._remove_invalid_commas(s)
        return super().decode(s, _w)
    
    def _remove_comments(self, s):
        """
        Remove comentários do formato /* ... */ de uma string JSON.
        
        Args:
            s (str): A string JSON contendo comentários.
        
        Returns:
            str: A string JSON com comentários removidos.
        """
        return re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)
    
    def _remove_invalid_commas(self, s):
        # Remove espaços desnecessários após vírgulas
        s = re.sub(r',\s+', ',', s)
        # Coloca as vírgulas após chaves e colchetes na próxima linha
        s = re.sub(r',(?=\s*[\}\]])', ',\n', s)
        # Remove vírgulas extras dentro de objetos
        s = re.sub(r',(\s*\})', r'\1', s)
        # Remove vírgulas extras após o último elemento
        s = re.sub(r',(\s*[\}\]])', r'\1', s)
        return s

# Classe que representa um mod
class Mod:
    """
    Uma classe que representa um mod de jogo e lida com as informações relacionadas ao mod.
    """
    def __init__(self, mod_folder_path, base_mods_directory) -> None:
        """
        Inicializa um objeto Mod com informações padrão e carrega informações do arquivo "manifest.json".
        
        Args:
            mod_folder_path (str): O caminho para a pasta do mod.
            base_mods_directory (str): O diretório base onde os mods estão localizados.
        """
        self.mod_folder_path = mod_folder_path
        self.manifest_path = os.path.join(mod_folder_path, 'manifest.json')
        self.name = ""
        self.author = ""
        self.version = ""
        self.description = ""
        self.unique_id = ""
        self.entry_dll = ""
        self.minimum_api_version = ""
        self.update_keys = []
        self.dependencies = []

        self.base_mods_directory = base_mods_directory
        self.parent_folder_name = os.path.basename(mod_folder_path)
        # Carrega as informações do mod a partir do arquivo "manifest.json"
        self.load_manifest()
    
    def load_manifest(self):
        """
        Carrega informações do arquivo "manifest.json" e popula os atributos do objeto Mod.
        """
        if os.path.exists(self.manifest_path):
            manifest_data = JasonAutoFix.load(self.manifest_path)
            
            # Extrai informações do arquivo JSON carregado
            self.name = manifest_data.get("Name", "")
            self.author = manifest_data.get("Author", "")
            self.version = manifest_data.get("Version", "")
            self.description = manifest_data.get("Description", "")
            self.unique_id = manifest_data.get("UniqueID", "")
            self.entry_dll = manifest_data.get("EntryDll", "")
            self.minimum_api_version = manifest_data.get("MinimumApiVersion", "")
            self.update_keys = manifest_data.get("UpdateKeys", [])
            self.dependencies = manifest_data.get("Dependencies", [])
            
            # Cria instâncias da classe Mod para cada dependência
            for dependency in self.dependencies:
                if "UniqueId" in dependency:
                    dependency["UniqueID"] = dependency["UniqueId"]
                    del dependency["UniqueId"]

    def to_dict(self):
        """
        Converte as informações do objeto Mod em um dicionário.
        
        Returns:
            dict: Um dicionário contendo as informações do objeto Mod.
        """
        return {
            "name": self.name,
            "author": self.author,
            "version": self.version,
            "description": self.description,
            "unique_id": self.unique_id,
            "entry_dll": self.entry_dll,
            "minimum_api_version": self.minimum_api_version,
            "update_keys": self.update_keys,
            "dependencies": self.dependencies
        }