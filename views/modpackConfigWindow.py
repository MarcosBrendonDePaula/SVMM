import os
import base64
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QListWidgetItem,
    QListWidget, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage, QImageReader
from PyQt6.QtCore import Qt

def base64_to_img(_base64) -> QPixmap:
    icon_pixmap = QPixmap()
    icon_pixmap.loadFromData(base64.b64decode(_base64))  # Carregar o pixmap a partir dos dados
    return icon_pixmap

class ModpackConfigWindow(QDialog):
    def __init__(self, modpack):
        super().__init__()
        self.modpack = modpack
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Parte esquerda: Lista de mods com caixas de seleção
        self.mods_list_widget = QListWidget()
        self.update_mods_list()  # Atualiza a lista de mods
        layout.addWidget(self.mods_list_widget)

        # Parte direita: Campos de edição da modpack
        modpack_edit_layout = QVBoxLayout()

        name_label = QLabel("Nome da Modpack:")
        self.name_edit = QLineEdit(self.modpack.name)
        modpack_edit_layout.addWidget(name_label)
        modpack_edit_layout.addWidget(self.name_edit)

        image_label = QLabel("Imagem da Modpack:")
        self.image_edit = QLineEdit(self.modpack.image)
        modpack_edit_layout.addWidget(image_label)

        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = None
        if self.modpack.image:
            try:
                pixmap = base64_to_img(self.modpack.image)
            except Exception as e:
                print("Erro ao carregar a imagem:", e)

        if not pixmap == None:
            # Redimensionar a imagem como antes
            desired_width = 200
            desired_height = 200
            pixmap_resized = pixmap.scaled(desired_width, desired_height, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_preview.setPixmap(pixmap_resized)
        
        modpack_edit_layout.addWidget(self.image_preview)

        select_image_button = QPushButton('Selecionar Imagem')
        select_image_button.clicked.connect(self.select_image)
        modpack_edit_layout.addWidget(select_image_button)

        confirm_button = QPushButton('Confirmar')
        confirm_button.clicked.connect(self.confirm_changes)
        modpack_edit_layout.addWidget(confirm_button)

        # Habilitar todos os mods
        enable_all_button = QPushButton('Habilitar Todos')
        enable_all_button.clicked.connect(self.enable_all_mods)
        modpack_edit_layout.addWidget(enable_all_button)

        # Desabilitar todos os mods
        enable_all_button = QPushButton('Desabilitar Todos')
        enable_all_button.clicked.connect(self.disable_all_mods)
        modpack_edit_layout.addWidget(enable_all_button)
        
        layout.addLayout(modpack_edit_layout)

        self.setLayout(layout)

    def update_mods_list(self):
        all_mods = sorted(self.modpack.list_all_mods()['enabled'] + self.modpack.list_all_mods()['disabled'])
        self.mods_list_widget.clear()
        for mod_name in all_mods:
            item = QListWidgetItem(mod_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if mod_name in self.modpack.list_enabled_mods() else Qt.CheckState.Unchecked)
            self.mods_list_widget.addItem(item)

    def select_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Images (*.png *.jpg *.jpeg);;All Files (*)")
        
        if image_path:
            # Verifique se a imagem é válida usando QImageReader
            image_reader = QImageReader(image_path)
            if image_reader.size().isValid():
                with open(image_path, 'rb') as image_file:
                    image_data = image_file.read()
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    
                    self.image_edit.setText(base64_image)
                    
                    # Redimensionar a imagem para 200x200
                    pixmap = QPixmap.fromImage(QImage.fromData(image_data))
                    desired_width = 200
                    desired_height = 200
                    pixmap_resized = pixmap.scaled(desired_width, desired_height, Qt.AspectRatioMode.KeepAspectRatio)
                    self.image_preview.setPixmap(pixmap_resized)
            else:
                # Imagem inválida, exiba uma mensagem de erro
                QMessageBox.critical(self, "Erro", "A imagem selecionada não é válida.")

    def confirm_changes(self):
        # Atualize os mods habilitados/desabilitados com base nas caixas de seleção
        for row in range(self.mods_list_widget.count()):
            item = self.mods_list_widget.item(row)
            mod_name = item.text()
            if item.checkState() == Qt.CheckState.Checked:
                self.modpack.enable_mod(mod_name)
            else:
                self.modpack.disable_mod(mod_name)

        # Atualize o nome e a imagem da modpack
        new_name = self.name_edit.text()
        new_image = self.image_edit.text()

        if new_name != self.modpack.name:
            self.modpack.rename_modpack(new_name)

        self.modpack.name = new_name
        self.modpack.image = new_image
        self.modpack.save()

        self.close()

    def enable_all_mods(self):
        self.modpack.enable_all_mods()
        self.update_mods_list()  # Atualiza a lista de mods
        
    def disable_all_mods(self):
        self.modpack.disable_all_mods()
        self.update_mods_list()  # Atualiza a lista de mod