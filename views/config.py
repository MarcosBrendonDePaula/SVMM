import sys
import subprocess
from PyQt6.QtWidgets import QMessageBox, QDialog,QSizePolicy, QLabel, QLineEdit, QComboBox, QGridLayout, QPushButton, QFileDialog
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon,QIntValidator

from pathlib import Path
from typing import List
import i18n, logging
from src.config import Config as SysConfig
from src.tools import Resources
from src.infos import Infos
from views.contributors import ContributorsDialog

class Config(QDialog):
    ICON_SCALE = 0.5
    def define_button_icon(self, button:QPushButton, resource_img_name, size=(45, 45), usePolice = True):
        icon = QIcon(f"{Resources.get_image_path(resource_img_name)}")
        icon_pixmap = icon.pixmap(size[0], size[1])
        button.setIcon(icon)
        button.setIconSize(icon_pixmap.size())
        if usePolice:
            self.define_button_icon_pollice(button, size)
    
    def define_button_icon_pollice(self, button:QPushButton, size=(45, 45)):
        size_policy = button.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        button.setSizePolicy(size_policy)
        button.setFixedSize(size[0], size[1])
          
    def __init__(self):
        super().__init__()
        self.config = SysConfig()
        self.init_ui()
        self.load_info()
        
    def init_ui(self):
        self.setWindowIcon(QIcon(Resources.get_image('Settings.png')))
        self.layout_basico = QGridLayout()

        # Rótulo e campo de seleção para Game Path
        self.label_game_path = QLabel(i18n.t(f'Config.label.game_path'))
        self.game_path_input = QLineEdit()
        self.layout_basico.addWidget(self.label_game_path, 0, 0)
        self.layout_basico.addWidget(self.game_path_input, 0, 1)
        
        # Botão para procurar o arquivo StardewModdingAPI.exe
        self.browse_button = QPushButton(i18n.t(f'Config.btn.find'))
        self.layout_basico.addWidget(self.browse_button, 0, 2)
        self.define_button_icon(self.browse_button, 'Opened Folder_1', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        
        # Rótulo e campo de seleção para a linguagem
        self.label_language = QLabel(i18n.t(f'Config.label.language'))
        self.language_select = QComboBox()
        languages = self.list_langs()
        self.language_select.addItems(languages)
        self.layout_basico.addWidget(self.label_language, 2, 0)
        self.layout_basico.addWidget(self.language_select, 2, 1, 1, 2)

        # Rótulo e campo de seleção para LogLevel
        self.label_log_level = QLabel(i18n.t(f'Config.label.log_level'))
        self.log_level_select = QComboBox()
        self.log_level_select.addItems(['INFO', 'DEBUG', 'WARNING', 'ERROR'])
        self.layout_basico.addWidget(self.label_log_level, 3, 0)
        self.layout_basico.addWidget(self.log_level_select, 3, 1, 1, 2)

        # Rótulo e campo de entrada para SYNCAPI
        self.label_sync_api = QLabel(i18n.t(f'Config.label.sync_api'))
        self.sync_api_input = QLineEdit()
        self.layout_basico.addWidget(self.label_sync_api, 4, 0)
        self.layout_basico.addWidget(self.sync_api_input, 4, 1, 1, 2)

        self.max_con_label = QLabel(i18n.t(f'Config.label.sync_api.max_con'))
        self.sync_api_max_con = QLineEdit()
        self.sync_api_max_con.setValidator(QIntValidator())
        self.sync_api_max_con.textEdited.connect(self.max_connections_validate)
        self.layout_basico.addWidget(self.max_con_label, 5, 0)
        self.layout_basico.addWidget(self.sync_api_max_con, 5, 1, 1, 2)

        # Botões de ação
        self.save_button = QPushButton(i18n.t(f'Config.btn.salve_restart'))
        self.cancel_button = QPushButton(i18n.t(f'Config.btn.cancel'))
        
        self.define_button_icon(self.save_button, 'Save.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        self.define_button_icon(self.cancel_button, 'Close Window.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        
        self.layout_basico.addWidget(self.save_button, 6, 0)
        self.layout_basico.addWidget(self.cancel_button, 6, 1)
        
        self.contributors = QPushButton(i18n.t(f'Config.btn.contributors'))
        self.define_button_icon(self.contributors, 'People.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        self.layout_basico.addWidget(self.contributors, 6, 2)
        
        self.setLayout(self.layout_basico)
        self.setGeometry(100, 100, 400, 250)
        self.setWindowTitle(i18n.t(f'Config.window.title'))
        
        # Conecte os botões aos métodos correspondentes
        self.save_button.clicked.connect(self.save_and_restart)
        self.cancel_button.clicked.connect(self.close)
        self.browse_button.clicked.connect(self.browse_game_directory)
        self.contributors.clicked.connect(self.show_contributors)
    
    def max_connections_validate(self, text):
        try:
            int_value = int(text)
            if int_value > Infos.limit_connections:
                self.sync_api_max_con.setText(f"{Infos.limit_connections}")
            elif int_value < 1:
                self.sync_api_max_con.setText("1")
            self.save_button.setDisabled(False)
        except ValueError:
            self.save_button.setDisabled(True)
    
    def show_contributors(self):
        ContributorsDialog().exec()
        pass
    
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
        self.sync_api_max_con.setText(self.config.get('SYNCAPI', 'max_connections'))
        self.language_select.setCurrentText(self.config.get('SVMG', 'lang'))
        

    # Função para salvar informações nas configurações e reiniciar a aplicação
    def save_and_restart(self):
        self.config.set('GAME', 'gamepath', self.game_path_input.text())
        # self.config.set('GAME', 'modsfolder', self.mods_path_input.text())
        self.config.set('CONSOLE', 'loglevel', self.log_level_select.currentText())
        self.config.set('SYNCAPI', 'host', self.sync_api_input.text())
        self.config.set('SYNCAPI', 'max_connections', self.sync_api_max_con.text())
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
