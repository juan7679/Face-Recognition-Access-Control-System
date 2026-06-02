"""
interfaz.py — Interfaz del sistema de reconocimiento facial (OpenCV)
Requiere: conocedor.py en la misma carpeta
Dependencias: pip install deepface opencv-python numpy tf-keras tensorflow
"""

import cv2
import os
import shutil
import time
import numpy as np

# ── Cargar módulo del compañero ───────────────────────────────────────
print("[INFO] Cargando modelos de IA, espera unos segundos...")
try:
    from conocedor import reconocer_rostro
    print("[INFO] Calentando modelo...")
    _prueba = np.zeros((480, 640, 3), dtype=np.uint8)
    try:
        reconocer_rostro(_prueba, "base_datos")
    except Exception:
        pass
    print("[INFO] Modelos listos.")
except ImportError:
    print("[AVISO] conocedor.py no encontrado.")
    def reconocer_rostro(frame, ruta_db="base_datos"):
        return "Modulo no encontrado"

# ── Configuración ─────────────────────────────────────────────────────
RUTA_DB = "base_datos"

# ── Colores BGR ───────────────────────────────────────────────────────
VERDE    = (0, 255, 136)
ROJO     = (51,  51, 255)
CIAN     = (255, 220, 0)
BLANCO   = (220, 220, 220)
GRIS     = (100, 100, 100)
NEGRO    = (0,   0,   0)
PANEL_BG = (22,  22,  26)


