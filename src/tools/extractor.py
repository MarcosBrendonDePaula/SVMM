import os
import winreg
from pyunpack import Archive
import subprocess

class Extractor:
    @staticmethod
    def get_winrar_installation_path():
        try:
            # Abrir a chave de registro correspondente à instalação do WinRAR
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WinRAR.exe") as key:
                # Obter o valor padrão (que é o caminho de instalação do WinRAR)
                winrar_path = winreg.QueryValue(key, None)
                return winrar_path
        except Exception:
            return None
    
    @staticmethod
    def extract_rar(rar_file, output_path):
        winrar_path = Extractor.get_winrar_installation_path()
        if not winrar_path:
            print("WinRAR não foi encontrado. Certifique-se de que o WinRAR está instalado e registrado no registro do Windows.")
            return
        try:
            subprocess.run([winrar_path, 'x', rar_file, output_path], shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ocorreu um erro ao converter o arquivo: {e}")
        finally:
            pass

    @staticmethod
    def extract(file, out):
        is_zip = file.lower().endswith('.zip')
        is_rar = file.lower().endswith('.rar')
        
        if is_rar:
            Extractor.extract_rar(file, os.path.join(out,''))
        elif is_zip:
            Archive(file).extractall(out)
        else:
            print("Formato de arquivo não suportado")
            return