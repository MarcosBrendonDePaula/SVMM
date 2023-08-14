import configparser
import os

class Config:
    """Classe para gerenciar configurações do jogo usando um padrão Singleton."""
    _instance = None

    def __new__(cls):
        """Cria uma instância única da classe Config, garantindo que as configurações sejam carregadas apenas uma vez."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.config = configparser.ConfigParser()
            cls._instance.load()
        return cls._instance

    def __init__(self):
        """Inicializa a classe Config com as configurações padrão."""
        self.config = configparser.ConfigParser()

        self.config['CONSOLE'] = {
            'loglevel': 'INFO',
        }

        # Valores padrão
        self.config['GAME'] = {
            'gamepath': '',
            'modsfolder': 'Mods'
        }

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
        if os.path.exists('settings.ini'):
            self.config.read('settings.ini')
        else:
            self.save()  # Cria o arquivo com as configurações padrão