def dibujar_panel(frame, identidad, usuarios):
    #Dibuja el panel lateral derecho con info y controles
    h, w = frame.shape[:2]
    panel_w = 280

    # Fondo del panel
    cv2.rectangle(frame, (w - panel_w, 0), (w, h), PANEL_BG, -1)
    cv2.line(frame, (w - panel_w, 0), (w - panel_w, h), CIAN, 2)

    x = w - panel_w + 10
    y = 30

    # Título
    cv2.putText(frame, "FACEGUARD", (x, y),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, CIAN, 2)
    y += 20
    cv2.putText(frame, "Sistema de Acceso", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, GRIS, 1)
    y += 20
    cv2.line(frame, (x, y), (w - 10, y), GRIS, 1)
    y += 20

    # Identidad
    cv2.putText(frame, "IDENTIDAD:", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, GRIS, 1)
    y += 22

    conocido = identidad not in [
        "DESCONOCIDO", "Buscando rostro...", "Buscando...",
        "Iniciando...", "Modulo no encontrado", "Error"
    ]
    color_id = VERDE if conocido else (ROJO if identidad == "DESCONOCIDO" else BLANCO)
    cv2.putText(frame, identidad[:20], (x, y),
                cv2.FONT_HERSHEY_DUPLEX, 0.6, color_id, 2)
    y += 22

    estado_txt = "ACCESO AUTORIZADO" if conocido else ("ACCESO DENEGADO" if identidad == "DESCONOCIDO" else identidad)
    cv2.putText(frame, estado_txt, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, color_id, 1)
    y += 25
    cv2.line(frame, (x, y), (w - 10, y), GRIS, 1)
    y += 18

    # Usuarios registrados
    cv2.putText(frame, "USUARIOS REGISTRADOS:", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, CIAN, 1)
    y += 18
    if usuarios:
        for u in usuarios[:8]:  # máximo 8 en pantalla
            cv2.putText(frame, f"  > {u.upper()}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, BLANCO, 1)
            y += 16
    else:
        cv2.putText(frame, "  (vacia)", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, GRIS, 1)
        y += 16

    y += 10
    cv2.line(frame, (x, y), (w - 10, y), GRIS, 1)
    y += 18

    # Controles
    cv2.putText(frame, "CONTROLES:", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, CIAN, 1)
    y += 18
    controles = [
        "[R] Registrar usuario",
        "[E] Eliminar usuario",
        "[Q] Salir",
    ]
    for c in controles:
        cv2.putText(frame, c, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, BLANCO, 1)
        y += 16

    # Aviso ético
    y = h - 40
    cv2.line(frame, (x, y), (w - 10, y), GRIS, 1)
    y += 14
    cv2.putText(frame, "Solo rostros con", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, GRIS, 1)
    y += 13
    cv2.putText(frame, "consentimiento explicito.", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, GRIS, 1)

    return frame


def obtener_usuarios():
    if not os.path.exists(RUTA_DB):
        return []
    return [d for d in os.listdir(RUTA_DB) if os.path.isdir(os.path.join(RUTA_DB, d))]


def registrar_usuario(cap):
    #Flujo de registro por consola + captura con la cámara.
    print("\n=== REGISTRAR NUEVO USUARIO ===")
    nombre = input("Nombre del usuario: ").strip().lower().replace(" ", "_")
    if not nombre:
        print("[!] Nombre vacío. Cancelado.")
        return

    print(f"\n¿La persona '{nombre.upper()}' está presente y da su CONSENTIMIENTO")
    print("explícito para almacenar su rostro en este sistema? (s/n): ", end="")
    resp = input().strip().lower()
    if resp != "s":
        print("[!] Sin consentimiento. Registro cancelado.")
        return

    carpeta = os.path.join(RUTA_DB, nombre)
    os.makedirs(carpeta, exist_ok=True)

    print(f"\n[INFO] Se tomarán 5 fotos. Pide al usuario distintos ángulos.")
    print("[INFO] Presiona ESPACIO para capturar cada foto, Q para cancelar.")

    guardadas = 0
    ventana = "Captura - " + nombre.upper()
    while guardadas < 5:
        ret, frame = cap.read()
        if not ret:
            break
        info = frame.copy()
        cv2.putText(info, f"Foto {guardadas+1}/5 — ESPACIO para capturar, Q para cancelar",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, CIAN, 2)
        cv2.imshow(ventana, info)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            ruta = os.path.join(carpeta, f"{nombre}_{guardadas+1}.jpg")
            cv2.imwrite(ruta, frame)
            guardadas += 1
            print(f"  Foto {guardadas} guardada.")
        elif key == ord('q'):
            break

    cv2.destroyWindow(ventana)
    print(f"[OK] {guardadas} foto(s) guardadas para '{nombre.upper()}'.")


def eliminar_usuario():
    #Elimina un usuario de la base de datos.
    usuarios = obtener_usuarios()
    if not usuarios:
        print("[!] No hay usuarios registrados.")
        return
    print("\n=== ELIMINAR USUARIO ===")
    print("Usuarios:", ", ".join(u.upper() for u in usuarios))
    nombre = input("Nombre a eliminar: ").strip().lower().replace(" ", "_")
    carpeta = os.path.join(RUTA_DB, nombre)
    if not os.path.exists(carpeta):
        print(f"[!] No existe '{nombre.upper()}'.")
        return
    print(f"¿Eliminar todos los datos de '{nombre.upper()}'? (s/n): ", end="")
    if input().strip().lower() == "s":
        shutil.rmtree(carpeta)
        print(f"[OK] Usuario '{nombre.upper()}' eliminado.")
    else:
        print("[!] Cancelado.")


# ── Loop principal ────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara.")
        return

    identidad   = "Iniciando..."
    usuarios    = obtener_usuarios()
    contador    = 0

    print("[INFO] Sistema iniciado. R=Registrar, E=Eliminar, Q=Salir")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Reconocimiento cada 15 frames
        if contador % 15 == 0:
            try:
                identidad = reconocer_rostro(frame, RUTA_DB)
                usuarios  = obtener_usuarios()
            except Exception:
                identidad = "Error"
        contador += 1

        # Borde de color según estado
        conocido = identidad not in [
            "DESCONOCIDO", "Buscando rostro...", "Buscando...",
            "Iniciando...", "Modulo no encontrado", "Error"
        ]
        color_borde = VERDE if conocido else (ROJO if identidad == "DESCONOCIDO" else GRIS)

        # Añadir espacio para el panel
        h, w = frame.shape[:2]
        canvas = np.zeros((h, w + 280, 3), dtype=np.uint8)
        canvas[:, :w] = frame
        cv2.rectangle(canvas, (0, 0), (w - 1, h - 1), color_borde, 3)

        canvas = dibujar_panel(canvas, identidad, usuarios)
        cv2.imshow("FaceGuard — Sistema de Acceso", canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            cv2.destroyAllWindows()
            registrar_usuario(cap)
        elif key == ord('e'):
            cv2.destroyAllWindows()
            eliminar_usuario()

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Sistema cerrado.")


if __name__ == "__main__":
    main()