import sys
import subprocess
from PyQt6.QtWidgets import QMessageBox,QDialog, QLabel, QLineEdit, QComboBox, QGridLayout, QPushButton, QFileDialog
from PyQt6.QtCore import QCoreApplication
from pathlib import Path
from typing import List
import i18n
from src.config import Config as SysConfig

class Config(QDialog):
    def __init__(self):
        super().__init__()
        self.config = SysConfig()
        self.init_ui()
        self.load_info()
        
    def init_ui(self):
        self.layout_basico = QGridLayout()

        # Rótulo e campo de seleção para Game Path
        self.label_game_path = QLabel(i18n.t(f'Config.label.game_path'))
        self.game_path_input = QLineEdit()
        self.layout_basico.addWidget(self.label_game_path, 0, 0)
        self.layout_basico.addWidget(self.game_path_input, 0, 1)
        
        # Botão para procurar o arquivo StardewModdingAPI.exe
        self.browse_button = QPushButton(i18n.t(f'Config.btn.find'))
        self.layout_basico.addWidget(self.browse_button, 0, 2)

        # Rótulo e campo de seleção para a linguagem
        self.label_language = QLabel(i18n.t(f'Config.label.language'))
        self.language_select = QComboBox()
        languages = self.list_langs()
        self.language_select.addItems(languages)
        self.layout_basico.addWidget(self.label_language, 2, 0)
        self.layout_basico.addWidget(self.language_select, 2, 1)

        # Rótulo e campo de seleção para LogLevel
        self.label_log_level = QLabel(i18n.t(f'Config.label.log_level'))
        self.log_level_select = QComboBox()
        self.log_level_select.addItems(['INFO', 'DEBUG', 'WARNING', 'ERROR'])
        self.layout_basico.addWidget(self.label_log_level, 3, 0)
        self.layout_basico.addWidget(self.log_level_select, 3, 1)

        # Rótulo e campo de entrada para SYNCAPI
        self.label_sync_api = QLabel(i18n.t(f'Config.label.sync_api'))
        self.sync_api_input = QLineEdit()
        self.layout_basico.addWidget(self.label_sync_api, 4, 0)
        self.layout_basico.addWidget(self.sync_api_input, 4, 1)

        # Botões de ação
        self.save_button = QPushButton(i18n.t(f'Config.btn.salve_restart'))
        self.cancel_button = QPushButton(i18n.t(f'Config.btn.cancel'))
        self.layout_basico.addWidget(self.save_button, 5, 0)
        self.layout_basico.addWidget(self.cancel_button, 5, 1)

        self.setLayout(self.layout_basico)
        self.setGeometry(100, 100, 400, 250)
        self.setWindowTitle(i18n.t(f'Config.window.title'))

        # Conecte os botões aos métodos correspondentes
        self.save_button.clicked.connect(self.save_and_restart)
        self.cancel_button.clicked.connect(self.close)
        self.browse_button.clicked.connect(self.browse_game_directory)
    
    def list_langs(self) -> List[str]:
        langs = []
        path = Path('resources') / "i18n"
        # Verifica se o diretório existe
        if path.exists() and path.is_dir():
            # Lista os arquivos JSON no diretório
            for arquivo in path.glob('*.json'):
                langs.append(arquivo.name.replace('.json', ''))
        return langs

    # Função para carregar informações nas configurações
    def load_info(self):
        self.game_path_input.setText(self.config.get('GAME', 'gamepath'))
        # self.mods_path_input.setText(self.config.get('GAME', 'modsfolder'))
        self.log_level_select.setCurrentText(self.config.get('CONSOLE', 'loglevel'))
        self.sync_api_input.setText(self.config.get('SYNCAPI', 'host'))
        self.language_select.setCurrentText(self.config.get('SVMG', 'lang'))

    # Função para salvar informações nas configurações e reiniciar a aplicação
    def save_and_restart(self):
        self.config.set('GAME', 'gamepath', self.game_path_input.text())
        # self.config.set('GAME', 'modsfolder', self.mods_path_input.text())
        self.config.set('CONSOLE', 'loglevel', self.log_level_select.currentText())
        self.config.set('SYNCAPI', 'host', self.sync_api_input.text())
        self.config.set('SVMG', 'lang', self.language_select.currentText())
        self.config.save()  # Salva as configurações

        # Reiniciar a aplicação
        python = sys.executable
        subprocess.Popen([python, sys.argv[0]])
        QCoreApplication.quit()  # Fecha a aplicação

    # Função para abrir um diálogo de seleção de diretório para o Game Path
    def browse_game_directory(self):
        selected_directory = QFileDialog.getExistingDirectory(self, 'Procurar diretório do jogo')
        if selected_directory:
            self.game_path_input.setText(selected_directory)
