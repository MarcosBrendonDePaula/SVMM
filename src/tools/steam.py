import psutil, os, subprocess, time

class Steam:
    @staticmethod
    def exists():
        return Steam._check_common_locations() or Steam._check_all_drives()
    
    @staticmethod
    def get_installation_path():
        return Steam._find_steam_in_common_locations() or Steam._find_steam_in_all_drives()
    
    @staticmethod
    def _check_common_locations():
        steam_executable = "Steam.exe"
        
        # Verifique se o executável da Steam está em locais comuns
        common_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Steam", steam_executable),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Steam", steam_executable),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs", "Steam", steam_executable),
        ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return True
        
        return False
    
    @staticmethod
    def _find_steam_in_common_locations():
        steam_executable = "Steam.exe"
        
        # Verifique se o executável da Steam está em locais comuns
        common_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Steam", steam_executable),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Steam", steam_executable),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs", "Steam", steam_executable),
        ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return os.path.dirname(path)
        
        return None

    @staticmethod
    def _check_all_drives():
        steam_executable = "Steam.exe"
        
        # Obtenha uma lista de todas as partições do disco no sistema
        partitions = psutil.disk_partitions()
        drive_letters = [partition.device.split(':')[0] for partition in partitions if partition.device]
        
        # Verifique se o executável da Steam está em todos os discos
        for drive in drive_letters:
            steam_path = os.path.join(drive, "Steam", steam_executable)
            if os.path.isfile(steam_path):
                return True
        
        return False
    
    @staticmethod
    def _find_steam_in_all_drives():
        steam_executable = "Steam.exe"
        
        # Obtenha uma lista de todas as partições do disco no sistema
        partitions = psutil.disk_partitions()
        drive_letters = [partition.device.split(':')[0] for partition in partitions if partition.device]
        
        # Verifique se o executável da Steam está em todos os discos
        for drive in drive_letters:
            common_paths = [
                os.path.join(os.environ.get("ProgramFiles", ""), "Steam", steam_executable).replace('C:\\', f"{drive}\\"),
                os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Steam", steam_executable).replace('C:\\', f"{drive}\\"),
            ]
            for path in common_paths:
                if os.path.isfile(path):
                    return path
        return None
    
    @staticmethod
    def start_steam_and_wait():
        steam_executable = "Steam.exe"
        
        # Verifique se o Steam.exe está em locais comuns
        common_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Steam", steam_executable),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Steam", steam_executable),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs", "Steam", steam_executable),
        ]
        
        steam_path = None
        
        for path in common_paths:
            if os.path.isfile(path):
                steam_path = path
                break
        
        if steam_path is None:
            print("Steam não encontrado em locais comuns.")
            return
        
        # Inicie o Steam
        subprocess.Popen([steam_path])
        
        # Aguarde até que o processo do Steam seja criado
        while not Steam.is_steam_running():
            time.sleep(1)
        
    @staticmethod
    def is_steam_running():
        steamwebhelper_count = 0
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if str(process.info['name']).lower() == 'steamwebhelper.exe':
                steamwebhelper_count += 1
        return steamwebhelper_count > 5
