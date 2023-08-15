import json
import os

class Modpack:
    """Classe para representar e gerenciar modpacks do jogo."""

    def __init__(self, name, base_directory=""):
        """Inicializa uma instância da classe Modpack."""
        self.name = name
        self.folder_path = ""

        folder_path = os.path.join(base_directory, 'modpacks', name)
        self.folder_path = folder_path

        self.mods_enabled_path = os.path.join(self.folder_path, 'mods_enabled')
        self.mods_disabled_path = os.path.join(self.folder_path, 'mods_disabled')
        self.saves_path = os.path.join(self.folder_path, 'saves')

        os.makedirs(self.mods_enabled_path, exist_ok=True)
        os.makedirs(self.mods_disabled_path, exist_ok=True)
        os.makedirs(self.saves_path, exist_ok=True)



    def to_dict(self):
        """Converte a modpack em um dicionário."""
        return {
            'name': self.name
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
    def load_from_json(cls, name, base_directory):
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

            modpack = cls(name, base_directory=base_directory)
            modpack.mods = modpack_data['mods']
            return modpack

        return None  # Retorna None se o arquivo JSON não existir
