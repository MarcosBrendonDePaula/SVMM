import sys
import os
from PyQt6.QtWidgets import QApplication, QMenu ,QSystemTrayIcon, QWidget, QLabel, QGridLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QVBoxLayout, QDialog
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import base64

from src.config import Config
from src.game import Game
from src.modpack import Modpack
from views.modpack_config import ModpackConfigWindow

def base64_to_img(_base64) -> QPixmap:
    icon_pixmap = QPixmap()
    try:
        icon_pixmap.loadFromData(base64.b64decode(_base64))  # Carregar o pixmap a partir dos dados
    except:
        pass
    return icon_pixmap

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
        self.init_ui()

    def create_system_tray_icon(self, modpack):
        self.tray_icon = QSystemTrayIcon(self)
        # Carregue o ícone da modpack e defina-o como o ícone da bandeja do sistema
        modpack_icon = base64_to_img(modpack.image)
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
        modpacks = Modpack.get_all_modpacks()
        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        list_widget.clear()
        list_widget.itemSelectionChanged.connect(self.on_item_selected)
        
        self.info_layout = QGridLayout()  # Inicialize o layout de informações
        
        for modpack in modpacks:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, modpack)  # Associe o objeto Modpack ao item da lista
            item.setText(modpack.name)  # Define o texto do item como o nome do modpack
            
            icon_pixmap = base64_to_img(modpack.image)  # Converte a base64 em QPixmap
            icon_pixmap_resized = icon_pixmap.scaledToHeight(32)  # Redimensione para 128 pixels de altura (ajuste conforme necessário)
            item.setIcon(QIcon(icon_pixmap_resized))  # Define o ícone do item
            list_widget.addItem(item)  # Adiciona o item à lista

    def on_item_selected(self):
        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        selected_items = list_widget.selectedItems()  # Obtenha os itens selecionados
        
        if selected_items:
            selected_item = selected_items[0]  # Use o primeiro item selecionado, se houver
            modpack = selected_item.data(Qt.ItemDataRole.UserRole)  # Obtém o objeto Modpack associado ao item
            # Limpe e atualize o layout de informações
            while self.info_layout.count():
                item = self.info_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            
            # Limpe e atualize o layout de informações
            for i in reversed(range(self.info_layout.count())):
                self.info_layout.itemAt(i).widget().setParent(None)
            
            # Adicione imagem acima do nome da modpack
            icon_label = QLabel()
            icon_pixmap = base64_to_img(modpack.image)  # Converte a base64 em QPixmap
            icon_pixmap_resized = icon_pixmap.scaledToHeight(128)  # Redimensione para 128 pixels de altura (ajuste conforme necessário)
            icon_label.setPixmap(icon_pixmap_resized)
            self.info_layout.addWidget(icon_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Adicione nome da modpack
            name_label = QLabel(modpack.name)
            self.info_layout.addWidget(name_label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Set o ícone da janela com o ícone da modpack selecionada
            icon_pixmap = base64_to_img(modpack.image)
            self.setWindowIcon(QIcon(icon_pixmap))

            # Trocar o título da janela com o nome da modpack selecionada
            self.setWindowTitle(f"M: {modpack.name}")
            
            # Adicione os botões
            self.play_button = QPushButton('JOGAR')
            edit_button = QPushButton('EDITAR')
            remove_button = QPushButton('REMOVER')
            
            # Associe funções aos botões, se necessário
            self.play_button.clicked.connect(self.play_modpack)
            edit_button.clicked.connect(self.edit_modpack)
            remove_button.clicked.connect(self.remove_modpack)
            
            # Adicione os botões ao layout
            button_layout = QGridLayout()
            button_layout.addWidget(self.play_button, 0, 0)
            button_layout.addWidget(edit_button, 0, 1)
            button_layout.addWidget(remove_button, 0, 2)
            
            # Adicione o layout de botões ao layout de informações
            self.info_layout.addLayout(button_layout, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Configure o layout de informações na posição desejada
            self.layout().addLayout(self.info_layout, 0, 2, 5, 2)
            self.layout().update()
    
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
        print("Botão REMOVER pressionado")
    
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
    
    def confirm_create_modpack(self, modpack_name, dialog):
        if modpack_name:
            modpack = Modpack(modpack_name)
            modpack.save()
            # Atualizar a lista de modpacks
            self.ListAllModpacks()
            dialog.close()
    
    def init_ui(self):
        layout = QGridLayout()

        # Adicionar lista à esquerda
        list_widget = QListWidget(self)
        list_widget.setObjectName("list_widget")  # Defina o nome do objeto
        layout.addWidget(list_widget, 0, 0, 5, 2)  # (linha, coluna, rowspan, colspan)

        # Adicionar botão de criar modpack
        create_button = QPushButton('Criar Modpack')
        create_button.clicked.connect(self.create_modpack)
        layout.addWidget(create_button, 5, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
    
        self.setLayout(layout)
        self.ListAllModpacks()
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Teste de Layout')
        self.show()

