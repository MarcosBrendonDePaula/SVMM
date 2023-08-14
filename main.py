from config import Config
from game import Game


if __name__ == '__main__':
    conf = Config()
    conf.load()

    game = Game()
    game.set_mods_folder("teste1")
    game.play()

    pass
