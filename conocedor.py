import cv2
import os
from deepface import DeepFace

# =====================================================================

# =====================================================================
from logger import LoggerAcceso

os.makedirs("base_datos", exist_ok=True)  # Carpeta de rostros registrados
os.makedirs("logs", exist_ok=True)        # Carpeta de registros de acceso

# =====================================================================
# 1. ENTREGABLE: MÓDULO DE RECONOCIMIENTO FACIAL
# =====================================================================
def reconocer_rostro(frame_imagen, ruta_db="base_datos"):
    try:
        resultados = DeepFace.find(
            img_path=frame_imagen,
            db_path=ruta_db,
            model_name="Facenet",
            detector_backend="opencv",
            enforce_detection=False,
            silent=True
        )

        if len(resultados) > 0 and not resultados[0].empty:
            ruta_match = resultados[0].iloc[0]['identity']
            nombre_carpeta = os.path.basename(os.path.dirname(ruta_match))
            distancia = resultados[0].iloc[0]['distance']

            if distancia < 0.45:
                return nombre_carpeta.upper()
            else:
                return "DESCONOCIDO"
        else:
            return "Buscando rostro..."

    except Exception as e:
        return "Buscando rostro..."


# =====================================================================
# 2. MOTOR EN TIEMPO REAL (OPTIMIZADO PARA FPS)
# =====================================================================
if __name__ == "__main__":
    print("[INFO] Iniciando sistema de reconocimiento facial ultra rápido...")

    captura = cv2.VideoCapture(0)

    contador_frames = 0
    frecuencia_analisis = 10
    identidad_memoria = "Buscando..."

    # ▼  Inicializar el sistema de logs
    log = LoggerAcceso()

    while True:
        ret, frame = captura.read()
        if not ret:
            break

        if contador_frames % frecuencia_analisis == 0:
            identidad_memoria = reconocer_rostro(frame)
            # ▼ INTEGRANTE 4: Registrar cada detección en el log
            log.registrar(identidad_memoria)

        contador_frames += 1

        color = (0, 255, 0) if identidad_memoria not in ["DESCONOCIDO", "Buscando rostro...", "Buscando..."] else (0, 0, 255)

        cv2.putText(frame, f"Identidad: {identidad_memoria}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("Scanner de Acceso", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Mostrar resumen de accesos al cerrar
    log.resumen()

    captura.release()
    cv2.destroyAllWindows()
