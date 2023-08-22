
import os, base64
from PyQt6.QtGui import QPixmap

class Converter:
    
    @staticmethod    
    def base64_to_QPixmap(_base64) -> QPixmap:
        icon_pixmap = QPixmap()
        icon_pixmap.loadFromData(base64.b64decode(_base64))  # Carregar o pixmap a partir dos dados
        return icon_pixmap
    pass
