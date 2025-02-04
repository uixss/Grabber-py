
# Asignación de memoria (solo para Windows)
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

# Funciones para obtener información del sistema