import os
import hashlib
import json
import time
from tqdm import tqdm

def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

class HashMap:
    """
    Classe para criar e comparar mapas de hashes de arquivos e diretórios.
    """

    def __init__(self, directory, load_existing=False, show_progress=True):
        """
        Inicializa um novo objeto HashMap para um diretório específico.

        :param directory: O caminho absoluto para o diretório a ser monitorado.
        :param load_existing: Define se deve carregar um hashmap existente de um arquivo JSON.
        :param show_progress: Define se deve exibir o progressbar durante a criação do hashmap.
        """
        self.directory = directory
        self.hashmap = {}
        self.parent_changes = set()  # Conjunto para armazenar as pastas pai que tiveram mudanças
        self.elapsed_time = None
        self.show_progress = show_progress
        self.hashmap_file_path = os.path.join(directory, "hashmap.json")  # Caminho para o arquivo de hashmap

        if load_existing:
            self.load_from_file(self.hashmap_file_path)
        else:
            self.hashmap = self.create_hashmap()
            self.save_to_file(self.hashmap_file_path)

    def hash_file(self, file_path):
        """
        Calcula o hash MD5 de um arquivo.

        :param file_path: Caminho absoluto para o arquivo.
        :return: O valor de hash MD5 em formato hexadecimal.
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def hash_files(self, files):
        """
        Calcula o hash MD5 de uma lista de arquivos.

        :param files: Lista de caminhos absolutos para os arquivos.
        :return: O valor de hash MD5 em formato hexadecimal.
        """
        hash_md5 = hashlib.md5()
        for file_path in files:
            if os.path.isfile(file_path):  # Verifica se o caminho é um arquivo
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def hash_directory(self, dir_path, dir_hash):
        """
        Calcula um hash que incorpora o hash do diretório e seus arquivos.

        :param dir_path: Caminho absoluto para o diretório.
        :param dir_hash: Hash do diretório (sem considerar os arquivos nele).
        :return: O valor de hash MD5 em formato hexadecimal.
        """
        files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
        files.sort()  # Ordenar os arquivos para garantir consistência
        files_hash = self.hash_files(files)
        combined_hash = dir_hash + files_hash
        return hashlib.md5(combined_hash.encode()).hexdigest()

    def create_hashmap(self):
        start_time = time.time()

        total_files = count_files(self.directory)
        progress_bar = tqdm(total=total_files, disable=not self.show_progress)

        hashmap = {}
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = self.hash_file(file_path)
                relative_path = os.path.relpath(file_path, self.directory).replace("\\", "/")
                hashmap[relative_path] = file_hash
                progress_bar.update(1)

        progress_bar.close()

        end_time = time.time()
        self.elapsed_time = end_time - start_time
        print(f"Tempo decorrido: {self.elapsed_time:.2f} segundos")
        return hashmap

    def compare(self, other_hashmap):
        """
        Compara dois mapas de hashes e retorna as diferenças encontradas.

        :param other_hashmap: Outra instância da classe HashMap a ser comparada.
        :return: Um dicionário contendo as diferenças encontradas nos hashes.
        """
        differences = {}

        # Primeiro, verifica as pastas pai que tiveram mudanças
        for parent_folder in self.parent_changes:
            if parent_folder not in other_hashmap.parent_changes:
                continue

            if self.hashmap[parent_folder] != other_hashmap.hashmap[parent_folder]:
                differences[parent_folder] = (
                    self.hashmap[parent_folder], other_hashmap.hashmap[parent_folder]
                )

            # Agora, verifique os filhos dessa pasta
            for key in self.hashmap.keys():
                if key.startswith(parent_folder + os.path.sep):
                    if key in other_hashmap.hashmap:
                        if self.hashmap[key] != other_hashmap.hashmap[key]:
                            differences[key] = (
                                self.hashmap[key], other_hashmap.hashmap[key]
                            )
        
        return differences

    def save_to_file(self, file_path):
        """
        Salva o hashmap em um arquivo JSON.

        :param file_path: O caminho absoluto para o arquivo JSON a ser criado.
        """
        with open(file_path, "w") as f:
            json.dump(self.hashmap, f, indent=4)

    def load_from_file(self, file_path):
        """
        Carrega um hashmap existente de um arquivo JSON.

        :param file_path: O caminho absoluto para o arquivo JSON contendo o hashmap existente.
        """
        try:
            with open(file_path, "r") as f:
                self.hashmap = json.load(f)
        except FileNotFoundError:
            print(f"Arquivo {file_path} não encontrado. Criando novo hashmap.")
            self.hashmap = self.create_hashmap()
    
    def load_from_json(self, json:json):
        """
        Carrega um hashmap existente de uma variavel JSON.
        """
        self.hashmap = json