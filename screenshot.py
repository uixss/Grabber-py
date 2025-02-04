
import os
from PIL import ImageGrab

user = os.path.expanduser("~")

def screen():
    sss = ImageGrab.grab()
    temp_path = os.path.join(user, "AppData\\Local\\Temp\\ss.png")
    sss.save(temp_path)

    try:
        os.remove(temp_path)
    except Exception as e:
        print(f"Error removing file: {e}")

screen()
