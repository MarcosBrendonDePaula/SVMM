from PyQt6.QtGui import QPixmap
from pathlib import Path
class Resources:
    PATH = Path('resources')
    
    @staticmethod
    def get_image(file = "")->QPixmap:
        path:Path = Resources.PATH / "img" / file
        pixmap = QPixmap(str(path))
        return pixmap
    
    @staticmethod
    def get_image_path(file = "")->Path:
        path = Resources.PATH / "img" / file
        return path
    