from cx_Freeze import setup, Executable

executables = [
    Executable(
        script="main.py",
        # base="Win32GUI",
        icon="resources/icon.ico",  # Substitua pelo caminho real para o ícone
        target_name="SVMG.exe",  # Substitua pelo nome que desejar para o executável
        shortcut_name="SVMG - Stardew Valley Mod Manager",  # Nome para o atalho no menu Iniciar
        shortcut_dir="DesktopFolder",  # Local para criar o atalho (DesktopFolder = Área de Trabalho)
        # Adicione a linha abaixo para solicitar privilégios de administrador
        uac_admin=True
    )
]

setup(
    name="SVMG - Stardew Valley Mod Manager",
    version="1.0",
    description="O SVMG (Stardew Valley Mod Manager) é uma ferramenta para gerenciar, sincronizar e atualizar mods do Stardew Valley.",
    executables=executables,
    options={
        "build_exe": {
            "include_files": "resources"
        }
    },
)