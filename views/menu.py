import json
from pathlib import Path
import shutil
import sys
import os
from PyQt6.QtWidgets import QApplication, QMenu ,QSystemTrayIcon, QWidget, QLabel, QGridLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QVBoxLayout, QDialog
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import base64

from src.config import Config
from src.game import Game
from src.modpack import Modpack
from views.modpack_config import ModpackConfigWindow
from src.tools import (Converter)

class GameThread(QThread):
    finished = pyqtSignal()
    def __init__(self, game):
        super().__init__()
        self.game = game

    def run(self):
        self.game.play()
        self.finished.emit()

class MenuView(QWidget):
    
    def __init__(self):
        super().__init__()
        self.create_default_modpack()
        self.init_ui()
    
    def create_default_modpack(self):
        modpacks = Modpack.get_all_modpacks()
        if len(modpacks) == 0:
            Modpack("default")
              
    def create_system_tray_icon(self, modpack):
        self.tray_icon = QSystemTrayIcon(self)
        # Carregue o ícone da modpack e defina-o como o ícone da bandeja do sistema
        modpack_icon = Converter.base64_to_QPixmap(modpack.image)
        modpack_icon_resized = modpack_icon.scaledToHeight(16)  # Redimensione conforme necessário
        self.tray_icon.setIcon(QIcon(modpack_icon_resized))
        self.tray_icon.setToolTip('Seu aplicativo de modpacks')  # Substitua pela dica desejada
        self.tray_icon.activated.connect(self.toggle_window)

        # Crie um menu para a bandeja do sistema
        tray_menu = QMenu()
        open_action = tray_menu.addAction('Abrir')
        open_action.triggered.connect(self.show_window)
        exit_action = tray_menu.addAction('Sair')
        exit_action.triggered.connect(self.close_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def ListAllModpacks(self):
        modpacks = Modpack.get_all_modpacks(os.getcwd())
        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        list_widget.clear()
        list_widget.itemSelectionChanged.connect(self.on_item_selected)
        
        self.info_layout = QGridLayout()  # Inicialize o layout de informações
        
        for modpack in modpacks:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, modpack)  # Associe o objeto Modpack ao item da lista
            item.setText(modpack.name)  # Define o texto do item como o nome do modpack
            
            icon_pixmap = Converter.base64_to_QPixmap(modpack.image)  # Converte a base64 em QPixmap
            icon_pixmap_resized = icon_pixmap.scaledToHeight(32)  # Redimensione para 128 pixels de altura (ajuste conforme necessário)
            item.setIcon(QIcon(icon_pixmap_resized))  # Define o ícone do item
            list_widget.addItem(item)  # Adiciona o item à lista

    def on_item_selected(self):
        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        selected_items = list_widget.selectedItems()  # Obtenha os itens selecionados
        
        if selected_items:
            selected_item = selected_items[0]  # Use o primeiro item selecionado, se houver
            modpack:Modpack = selected_item.data(Qt.ItemDataRole.UserRole)  # Obtém o objeto Modpack associado ao item
            
            icon_pixmap = Converter.base64_to_QPixmap(modpack.image)  # Converte a base64 em QPixmap
            icon_pixmap_resized = icon_pixmap.scaledToHeight(128)  # Redimensione para 128 pixels de altura (ajuste conforme necessário)
            self.icon_label.setPixmap(icon_pixmap_resized)

            self.name_label.setText(modpack.name)
            self.setWindowIcon(QIcon(icon_pixmap))
            
            # Trocar o título da janela com o nome da modpack selecionada
            self.setWindowTitle(f"M: {modpack.name}")
            self.info_layout.update()
    
    def play_modpack(self):
        list_widget = self.findChild(QListWidget, "list_widget")
        selected_items = list_widget.selectedItems()

        if selected_items:
            selected_item = selected_items[0]
            modpack = selected_item.data(Qt.ItemDataRole.UserRole)
            game = Game()
            game.set_mods_folder(os.path.join(os.getcwd(), modpack.mods_folder()))
            self.create_system_tray_icon(modpack)

            self.play_button.setEnabled(False)  # Desabilitar o botão "JOGAR"
            self.play_button.setText('RODANDO')  # Alterar o texto do botão

            # Inicie o jogo em uma thread separada
            self.game_thread = GameThread(game)
            self.game_thread.finished.connect(self.on_game_finished)
            self.game_thread.start()
            self.toggle_window(QSystemTrayIcon.ActivationReason.MiddleClick)

    def on_game_finished(self):
        self.tray_icon.hide()
        self.show()

        self.play_button.setEnabled(True)  # Habilitar o botão "JOGAR" novamente
        self.play_button.setText('JOGAR')  # Restaurar o texto do botão
        
    def edit_modpack(self):
        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        selected_items = list_widget.selectedItems()  # Obtenha os itens selecionados
        
        if selected_items:
            selected_item = selected_items[0]  # Use o primeiro item selecionado, se houver
            modpack = selected_item.data(Qt.ItemDataRole.UserRole)  # Obtém o objeto Modpack associado ao item
            
            # Abra a janela de configuração passando o objeto Modpack
            config_window = ModpackConfigWindow(modpack)
            config_window.exec()

    def toggle_window(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def show_window(self):
        self.show()

    def close_app(self):
        self.tray_icon.hide()
        self.close()
    
    def remove_modpack(self):
        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        selected_items = list_widget.selectedItems()  # Obtenha os itens selecionados
        
        if selected_items:
            selected_item = selected_items[0]  # Use o primeiro item selecionado, se houver
            modpack:Modpack = selected_item.data(Qt.ItemDataRole.UserRole)  # Obtém o objeto Modpack associado ao item
            try:
                shutil.rmtree(modpack.folder_path)
                print(f"Folder '{modpack.folder_path}' and its contents have been removed recursively.")
            except Exception as e:
                print(f"An error occurred while removing the folder: {e}")
                
            self.ListAllModpacks()
            if list_widget.count() > 0:  # Verifica se a lista não está vazia
                list_widget.setCurrentRow(0)  # Seleciona o primeiro item da lista
    
    def create_modpack(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Criar Modpack')
        
        layout = QVBoxLayout()
        
        label = QLabel('Digite o nome da Modpack:')
        layout.addWidget(label)
        
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        confirm_button = QPushButton('Criar')
        confirm_button.clicked.connect(lambda: self.confirm_create_modpack(name_input.text(), dialog))
        layout.addWidget(confirm_button)

        dialog.setLayout(layout)
        dialog.exec()
        
    def create_remote_modpack(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('External Pack')
        
        layout = QVBoxLayout()
        
        label = QLabel('modpack uuid')
        layout.addWidget(label)
        
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        confirm_button = QPushButton('Criar')
        confirm_button.clicked.connect(lambda: self.confirm_create_remote_modpack(name_input.text(), dialog))
        layout.addWidget(confirm_button)

        dialog.setLayout(layout)
        dialog.exec()
    
    def confirm_create_modpack(self, modpack_name, dialog):
        if modpack_name:
            modpack = Modpack(modpack_name)
            modpack.save()
            # Atualizar a lista de modpacks
            self.ListAllModpacks()
            dialog.close()
            
    def confirm_create_remote_modpack(self, uuid, dialog):
        if uuid:
            from src.tools import ModpackApi
            conf = Config()
            server_host = f"{conf.get('SYNCAPI','protocol')}://{conf.get('SYNCAPI','host')}"
            api = ModpackApi(server_host)
            resp = api.get_modpack_info(uuid)
            print(resp)
            if resp['status'] == 200:
                modpack = Modpack(resp['json']['name'], _uuid=resp['json']['uuid'])
                # Create the path for modpack.json in the modpack folder
                modpack_json_path = Path(modpack.folder_path) / "modpack.json"
                # Write the JSON content to modpack.json
                with modpack_json_path.open('w') as json_file:
                    json.dump(resp['json'], json_file, indent=4)
                    dialog.close()
                self.ListAllModpacks()
                    
    def init_ui(self):
        layout = QGridLayout()
        self.info_layout = QGridLayout()
        
        font = QFont("Roboto", weight=QFont.Weight.Bold)
        font.setPointSize(25)  # Defina o tamanho da fonte
        
        # Adicione imagem acima do nome da modpack
        self.icon_label = QLabel()
        self.icon_pixmap = QPixmap()  # Você deve definir a imagem corretamente aqui
        icon_pixmap_resized = self.icon_pixmap.scaledToHeight(128)  # Redimensione para 128 pixels de altura (ajuste conforme necessário)
        self.icon_label.setPixmap(icon_pixmap_resized)
        self.info_layout.addWidget(self.icon_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Adicione nome da modpack
        self.name_label = QLabel()  # Defina o nome da modpack corretamente aqui
        font = QFont("Roboto", weight=QFont.Weight.Bold)
        font.setPointSize(25)  # Defina o tamanho da fonte
        self.name_label.setFont(font)
        self.info_layout.addWidget(self.name_label, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Adicionar lista à esquerda
        list_widget = QListWidget(self)
        list_widget.setObjectName("list_widget")  # Defina o nome do objeto
        layout.addWidget(list_widget, 0, 0, 5, 2)  # (linha, coluna, rowspan, colspan)

        # Adicionar botão de criar modpack
        create_button = QPushButton('Criar Modpack')
        create_button.clicked.connect(self.create_modpack)
        layout.addWidget(create_button, 5, 0, 1, 2)
        
        # Adicionar botão de criar modpack
        connect_button = QPushButton('Conectar Modpack')
        connect_button.clicked.connect(self.create_remote_modpack)
        layout.addWidget(connect_button, 5, 2, 1, 2)
        
        # Adicione os botões
        self.play_button = QPushButton('JOGAR')
        self.edit_button = QPushButton('EDITAR')
        self.remove_button = QPushButton('REMOVER')
        
        # Associe funções aos botões, se necessário
        self.play_button.clicked.connect(self.play_modpack)
        self.edit_button.clicked.connect(self.edit_modpack)
        self.remove_button.clicked.connect(self.remove_modpack)
        
        # Adicione os botões ao layout
        button_layout = QGridLayout()
        button_layout.addWidget(self.play_button, 0, 0)
        button_layout.addWidget(self.edit_button, 0, 1)
        button_layout.addWidget(self.remove_button, 0, 2)
            
        # Adicione o layout de botões ao layout de informações
        self.info_layout.addLayout(button_layout, 4, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            
        # Configure o layout de informações na posição desejada
        layout.addLayout(self.info_layout, 0, 2, 5, 2)
    
        self.setLayout(layout)
        self.ListAllModpacks()
        
        if list_widget.count() > 0:  # Verifica se a lista não está vazia
            list_widget.setCurrentRow(0)  # Seleciona o primeiro item da lista
        
        self.setGeometry(100, 100, 400, 250)
        self.setWindowTitle('Teste de Layout')
        self.show()

