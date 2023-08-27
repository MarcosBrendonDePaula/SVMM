from PyQt6.QtWidgets import QApplication
import sys

from src.config import Config
from src.game import Game
from src.modpack import Modpack
import os

from views.menu import MenuView

if __name__ == '__main__':
    conf = Config()
    conf.load()
    
    app = QApplication(sys.argv)
    ex = MenuView()
    sys.exit(app.exec())
    
    #carrega uma modpack ja criada
    # modpack = Modpack.load_from_json('marcos')
    # # modpack.disable_mod('ExpandedPreconditionsUtility')
    # enabled_mods = modpack.get_disabled_mods()
    # print("Enabled Mods:")
    # for index, mod in enumerate(enabled_mods, start=1):
    #     print(f"Mod {index}:")
    #     print("Mod Name:", mod.name)
    #     print("Mod Author:", mod.author)
    #     print("Mod version:", mod.version)

    #     if mod.dependencies:
    #         # dependencies_list = [dependency["UniqueID"] for dependency in mod.dependencies]
    #         # dependencies_str = ", ".join(dependencies_list)
    #         # print("Mod Dependencies:", dependencies_str)
    #         print(mod.dependencies)      
    #     else:
    #         print("Mod Dependencies: None")
    #     print("=" * 30)  # Linha de separação entre os mods


    # disabled_mods = modpack.get_disabled_mods()
    # print("Disabled Mods:")
    # for mod in disabled_mods:
    #     print("Mod Name:", mod.name)
    #     print("Mod Author:", mod.author)
    #     print("Mod Dependencies:", [dependency["UniqueID"] for dependency in mod.dependencies])
    #lista as modpacks validas
    # print(Modpack.list_modpacks())

    #instancia todas as modpacks validas
    # print(Modpack.get_all_modpacks())

    

    # conf = Config()
    # conf.load()
    # game = Game()
    # game.set_mods_folder(os.path.join(os.getcwd(), modpack.mods_folder()))
    # game.play()

    # Crie uma instância da classe Modpack
    # modpack_name = "minha_modpack"
    # modpack = Modpack(modpack_name)

    # # Liste os mods habilitados e desabilitados
    # print("Mods habilitados:", modpack.list_enabled_mods())
    # print("Mods desabilitados:", modpack.list_disabled_mods())

    # # Habilite alguns mods
    # mods_to_enable = ['ExpandedPreconditionsUtility', 'ZoomLevel']
    # modpack.enable_mods(mods_to_enable)

    # # Liste novamente os mods habilitados e desabilitados
    # print("Mods habilitados após habilitar:", modpack.list_enabled_mods())
    # print("Mods desabilitados após habilitar:", modpack.list_disabled_mods())

    # # Desabilite alguns mods
    # mods_to_disable = ['ZoomLevel','ExpandedPreconditionsUtility']
    # modpack.disable_mods(mods_to_disable)

    # # Liste novamente os mods habilitados e desabilitados
    # print("Mods habilitados após desabilitar:", modpack.list_enabled_mods())
    # print("Mods desabilitados após desabilitar:", modpack.list_disabled_mods())
    pass
