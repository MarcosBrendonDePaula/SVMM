from typing import List
import concurrent.futures, base64, os, json, shutil, uuid, secrets, re
import threading

from pathlib import Path
from src.mod import Mod
from src.config import Config
from src.infos import Infos
from src.tools import JasonAutoFix,HashMap,ModpackApi,Extractor
import logging

from tqdm import tqdm
import math

from PyQt6.QtCore import QObject, pyqtSignal

class Modpack(QObject):
    uploadSignal = pyqtSignal(dict)
    downloadSignal = pyqtSignal(dict)
    """Classe para representar e gerenciar modpacks do jogo."""
    
    def __init__(self, name, image="", _uuid="", token="", version="0.0.0", base_directory=""):
        """Inicializa uma instância da classe Modpack."""
        super().__init__()
        
        self.logger = logging.getLogger(f'Modpack-{name}')
        
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
        self.version = version
        
        self.folder_path = os.path.join(base_directory, 'modpacks', _uuid)

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
        conf = Config()
        server_host = f"{conf.get('SYNCAPI','protocol')}://{conf.get('SYNCAPI','host')}"
        self.api = ModpackApi(server_host)
        self.is_owner = self.api.is_owner(self._uuid,self.token)
        
    def to_dict(self):
        """Converte a modpack em um dicionário."""
        return {
            'name': self.name,
            'image': self.image,
            'token': self.token,
            'uuid' : self._uuid,
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

    def delete_mod(self, mod:Mod):
        shutil.rmtree(mod.mod_folder_path)
    
    def disable_mod(self, mod_name):
        """
        Desabilita um mod, movendo-o da pasta 'mods_enabled' para 'mods_disabled'.

        Args:
            mod_name (str): Nome do mod a ser desabilitado.
        """
        try:
            source_path = os.path.join(self.mods_enabled_path, mod_name)
            destination_path = os.path.join(self.mods_disabled_path, mod_name)
            if os.path.exists(source_path):
                os.rename(source_path, destination_path)
                self.save()
        except:
            return "FUDEO"

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
            self.logger.error(f'{e}')
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
                self.logger.info(f"The mod '{mod_name}' is already installed.")
        
        # Remover a pasta pai onde os mods estavam originalmente
        try:
            shutil.rmtree(temp_dir)
            self.logger.info(f"Directory '{temp_dir}' removed after installing mods.")
        except Exception as e:
            self.logger.error(f"Error while removing temporary folder '{temp_dir}': {e}")


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
    
    def mod_dependencies_complete(self, mod: Mod):
        """Verifica se as dependências do mod estão completas na lista de mods da modpack.

        Parameters
        ----------
            mod (Mod): O objeto Mod cujas dependências devem ser verificadas.

        Returns
        -------
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
            self.logger.error(f"Missing dependencies for mod '{mod.name}': {', '.join(missing_dependencies)}")
            return False
            
        return True

    def sync(self):
        """Mateus documentar**
        """
        info = self.api.get_modpack_info(self._uuid)
        # se a modpack não existir crie ela no servidor
        if info['status'] == 404:
            self.api.create_modpack_directory(self._uuid, self.token)
            with open(Path(self.folder_path) / "modpack.json", 'rb') as file:
                self.api.upload_file(self._uuid, self.token, "modpack.json", file)
            self.send_all_files()
        else:
            self.send_all_files()
    
    def send_all_files(self):
        """Mateus documentar**
        """
        
        self.uploadSignal.emit({
            "runing": 1,
            "progress": 0,
            "step" : 0,
            "done" : False
        })
        
        HashMap(self.folder_path)
        info = self.api.get_modpack_info(self._uuid)
        folder = Path(self.folder_path)
        
        def _upload_file(mod_file:Path):
            if mod_file.is_file():
                with open(mod_file, 'rb') as file:
                    relative_path = mod_file.relative_to(self.folder_path)
                    return self.api.upload_file(self._uuid, self.token, str(relative_path).replace('\\', '/'), file)
            return None
        
        def _delete_remote_file(mod_file:Path):
            relative_path = str(mod_file.relative_to(self.folder_path)).replace('\\', '/')
            self.api.remove_modpack_file(self._uuid, relative_path)

        hashmap_remoto = self.api.get_modpack_hash_map(self._uuid)['json']
        upload_files = set()  # Conjunto para armazenar os arquivos que precisam ser carregados
        delete_files = set()  # Conjunto para armazenar os arquivos que precisam ser deletados

        # Iterar pelos arquivos para determinar quais precisam ser carregados ou deletados
        mod_file:Path
        for mod_file in folder.glob('**/*'):
            if mod_file.is_file():
                local_hash = HashMap.hash_file(mod_file)
                remote_hash = hashmap_remoto.get(str(mod_file.relative_to(folder)).replace('\\', '/'))
                if remote_hash is None:
                    upload_files.add(mod_file)
                elif remote_hash != local_hash:
                    upload_files.add(mod_file)
        
        # Iterar pelo hashmap remoto para verificar arquivos que precisam ser removidos remotamente
        for key in hashmap_remoto:
            file_path = key.replace('/', os.path.sep)
            local_file_path = Path(self.folder_path) / file_path
            if local_file_path.exists() == False:
                delete_files.add(local_file_path)
        
        max_connections = 20
        total_files = len(upload_files)
        total_exclusions = len(delete_files)
        processed = 0
        all_tasks = total_files + total_exclusions
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_connections) as executor:
            # Criação de futures para as remoções
            delete_futures = [executor.submit(_delete_remote_file, mod_file) for mod_file in delete_files]

            self.uploadSignal.emit({
                "runing": 1,
                "progress": 0,
                "step" : 1,
                "done" : False
            })
            
            # Cria uma barra de progresso para as remoções
            with tqdm(total=total_exclusions, desc="Deleting files") as delete_pbar:
                for future in concurrent.futures.as_completed(delete_futures):
                    res = future.result()
                    if res is not None:
                        # Handle the result if needed
                        pass
                    delete_pbar.update(1)  # Atualiza a barra de progresso a cada arquivo concluído
                    processed += 1
                    progress_percent = (processed / all_tasks) * 100
                    self.uploadSignal.emit({
                        "runing": 1,
                        "progress": math.floor(progress_percent),
                        "step": 1,
                        "done": False
                    })

            # Criação de futures para os envios
            upload_futures = [executor.submit(_upload_file, mod_file) for mod_file in upload_files]
            
            self.uploadSignal.emit({
                "runing": 1,
                "progress": 0,
                "step" : 2,
                "done" : False
            })
            
            # Cria uma barra de progresso para os envios
            with tqdm(total=total_files, desc="Uploading files") as upload_pbar:
                for future in concurrent.futures.as_completed(upload_futures):
                    res = future.result()
                    if res is not None:
                        # Handle the result if needed
                        pass
                    processed += 1
                    upload_pbar.update(1)  # Atualiza a barra de progresso a cada arquivo concluído
                    
                    progress_percent = (processed / all_tasks) * 100
                    self.uploadSignal.emit({
                        "runing": 1,
                        "progress": math.floor(progress_percent),
                        "step": 2,
                        "done": False
                    })
        
        self.uploadSignal.emit({
            "runing": 0,
            "progress": 100,
            "step" : None,
            "done" : True
        })
        
    def update_modpack(self):
        res = self.api.get_modpack_hash_map(self._uuid)
        if res['status'] == 200:
            thread = threading.Thread(target=self.download_files, args=(res['json'],))
            thread.start()
    
    def download_files(self, hash_json: dict):
        self.uploadSignal.emit({
            "runing": 1,
            "progress": 0,
            "step" : 0,
            "done" : False
        })
        
        dictRemoto = hash_json
        dictLocal = HashMap(self.folder_path, True).hashmap
        
        def download_file(file_path):
            if file_path.lower().endswith("desktop.ini"):
                self.logger.info(f"Ignoring {file_path}...")
                return

            res = self.api.download_modpack_file(self._uuid, file_path)
            if res['status'] == 200:
                content = res['content']
                local_file_path = Path(self.folder_path) / file_path.replace("/", os.path.sep)
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                with local_file_path.open('wb') as local_file:
                    local_file.write(content)
       
        max_connections = 25
        try:
            conf = Config()
            max_connections = int(conf.get('SYNCAPI', 'max_connections'))
            if max_connections > Infos.limit_connections:
                max_connections = Infos.limit_connections
        except:
            max_connections = 25
        
        download_tasks = []
        local_hash_map = HashMap(self.folder_path).hashmap
        
        self.uploadSignal.emit({
            "runing": 1,
            "progress": 0,
            "step" : 1,
            "done" : False
        })
        
        for file_path in local_hash_map.keys():
            if file_path.lower() == "modpack.json":
                continue
            full_path = Path(self.folder_path) / file_path
            if file_path not in dictRemoto or dictRemoto.get(file_path) != HashMap.hash_file(Path(full_path)):
                Path(full_path).unlink()


        for root, dirs, files in os.walk(self.folder_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):  # Check if directory is empty
                    os.rmdir(dir_path)
        
        folder = Path(self.folder_path) / "mods_enabled"
        folder.mkdir(parents=True, exist_ok=True)
        
        folder = Path(self.folder_path) / "mods_disabled"
        folder.mkdir(parents=True, exist_ok=True)

        for file_path in hash_json.keys():
            if file_path.lower().endswith("desktop.ini"):
                continue
            local_file_path = Path(self.folder_path) / file_path.replace("/", os.path.sep)
            try:
                localHash = HashMap.hash_file(local_file_path)
            except:
                localHash = None

            # Verifique se o arquivo não existe localmente, ou se os hashes são diferentes
            if localHash is None or localHash != hash_json[file_path]:
                download_tasks.append(file_path)
            elif localHash is not None and hash_json.get(file_path) is None:
                # Se o arquivo existe localmente mas não remotamente, apague-o localmente
                local_file_path.unlink()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_connections) as executor:
            futures = [executor.submit(download_file, file_path) for file_path in download_tasks]
            
            completed_tasks = 0
            total_tasks = len(download_tasks)
            
            with tqdm(total=len(download_tasks), desc="Downloading files") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    future.result()

                    completed_tasks += 1
                    progress = completed_tasks / total_tasks * 100

                    self.uploadSignal.emit({
                        "runing": 1,
                        "progress": math.floor(progress),
                        "step": 2,
                        "done": False
                    })
                    pbar.update(1)
                    
        self.uploadSignal.emit({
            "runing": 0,
            "progress": 100,
            "step" : None,
            "done" : True
        })
    
    def reload(self):
        json_filename = os.path.join(self.folder_path, 'modpack.json')
        if os.path.exists(json_filename):
            modpack_data = JasonAutoFix.load(json_filename)
            if not "uuid" in modpack_data:
                modpack_data['uuid'] = ""
            if not "token" in modpack_data:
                modpack_data['token'] = ""
            if not "version" in modpack_data:
                modpack_data['version'] = "0.0.0"

            # Atualize os atributos da instância existente com os dados do JSON
            self.name = modpack_data['name']
            self.image = modpack_data['image']
            self._uuid = modpack_data['uuid']
            self.token = modpack_data['token']
            self.version = modpack_data['version']
            
        else:
            raise FileNotFoundError(f"JSON file not found: {json_filename}")
    
    @classmethod
    def load_from_json(cls, dir_name, base_directory=""):
        """
        Carrega uma modpack a partir de um arquivo JSON no diretório.

        Args:
            name (str): Nome da modpack.
            base_directory (str): Caminho para o diretório da modpack.

        Returns:
            Modpack: Instância da classe Modpack com os dados carregados.
        """
        json_filename = os.path.join(base_directory, 'modpacks', dir_name, 'modpack.json')
        if os.path.exists(json_filename):
            modpack_data = JasonAutoFix.load(json_filename)
            if not "uuid" in modpack_data:
                modpack_data['uuid'] = ""
            if not "token" in modpack_data:
                modpack_data['token'] = ""
            if not "version" in modpack_data:
                modpack_data['version'] = "0.0.0"
            modpack = cls(modpack_data['name'], modpack_data['image'], modpack_data['uuid'], modpack_data['token'], modpack_data['version'], base_directory=base_directory)
            return modpack
        return None  # Retorna None se o arquivo JSON não existir
    
    @staticmethod
    def get_all_modpacks(base_directory="")->List['Modpack']:
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
    def list_modpacks(base_directory="")->List[str]:
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