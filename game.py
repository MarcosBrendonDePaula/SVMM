import os
import shlex

from config import Config


class Game:
    """Classe para gerenciar o jogo e executar comandos relacionados ao jogo usando as configurações definidas."""

    def __init__(self):
        """Inicializa a classe Game e carrega as configurações."""
        self.conf = Config()
        self.conf.load()

    def play(self):
        """Executa o jogo com as configurações definidas."""
        game_path = self.conf.get('GAME', 'gamepath')
        mods_folder = self.conf.get('GAME', 'modsfolder')

        print(game_path)

        if game_path and mods_folder:
            exe_path = f'"{game_path}/StardewModdingAPI.exe"'
            command = f'"{exe_path}" --mods-path {mods_folder}'
            if os.name == 'posix':  # Linux
                command = shlex.quote(command)
            print(command)
            os.system(command)
        else:
            print("Game path or mods folder not set. Please configure them.")

    def set_mods_folder(self, path):
        """Define o diretório dos mods nas configurações e salva as alterações."""
        self.conf.set('GAME', 'modsfolder', path)
        self.conf.save()
