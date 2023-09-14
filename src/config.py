import configparser
import os
from pathlib import Path
import platform
import psutil
import i18n
import logging
from src.tools import Steam
class Config:
    """Classe para gerenciar configurações do jogo usando um padrão Singleton."""

    _instance = None

    def __new__(cls):
        """Cria uma instância única da classe Config, garantindo que as configurações sejam carregadas apenas uma vez."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load()
        return cls._instance

    def __init__(self):
        """Inicializa a classe Config com as configurações padrão."""
        self.logger = logging.getLogger(f'Config')
        pass

    def set(self, section, key, value):
        """Define um valor para uma chave específica em uma seção."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def get(self, section, key):
        """Obtém o valor de uma chave em uma seção. Retorna None se não encontrado."""
        return self.config.get(section, key, fallback=None)

    def save(self):
        """Grava o arquivo de configuração."""
        with open('settings.ini', 'w') as configfile:
           self.config.write(configfile)

    def load(self):
        """Carrega o arquivo de configuração ou cria se não existir."""
        self.config = configparser.ConfigParser()

        if os.path.exists('settings.ini'):
            self.config.read('settings.ini')
        else:
            self.save()  # Cria o arquivo com as configurações padrão
        
        self.set_default_console()
        self.set_default_game()
        self.set_default_svmg()
        self.set_default_steam()
        
        self.configure_logger(self.get('CONSOLE', 'loglevel'))
        
        lang = self.get('SVMG', 'lang')
        i18n.config.set('locale', lang)
        i18n.set('filename_format', '{format}')
        i18n.resource_loader.load_translation_file(f"{lang}.json",(Path('resources') / "i18n"), lang)
    
    def set_default_svmg(self):
        self.ensure_config_field('SVMG', 'lang', 'en')

    def set_default_console(self):
        self.ensure_config_field('CONSOLE', 'loglevel', 'INFO')

    def set_default_game(self):
        self.ensure_config_field('GAME', 'path', self.find_stardew_valley_installation_path())
        self.ensure_config_field('GAME', 'modsfolder', 'Mods')
        self.ensure_config_field('SYNCAPI', 'host', 'svmgapi.marcosbrendon.com:3000')
        self.ensure_config_field('SYNCAPI', 'protocol', 'http')
        self.ensure_config_field('SYNCAPI', 'max_connections', '20')
    
    def set_default_steam(self):
        STEAM_PATH = Steam.get_installation_path()
        if STEAM_PATH:
            self.ensure_config_field('STEAM', 'use', "true")
        else:
            self.ensure_config_field('STEAM', 'use', "false")
        self.ensure_config_field('STEAM', 'path', Steam.get_installation_path() or "")

    def ensure_config_field(self, section, key, default_value):
        """
        Verifica se uma seção e chave específica existem no arquivo de configuração.
        Se não existirem, cria-os com o valor padrão especificado.
        """
        if section not in self.config:
            self.config[section] = {}
        if key not in self.config[section]:
            self.set(section, key, default_value)
            self.save()
    
    def find_steam_installation_path(self):
        if platform.system() == 'Windows':
            steam_registry_path = r'SOFTWARE\WOW6432Node\Valve\Steam'
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, steam_registry_path) as key:
                    return winreg.QueryValueEx(key, 'InstallPath')[0]
            except Exception as e:
                self.logger.error(f"Error accessing the Windows registry: {e}")
        elif platform.system() == 'Linux':
            home_folder = os.path.expanduser("~")
            steam_path = os.path.join(home_folder, '.steam', 'steam')
            if os.path.exists(steam_path):
                return steam_path
        return ''
    
    def find_stardew_valley_installation_path(self):
        steam_path = self.find_steam_installation_path()
        
        if steam_path:
            app_id = 413150  # App ID do Stardew Valley na Steam
            app_manifest_path = os.path.join(steam_path, 'steamapps', f'appmanifest_{app_id}.acf')

            if os.path.exists(app_manifest_path):
                with open(app_manifest_path, 'r', encoding='utf-8') as manifest_file:
                    manifest_data = manifest_file.read()
                    install_folder_line = [line for line in manifest_data.split('\n') if 'installdir' in line]
                    if install_folder_line:
                        install_folder = install_folder_line[0].split('"')[3]
                        return os.path.join(steam_path, 'steamapps', 'common', install_folder)
        
        # Se o ACF não existir ou não conter as informações, verifique a pasta diretamente
        possible_paths = [
            os.path.join(steam_path, 'steamapps', 'common', 'Stardew Valley'),
            os.path.join('steamapps', 'common', 'Stardew Valley'),
            os.path.join('SteamLibrary', 'steamapps', 'common', 'Stardew Valley'),
            # Outros possíveis caminhos aqui, dependendo da plataforma e da loja
        ]

        # Adicione a busca em outros discos aqui
        available_drives = [drive.device for drive in psutil.disk_partitions()]
        for drive in available_drives:
            for path in possible_paths:
                full_path = os.path.join(drive, path)
                if os.path.exists(full_path):
                    return full_path
        return ''

    def configure_logger(self, loglevel):
        # Mapeamento dos níveis de log
        loglevel_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }

        # Verifique se o nível de log fornecido é válido, caso contrário, use 'INFO' como padrão
        level = loglevel_map.get(loglevel, logging.INFO)

        # Configuração do logger
        logging.basicConfig(
            level=level,  # Defina o nível de log com base no mapeamento
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs.log'  # Especifique o nome do arquivo de log (opcional)
        )
        logging.captureWarnings(True)