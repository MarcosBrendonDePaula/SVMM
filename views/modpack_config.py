import os
import base64, i18n, logging
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QListWidgetItem,
    QListWidget, QHBoxLayout, QFileDialog, QMessageBox, QProgressBar, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage, QImageReader, QColor, QBrush, QCursor, QIcon
from PyQt6.QtCore import Qt, QSize, QThread

from src.mod import Mod
from src.tools import (Converter, Resources)
from src.modpack import Modpack
from PyQt6.QtCore import pyqtSignal

class WorkerUpload(QThread):
    def __init__(self, modpack:Modpack):
        super().__init__()
        self.modpack = modpack

    def run(self):
        self.modpack.sync()
        
class WorkerDownload(QThread):
    def __init__(self, modpack:Modpack):
        super().__init__()
        self.modpack = modpack

    def run(self):
        self.modpack.update_modpack()

class ModpackConfigWindow(QDialog):
    
    ICON_SCALE = 0.9
    BUTTON_SCALE = 1
    
    updateSignal = pyqtSignal(dict)
    
    def __init__(self, modpack:Modpack):
        super().__init__()
        self.modpack = modpack
        self.initUi()

    def button_size_rule(self, button:QPushButton):
        button.setMinimumWidth(180 * ModpackConfigWindow.BUTTON_SCALE)
    
    def initUi(self):
        layout = QHBoxLayout()
        self.image = None
        # Parte esquerda: Lista de mods com caixas de seleção
        self.mods_list_widget = QListWidget()
        self.mods_list_widget.itemDoubleClicked.connect(self.item_double_clicked)
        self.mods_list_widget.itemClicked.connect(self.item_selected)
        self.update_mods_list()  # Atualiza a lista de mods
        layout.addWidget(self.mods_list_widget)

        # Parte direita: Campos de edição da modpack
        modpack_edit_layout = QVBoxLayout()

        name_label = QLabel(i18n.t(f'mp.name'))
        self.name_edit = QLineEdit("")
        self.name_edit.editingFinished.connect(self.save)
        
        modpack_edit_layout.addWidget(name_label)
        modpack_edit_layout.addWidget(self.name_edit)

        image_label = QLabel(i18n.t(f'mp.image'))
        self.image_edit = QLineEdit(self.modpack.image)
        modpack_edit_layout.addWidget(image_label)

        # Layou horizontal para ancorar botao de trocar imagem ao topo na direita
        hbox_layout = QHBoxLayout()

        self.change_image_button = QPushButton()
        self.define_button_icon(self.change_image_button, 'camera_icon.png', (int(40 * self.ICON_SCALE), int(40 * self.ICON_SCALE)), False)

        self.change_image_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.change_image_button.setToolTip(i18n.t(f'mp.change.image'))
        self.change_image_button.clicked.connect(self.select_image)
        self.change_image_button.setStyleSheet('border: none;')
        hbox_layout.addStretch()

        hbox_layout.addWidget(self.change_image_button)
        modpack_edit_layout.addLayout(hbox_layout)

        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        modpack_edit_layout.addWidget(self.image_preview)
        #Ajustar imagem ao topo caso a janela seja redimensionada
        modpack_edit_layout.addStretch()
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        modpack_edit_layout.addWidget(self.progress_bar)
        
        self.send_button = QPushButton(i18n.t(f'mp.btn.upload'))
        self.define_button_icon(self.send_button, 'UploadToCloud.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        self.send_button.clicked.connect(self.upload_modpack)
        
        hbox_layout_mods_upload_download = QHBoxLayout()
        hbox_layout_mods_upload_download.addStretch()
        if self.modpack.is_owner:
            self.button_size_rule(self.send_button)
            hbox_layout_mods_upload_download.addWidget(self.send_button)
        
        self.download_button = QPushButton(i18n.t(f'mp.btn.download'))
        self.button_size_rule(self.download_button)
        self.download_button.clicked.connect(self.download_modpack)
        self.define_button_icon(self.download_button, 'DownloadFromCloud.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        hbox_layout_mods_upload_download.addWidget(self.download_button)
        hbox_layout_mods_upload_download.addStretch()
        modpack_edit_layout.addLayout(hbox_layout_mods_upload_download)
        
        
        hbox_layout_mods = QHBoxLayout()
        hbox_layout_mods.addStretch()
        install_mod_button = QPushButton(i18n.t(f'mp.btn.mod.install'))
        install_mod_button.clicked.connect(self.install_mod)
        self.button_size_rule(install_mod_button)
        self.define_button_icon(install_mod_button, 'Enter.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        hbox_layout_mods.addWidget(install_mod_button)
        
        self.delete_mod_button = QPushButton(i18n.t(f'mp.btn.mod.delete'))
        self.delete_mod_button.clicked.connect(self.delete_mod)
        self.button_size_rule(self.delete_mod_button)
        self.define_button_icon(self.delete_mod_button, 'Delete.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        self.delete_mod_button.setDisabled(True)
        hbox_layout_mods.addWidget(self.delete_mod_button)
        hbox_layout_mods.addStretch()
        
        modpack_edit_layout.addLayout(hbox_layout_mods)
        
        
        # Habilitar todos os mods
        hbox_layout_mods_all = QHBoxLayout()
        hbox_layout_mods_all.addStretch()
        enable_all_button = QPushButton(i18n.t(f'mp.btn.mod.enable.mods'))
        self.button_size_rule(enable_all_button)
        enable_all_button.clicked.connect(self.enable_all_mods)
        self.define_button_icon(enable_all_button, 'Open View.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        hbox_layout_mods_all.addWidget(enable_all_button)

        # Desabilitar todos os mods
        disable_all_button = QPushButton(i18n.t(f'mp.btn.mod.disable.mods'))
        disable_all_button.clicked.connect(self.disable_all_mods)
        self.button_size_rule(disable_all_button)
        self.define_button_icon(disable_all_button, 'Delete View.png', (int(45 * self.ICON_SCALE), int(45 * self.ICON_SCALE)), False)
        hbox_layout_mods_all.addWidget(disable_all_button)
        hbox_layout_mods_all.addStretch()
        modpack_edit_layout.addLayout(hbox_layout_mods_all)


        self.show_info()
        layout.addLayout(modpack_edit_layout)
        self.setLayout(layout)
        self.setWindowIcon(QIcon(Resources.get_image("Open Parcel.png")))
        self.setWindowTitle("Modpack Editor")
    
    def save(self):
        self.modpack.image = self.image or self.modpack.image 
        self.modpack.name = self.name_edit.text()
        self.modpack.save()
        self.updateSignal.emit({})
    
    def update_progress(self, args:dict):
        if args['step'] == 0:
            self.send_button.setText(i18n.t('mp.btn.event.mapping'))
            self.send_button.setDisabled(True)
        elif args['step'] == 1:
            self.send_button.setText(i18n.t('mp.btn.event.uploading'))
        self.progress_bar.setValue(int(round(args['progress'])))
        pass
        if args['done']:
            self.send_button.setDisabled(False)
            self.progress_bar.setVisible(False)
            self.send_button.setText(i18n.t(f'mp.btn.upload'))
    
    def download_progress(self, args:dict):
        if args['step'] == 0:
            self.download_button.setText(i18n.t('mp.btn.event.mapping'))
            self.download_button.setDisabled(True)
        elif args['step'] == 1:
            self.download_button.setText(i18n.t('mp.btn.event.downloading'))
        self.progress_bar.setValue(int(round(args['progress'])))
        pass
        if args['done']:
            self.download_button.setDisabled(False)
            self.progress_bar.setVisible(False)
            self.download_button.setText(i18n.t(f'mp.btn.download'))
            self.update_mods_list()
            self.modpack.reload()
            self.show_info()
            self.save()
    
    def show_info(self):
        self.name_edit.setText(self.modpack.name)
        pixmap = None
        if self.modpack.image:
            try:
                pixmap = Converter.base64_to_QPixmap(self.modpack.image)
            except Exception as e:
                logging.error(f"Error loading the image:{e}")

        if not pixmap == None:
            # Redimensionar a imagem como antes
            desired_width = 200
            desired_height = 200
            pixmap_resized = pixmap.scaled(desired_width, desired_height, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_preview.setPixmap(pixmap_resized)
        pass
    
    def upload_modpack(self):
        self.modpack.uploadSignal.connect(self.update_progress)
        self.worker = WorkerUpload(self.modpack)
        self.worker.start()
        self.progress_bar.setVisible(True)
    
    def download_modpack(self):
        self.modpack.uploadSignal.connect(self.download_progress)
        self.worker = WorkerDownload(self.modpack)
        self.worker.start()
        self.progress_bar.setVisible(True)
        pass
    
    def item_double_clicked(self, item):
        mod:Mod = item.data(Qt.ItemDataRole.UserRole)  # Obtém o objeto Mod associado ao item
        if mod:
            mod_folder_path = mod.mod_folder_path
            if os.path.exists(mod_folder_path):
                os.startfile(mod_folder_path)  # Abre a pasta do mod no sistema
    
    def handle_mod_item_change(self, item):
        mod_name = item.text()
        if item.checkState() == Qt.CheckState.Checked:
            self.modpack.enable_mod(mod_name.replace(' - Incomplete',""))
        else:
            self.modpack.disable_mod(mod_name.replace(' - Incomplete',""))
    
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
            self.mods_list_widget.addItem(item)
            self.mods_list_widget.itemChanged.connect(self.handle_mod_item_change)

    def select_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Images (*.png *.jpg *.jpeg);;All Files (*)")
        
        if image_path:
            # Verifique se a imagem é válida usando QImageReader
            image_reader = QImageReader(image_path)
            if image_reader.size().isValid():
                with open(image_path, 'rb') as image_file:
                    image_data = image_file.read()

                    # Verifique o tamanho do arquivo (em bytes)
                    max_file_size = 1024 * 1024 * 15  # 15 MB em bytes
                    if len(image_data) > max_file_size:
                        max_size_mb = max_file_size / (1024 * 1024)  # Convertendo para MB
                        QMessageBox.critical(self, "Erro", f"A imagem selecionada é maior do que {max_size_mb:.2f} MB.")
                        return

                    self.image = base64.b64encode(image_data).decode('utf-8')
                    
                    # Redimensionar a imagem para 200x200
                    pixmap = QPixmap.fromImage(QImage.fromData(image_data))
                    desired_width = 200
                    desired_height = 200
                    pixmap_resized = pixmap.scaled(desired_width, desired_height, Qt.AspectRatioMode.KeepAspectRatio)
                    self.image_preview.setPixmap(pixmap_resized)
                    self.save()
            else:
                # Imagem inválida, exiba uma mensagem de erro
                QMessageBox.critical(self, "Erro", "A imagem selecionada não é válida.")

    def confirm_changes(self):
        # Atualize os mods habilitados/desabilitados com base nas caixas de seleção
        for row in range(self.mods_list_widget.count()):
            item = self.mods_list_widget.item(row)
            mod_name = item.text()
            if item.checkState() == Qt.CheckState.Checked:
                self.modpack.enable_mod(mod_name.replace(' - Incomplete',""))
            else:
                self.modpack.disable_mod(mod_name.replace(' - Incomplete',""))

        # Atualize o nome e a imagem da modpack
        new_name = self.name_edit.text()

        if new_name != self.modpack.name:
            self.modpack.rename_modpack(new_name)
        if self.image:
            self.modpack.image = self.image
        
        self.modpack.name = new_name
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

    def delete_mod(self):
        selected_items = self.mods_list_widget.selectedItems()
        item = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.modpack.delete_mod(item)
        self.delete_mod_button.setDisabled(True)
        self.update_mods_list()
        pass
    
    def item_selected(self, item):
        self.delete_mod_button.setDisabled(False)
        pass
    
    def define_button_icon(self, button:QPushButton, resource_img_name, size=(45,45), usePolice = True):
        icon = QIcon(f"{Resources.get_image_path(resource_img_name)}")
        icon_pixmap = icon.pixmap(size[0], size[1])
        button.setIcon(icon)
        button.setIconSize(icon_pixmap.size())
        button.setStyleSheet('text-align: left;')
        if usePolice:
            self.define_button_icon_pollice(button, size)
    
    def define_button_icon_pollice(self, button:QPushButton, size=(45,45)):
        size_policy = button.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        button.setSizePolicy(size_policy)
        button.setFixedSize(size[0], size[1])