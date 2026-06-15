# ==================================================
# IMPORTACIÓN DE LIBRERÍAS
# ==================================================

# MTCNN se utiliza para la detección de rostros
from mtcnn import MTCNN

# OpenCV se utiliza para el procesamiento de imágenes
import cv2

# ==================================================
# INICIALIZAR DETECTOR FACIAL
# ==================================================

# Crear una instancia del detector MTCNN
detector = MTCNN()

# ==================================================
# FUNCIÓN DE DETECCIÓN FACIAL
# ==================================================

def detectar_rostro(imagen):
    """
    Detecta uno o varios rostros dentro de una imagen.

    Parámetros:
        imagen (numpy.ndarray):
        Imagen capturada por OpenCV en formato BGR.

    Retorna:
        list:
        Lista de rostros detectados con información como:
        - Coordenadas del rostro (box)
        - Nivel de confianza (confidence)
        - Puntos clave faciales (ojos, nariz y boca)
    """

    # Convertir la imagen de BGR a RGB
    # MTCNN trabaja con imágenes en formato RGB
    rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

    # Detectar rostros en la imagen
    resultados = detector.detect_faces(rgb)

    # Devolver resultados encontrados
    return resultados