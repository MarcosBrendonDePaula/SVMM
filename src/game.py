import os
import shlex
from pathlib import Path
from src.config import Config
import logging

from src.tools import Steam
class Game:
    """Classe para gerenciar o jogo e executar comandos relacionados ao jogo usando as configurações definidas."""

    def __init__(self):
        """Inicializa a classe Game e carrega as configurações."""
        self.conf = Config()
        self.conf.load()
        self.running = False
        self.logger = logging.getLogger(f'Game')
    
    def is_running(self):
        return self.running
    
    def play(self):
        """Executa o jogo com as configurações definidas."""
        game_path = self.conf.get('GAME', 'path')
        mods_folder = self.conf.get('GAME', 'modsfolder')

        use_steam = self.conf.get('STEAM', 'use')
        if use_steam == "true":
            if not Steam.is_steam_running():
                Steam.start_steam_and_wait()
        self.logger.info(f"Game Path: {game_path}")

        if game_path and mods_folder:
            exe_path = Path(game_path) / "StardewModdingAPI.exe"
            command = f'"{exe_path}" --mods-path "{mods_folder}"'
            if os.name == 'posix':  # Linux
                command = shlex.quote(command)
            self.running = True
            os.system(f'"{command}"')
        else:
            self.logger.info("Game path or mods folder not set. Please configure them.")
            return -1
        return 0

    def set_mods_folder(self, path):
        """Define o diretório dos mods nas configurações e salva as alterações."""
        self.conf.set('GAME', 'modsfolder', path)
        self.conf.save()