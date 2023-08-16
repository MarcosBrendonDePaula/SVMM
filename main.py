from config import Config
from game import Game
from modpack import Modpack
import os

if __name__ == '__main__':
    conf = Config()
    conf.load()
    #cria uma modpack
    modpack = Modpack("henri")

    #carrega uma modpack ja criada
    modpack = Modpack.load_from_json('marcos')

    #lista as modpacks validas
    print(Modpack.list_modpacks())

    #instancia todas as modpacks validas
    print(Modpack.get_all_modpacks())

    game = Game()


    game.set_mods_folder(os.path.join(os.getcwd(), modpack.mods_folder()))
    game.play()

    pass
