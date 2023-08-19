import configparser
import os
import platform
import psutil

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
            self.set_default_console()
            self.set_default_game()
            self.save()  # Cria o arquivo com as configurações padrão

    def set_default_console(self):
        self.set('CONSOLE', 'loglevel', 'INFO')

    def set_default_game(self):
        print(self.find_stardew_valley_installation_path())
        self.set('GAME', 'gamepath', self.find_stardew_valley_installation_path())
        self.set('GAME', 'modsfolder', 'Mods')

    def find_steam_installation_path(self):
        if platform.system() == 'Windows':
            steam_registry_path = r'SOFTWARE\WOW6432Node\Valve\Steam'
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, steam_registry_path) as key:
                    return winreg.QueryValueEx(key, 'InstallPath')[0]
            except Exception as e:
                print(f"Erro ao acessar o registro do Windows: {e}")
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
