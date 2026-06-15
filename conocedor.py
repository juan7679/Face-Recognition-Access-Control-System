import cv2
import os
import csv
from datetime import datetime
from deepface import DeepFace
from detector import detectar_rostro
# =====================================================================
# CONFIGURACIÓN DE LOGS
# =====================================================================
CARPETA_LOGS  = "logs"
ARCHIVO_LOG   = os.path.join(CARPETA_LOGS, "accesos.log")
ARCHIVO_CSV   = os.path.join(CARPETA_LOGS, "accesos.csv")
COOLDOWN_SEGS = 5

os.makedirs("base_datos", exist_ok=True)
os.makedirs(CARPETA_LOGS,  exist_ok=True)

if not os.path.exists(ARCHIVO_CSV):
    with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["fecha", "hora", "identidad", "evento"])

_ultimo_registro = {}

def registrar_acceso(identidad: str):
    if identidad in ("Buscando rostro...", "Buscando...", ""):
        return
    ahora  = datetime.now()
    ultimo = _ultimo_registro.get(identidad)
    if ultimo and (ahora - ultimo).total_seconds() < COOLDOWN_SEGS:
        return
    _ultimo_registro[identidad] = ahora
    evento    = "ACCESO CONCEDIDO" if identidad != "DESCONOCIDO" else "ACCESO DENEGADO"
    fecha_str = ahora.strftime("%Y-%m-%d")
    hora_str  = ahora.strftime("%H:%M:%S")
    linea     = f"[{fecha_str} {hora_str}] {evento:<20} | {identidad}"
    with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
    with open(ARCHIVO_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([fecha_str, hora_str, identidad, evento])
    simbolo = "✔" if identidad != "DESCONOCIDO" else "✘"
    print(f"[LOG] {simbolo} {linea}")

def resumen_logs():
    if not os.path.exists(ARCHIVO_CSV):
        return
    conteo = {}
    with open(ARCHIVO_CSV, "r", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            conteo[fila["identidad"]] = conteo.get(fila["identidad"], 0) + 1
    print("\n[LOG] ── RESUMEN DE SESIÓN ──────────────────────")
    for nombre, veces in sorted(conteo.items(), key=lambda x: -x[1]):
        print(f"       {nombre:<28} {veces:>4} registro(s)")
    print("[LOG] ────────────────────────────────────────────\n")


# =====================================================================
# 1. ENTREGABLE: MÓDULO DE RECONOCIMIENTO FACIAL
# =====================================================================
def reconocer_rostro(frame_imagen, ruta_db="base_datos"):
    # Primero verificar si hay rostro con MTCNN
    rostros = detectar_rostro(frame_imagen)
    if len(rostros) == 0:
        return "Buscando rostro..."
    
    # Si hay rostro, reconocer con DeepFace
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
            
            if distancia < 0.30:
                return nombre_carpeta.upper()
            else:
                return "DESCONOCIDO"
        else:
            return "DESCONOCIDO"
            
    except Exception as e:
        return "DESCONOCIDO"


# =====================================================================
# 2. MOTOR EN TIEMPO REAL (OPTIMIZADO PARA FPS)
# =====================================================================
if __name__ == "__main__":
    print("[INFO] Iniciando sistema de reconocimiento facial ultra rápido...")
    
    captura = cv2.VideoCapture(0)
    
    # --- VARIABLES PARA EL HACK DE VELOCIDAD ---
    contador_frames = 0
    frecuencia_analisis = 10  # Analiza 1 de cada 10 fotogramas
    identidad_memoria = "Buscando..."

    while True:
        ret, frame = captura.read()
        if not ret:
            break
            
        # Solo ejecutamos la IA pesada cuando el contador es múltiplo de 10
        if contador_frames % frecuencia_analisis == 0:
            identidad_memoria = reconocer_rostro(frame)
            registrar_acceso(identidad_memoria)
            
        contador_frames += 1
        
        # --- INTERFAZ GRÁFICA ---
        color = (0, 255, 0) if identidad_memoria not in ["DESCONOCIDO", "Buscando rostro...", "Buscando..."] else (0, 0, 255)
        
        cv2.putText(frame, f"Identidad: {identidad_memoria}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.imshow("Scanner de Acceso", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    resumen_logs()
    captura.release()
    cv2.destroyAllWindows()
