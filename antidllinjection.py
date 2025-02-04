import ctypes
from ctypes import wintypes, POINTER

PROCESS_SIGNATURE_POLICY_MITIGATION = 8
class PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY(ctypes.Structure):
    _fields_ = [("MicrosoftSignedOnly", wintypes.DWORD)]

kernelbase = ctypes.WinDLL("kernelbase.dll")

SetProcessMitigationPolicy = kernelbase.SetProcessMitigationPolicy
SetProcessMitigationPolicy.argtypes = [
    wintypes.DWORD,                            # policy
    POINTER(PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY),  # lpBuffer
    wintypes.DWORD                             # size
]
SetProcessMitigationPolicy.restype = wintypes.BOOL

def set_process_mitigation_policy():
    binary_policy = PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY()
    binary_policy.MicrosoftSignedOnly = 1

    success = SetProcessMitigationPolicy(
        PROCESS_SIGNATURE_POLICY_MITIGATION,
        ctypes.byref(binary_policy),
        ctypes.sizeof(binary_policy)
    )

    if not success:
        error_code = ctypes.GetLastError()
        raise ctypes.WinError(error_code)

    return True

if __name__ == "__main__":
    try:
        if set_process_mitigation_policy():
            print("Política de mitigación configurada correctamente.")
    except Exception as e:
        print(f"Error al configurar la política de mitigación: {e}")
