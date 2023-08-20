from cx_Freeze import setup, Executable

executables = [
    Executable(
        script="main.py",
        base="Win32GUI",
    )
]

setup(
    name="SVMG - Stardew Valley Mod Manager",
    version="1.0",
    description="O SVMG (Stardew Valley Mod Manager) é uma ferramenta para gerenciar, sincronizar e atualizar mods do Stardew Valley.",
    executables=executables
)
