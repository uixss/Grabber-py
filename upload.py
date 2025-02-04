import requests
import os

def upload_file_to_fileio(path):
    """
    Sube un archivo a file.io y retorna el enlace de descarga si es exitoso.

    Args:
        path (str): Ruta del archivo a subir.

    Returns:
        str: Enlace de descarga si la subida es exitosa.
        bool: False si ocurre un error.
    """
    # Validar si el archivo existe
    if not os.path.exists(path):
        print(f"Error: El archivo '{path}' no existe.")
        return False

    try:
        # Abrir el archivo en modo binario
        with open(path, 'rb') as file:
            # Enviar el archivo al servicio file.io
            response = requests.post("https://file.io", files={'file': file})

        # Validar la respuesta
        if response.status_code == 200:
            upload_data = response.json()
            if upload_data.get('success'):
                return upload_data.get('link')
            else:
                print(f"Error al subir el archivo: {upload_data.get('message', 'Desconocido')}")
                return False
        else:
            print(f"Error: Respuesta inesperada del servidor (código {response.status_code}).")
            return False

    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False



def get_best_server():
    response = requests.get("https://api.gofile.io/getServer")
    data = response.json()
    if data['status'] == 'ok':
        return data['data']['server']
    else:
        raise Exception("Failed to get a server from Gofile.")

def upload_file_to_gofile(file_path, server):
    upload_url = f"https://{server}.gofile.io/uploadFile"
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post(upload_url, files=files)
    data = response.json()
    if data['status'] == 'ok':
        return data['data']['downloadPage']
    else:
        raise Exception("Failed to upload file to Gofile.")