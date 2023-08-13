import configparser

class Config:

    def __init__(self):
        self.config = configparser.ConfigParser()

        # Valores padrão
        self.config['DEFAULT'] = {
            'LogLevel': 'INFO'
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
        """Carrega o arquivo de configuração."""
        self.config.read('settings.ini')
