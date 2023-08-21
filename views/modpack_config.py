import os
import base64
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QListWidgetItem,
    QListWidget, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage, QImageReader, QColor, QBrush
from PyQt6.QtCore import Qt

def base64_to_img(_base64) -> QPixmap:
    icon_pixmap = QPixmap()
    icon_pixmap.loadFromData(base64.b64decode(_base64))  # Carregar o pixmap a partir dos dados
    return icon_pixmap

class ModpackConfigWindow(QDialog):
    def __init__(self, modpack):
        super().__init__()
        self.modpack = modpack
        self.initUi()

    def initUi(self):
        layout = QHBoxLayout()
        # Parte esquerda: Lista de mods com caixas de seleção
        self.mods_list_widget = QListWidget()
        self.mods_list_widget.itemDoubleClicked.connect(self.item_double_clicked)
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
        
        install_mod_button = QPushButton('Instalar Mod')
        install_mod_button.clicked.connect(self.install_mod)
        modpack_edit_layout.addWidget(install_mod_button)
        
        layout.addLayout(modpack_edit_layout)
        self.setLayout(layout)
        self.setWindowTitle("Modpack Editor")
        
    def item_double_clicked(self, item):
        mod = item.data(Qt.ItemDataRole.UserRole)  # Obtém o objeto Mod associado ao item
        if mod:
            mod_folder_path = mod.mod_folder_path
            if os.path.exists(mod_folder_path):
                os.startfile(mod_folder_path)  # Abre a pasta do mod no sistema
    
    def update_mods_list(self):
        all_mods = sorted(self.modpack.get_enabled_mods() + self.modpack.get_disabled_mods(), key=lambda mod: mod.name)
        self.mods_list_widget.clear()
        
        for mod in all_mods:
            item = QListWidgetItem(mod.parent_folder_name)
            item.setData(Qt.ItemDataRole.UserRole, mod)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            if mod.parent_folder_name in self.modpack.list_enabled_mods():
                item.setCheckState(Qt.CheckState.Checked)
                dependencies_complete = self.modpack.mod_dependencies_complete(mod)
                
                if not dependencies_complete:
                    brush = QBrush(QColor.fromRgb(255, 200, 200))  # Criando um pincel com a cor de fundo vermelho claro
                    item.setText(f"{mod.parent_folder_name} - Incomplete")
                else:
                    brush = QBrush(QColor.fromRgb(200, 255, 200))  # Criando um pincel com a cor de fundo verde claro
                    item.setText(mod.parent_folder_name)
                
                item.setBackground(brush)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                brush = QBrush(QColor.fromRgb(255, 200, 200))  # Criando um pincel com a cor de fundo vermelho claro
                item.setBackground(brush)
            self.mods_list_widget.addItem(item)

    def select_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Images (*.png *.jpg *.jpeg);;All Files (*)")
        
        if image_path:
            # Verifique se a imagem é válida usando QImageReader
            image_reader = QImageReader(image_path)
            if image_reader.size().isValid():
                with open(image_path, 'rb') as image_file:
                    image_data = image_file.read()

                    # Verifique o tamanho do arquivo (em bytes)
                    max_file_size = 1024 * 1024  # 1 MB em bytes
                    if len(image_data) > max_file_size:
                        max_size_mb = max_file_size / (1024 * 1024)  # Convertendo para MB
                        QMessageBox.critical(self, "Erro", f"A imagem selecionada é maior do que {max_size_mb:.2f} MB.")
                        return

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
        
    def install_mod(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Selecionar Mods", "", "Mod Files (*.zip *.rar);;")
        if file_paths:
            for file_path in file_paths:
                self.modpack.install_mod(file_path)
            self.update_mods_list()
            QMessageBox.information(self, "Mods Instalados", "Os mods foram instalados com sucesso.")
