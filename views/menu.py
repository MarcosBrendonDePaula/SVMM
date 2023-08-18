import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QListWidget, QListWidgetItem, QPushButton
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import base64

from config import Config
from game import Game
from modpack import Modpack

def base64_to_img(_base64) -> QPixmap:
    icon_pixmap = QPixmap()
    icon_pixmap.loadFromData(base64.b64decode(_base64))  # Carregar o pixmap a partir dos dados
    return icon_pixmap


class MenuView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def ListAllModpacks(self):
        modpacks = Modpack.get_all_modpacks()

        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        list_widget.itemSelectionChanged.connect(self.on_item_selected)
        
        self.info_layout = QGridLayout()  # Inicialize o layout de informações
        
        for modpack in modpacks:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, modpack)  # Associe o objeto Modpack ao item da lista
            item.setText(modpack.name)  # Define o texto do item como o nome do modpack
            
            icon_pixmap = base64_to_img(modpack.image)  # Converte a base64 em QPixmap
            icon_pixmap_resized = icon_pixmap.scaledToHeight(128)  # Redimensione para 128 pixels de altura (ajuste conforme necessário)
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
            
            # Adicione os botões
            play_button = QPushButton('JOGAR')
            edit_button = QPushButton('EDITAR')
            remove_button = QPushButton('REMOVER')
            
            # Associe funções aos botões, se necessário
            play_button.clicked.connect(self.play_modpack)
            edit_button.clicked.connect(self.edit_modpack)
            remove_button.clicked.connect(self.remove_modpack)
            
            # Adicione os botões ao layout
            button_layout = QGridLayout()
            button_layout.addWidget(play_button, 0, 0)
            button_layout.addWidget(edit_button, 0, 1)
            button_layout.addWidget(remove_button, 0, 2)
            
            # Adicione o layout de botões ao layout de informações
            self.info_layout.addLayout(button_layout, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Configure o layout de informações na posição desejada
            self.layout().addLayout(self.info_layout, 0, 2, 5, 2)
            self.layout().update()
    
    # Funções dos botões
    def play_modpack(self):
        list_widget = self.findChild(QListWidget, "list_widget")  # Encontre o QListWidget pelo nome
        selected_items = list_widget.selectedItems()  # Obtenha os itens selecionados
        modpack = selected_items[0].data(Qt.ItemDataRole.UserRole)
        game = Game()
        game.set_mods_folder(os.path.join(os.getcwd(), modpack.mods_folder()))
        game.play()
        
    def edit_modpack(self):
        print("Botao EDITAR pressionado")
        
    def remove_modpack(self):
        print("Botão REMOVER pressionado")
    
    def init_ui(self):
        layout = QGridLayout()

        # Adicionar lista à esquerda
        list_widget = QListWidget(self)
        list_widget.setObjectName("list_widget")  # Defina o nome do objeto
        layout.addWidget(list_widget, 0, 0, 5, 2)  # (linha, coluna, rowspan, colspan)

        self.setLayout(layout)
        self.ListAllModpacks()
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Teste de Layout')
        self.show()

