from PyQt6.QtWidgets import QApplication
import sys

from src.config import Config
from src.game import Game
from src.modpack import Modpack
import os, logging

from views.menu import MenuView

import i18n

if __name__ == '__main__':
    conf = Config()
    conf.load()
    app = QApplication(sys.argv)
    ex = MenuView()
    sys.exit(app.exec())
    pass
