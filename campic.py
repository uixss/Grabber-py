import cv2

def take():
    # Intentar abrir la cámara
    cap = cv2.VideoCapture(0)

    # Verificar si la cámara está disponible
    if not cap.isOpened():
        print("No se encontró ninguna cámara.")
        return

    # Capturar un cuadro de la cámara
    ret, frame = cap.read()
    
    if ret:  # Si la captura fue exitosa
        cv2.imwrite("image.png", frame)
        print("Imagen capturada y guardada como image.png.")
    else:
        print("No se pudo capturar la imagen.")

    # Liberar la cámara y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()
take()
