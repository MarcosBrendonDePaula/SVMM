from config import Config
from game import Game
from modpack import Modpack
import os

if __name__ == '__main__':
    conf = Config()
    conf.load()

    modpack = Modpack("henri")
    modpack.save()

    modpack = Modpack("marcos")
    modpack.save()

    game = Game()


    game.set_mods_folder(os.path.join(os.getcwd(), modpack.mods_folder()))
    game.play()

    pass
