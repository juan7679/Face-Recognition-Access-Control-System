"""
interfaz.py — Interfaz del sistema de reconocimiento facial
Requiere: conocedor.py, captura.py, detector.py en la misma carpeta
Dependencias: pip install deepface opencv-python numpy tf-keras tensorflow Pillow mtcnn
"""

import cv2
import os
import shutil
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

print("Iniciando sistema, por favor espere...")
try:
    from conocedor import reconocer_rostro
except ImportError:
    print("conocedor.py no encontrado.")
    def reconocer_rostro(frame, ruta_db="base_datos"):
        return "Modulo no encontrado"

try:
    from captura import registrar_usuario_automatico
except ImportError:
    print("captura.py no encontrado.")
    def registrar_usuario_automatico(nombre, cap):
        print("Funcion de captura no disponible.")

# ── Configuración ─────────────────────────────────────────────────────
RUTA_DB = "base_datos"
PANEL_W = 300
CAM_W   = 640
CAM_H   = 480

# ── Colores RGB ───────────────────────────────────────────────────────
C_BG     = (13,  13,  15)
C_PANEL  = (20,  20,  25)
C_CARD   = (28,  28,  36)
C_BORDER = (42,  42,  55)
C_CYAN   = (0,   210, 255)
C_GREEN  = (0,   230, 140)
C_RED    = (255, 60,  80)
C_WHITE  = (220, 220, 230)
C_GRAY   = (110, 110, 140)
C_ACCENT2= (140, 80,  255)

# ── Fuentes ───────────────────────────────────────────────────────────
def cargar_fuente(size):
    rutas = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for r in rutas:
        if os.path.exists(r):
            try:
                return ImageFont.truetype(r, size)
            except Exception:
                continue
    return ImageFont.load_default()

F_TITLE  = cargar_fuente(22)
F_NAME   = cargar_fuente(26)
F_NORMAL = cargar_fuente(14)
F_SMALL  = cargar_fuente(12)
F_LABEL  = cargar_fuente(11)

# ── Helpers de dibujo ─────────────────────────────────────────────────
def texto(draw, txt, pos, fuente, color):
    draw.text(pos, txt, font=fuente, fill=color)

def linea_h(draw, x1, y, x2, color=C_BORDER):
    draw.line([(x1, y), (x2, y)], fill=color, width=1)

def rect_redondeado(draw, x1, y1, x2, y2, r, color):
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=r, fill=color)

# ── Panel lateral ─────────────────────────────────────────────────────
def dibujar_panel(img_pil, identidad, usuarios):
    draw = ImageDraw.Draw(img_pil)
    px   = CAM_W + 12
    pw   = PANEL_W - 14
    H    = CAM_H

    draw.rectangle([(CAM_W, 0), (CAM_W + PANEL_W, H)], fill=C_PANEL)
    draw.line([(CAM_W, 0), (CAM_W, H)], fill=C_CYAN, width=2)

    y = 16
    texto(draw, "FaceGuard", (px, y), F_TITLE, C_CYAN)
    y += 30
    texto(draw, "Sistema de Reconocimiento Facial", (px, y), F_SMALL, C_GRAY)
    y += 18
    linea_h(draw, px, y, CAM_W + PANEL_W - 12)
    y += 14

    texto(draw, "IDENTIDAD DETECTADA", (px, y), F_LABEL, C_CYAN)
    y += 16

    conocido = identidad not in [
        "DESCONOCIDO", "Buscando rostro...", "Buscando...",
        "Iniciando...", "Modulo no encontrado", "Error"
    ]
    color_id  = C_GREEN if conocido else (C_RED if identidad == "DESCONOCIDO" else C_WHITE)
    estado_txt = "Acceso autorizado" if conocido else ("Acceso denegado" if identidad == "DESCONOCIDO" else identidad)

    rect_redondeado(draw, px - 4, y, px + pw + 4, y + 58, 8, C_CARD)
    texto(draw, identidad[:18], (px + 4, y + 6),  F_NAME,   color_id)
    texto(draw, estado_txt,     (px + 4, y + 36), F_NORMAL, color_id)
    y += 68

    linea_h(draw, px, y, CAM_W + PANEL_W - 12)
    y += 14

    texto(draw, "USUARIOS REGISTRADOS", (px, y), F_LABEL, C_CYAN)
    y += 16
    rect_redondeado(draw, px - 4, y, px + pw + 4, y + max(len(usuarios), 1) * 20 + 10, 8, C_CARD)
    y += 6
    if usuarios:
        for u in usuarios[:8]:
            texto(draw, f"  ▸  {u.upper()}", (px + 4, y), F_NORMAL, C_WHITE)
            y += 20
    else:
        texto(draw, "   (base de datos vacia)", (px + 4, y), F_NORMAL, C_GRAY)
        y += 20
    y += 10

    linea_h(draw, px, y, CAM_W + PANEL_W - 12)
    y += 14

    texto(draw, "CONTROLES", (px, y), F_LABEL, C_CYAN)
    y += 16
    for tecla, desc, color_t in [("R", "Registrar usuario", C_ACCENT2),
                                   ("E", "Eliminar usuario",  C_RED),
                                   ("Q", "Salir",             C_GRAY)]:
        rect_redondeado(draw, px - 4, y, px + 22, y + 20, 4, color_t)
        texto(draw, tecla, (px + 4,  y + 3), F_SMALL,  C_BG)
        texto(draw, desc,  (px + 30, y + 3), F_NORMAL, C_WHITE)
        y += 26

    y = H - 36
    linea_h(draw, px, y, CAM_W + PANEL_W - 12, C_BORDER)
    y += 8
    texto(draw, "Solo rostros con consentimiento", (px, y), F_LABEL, C_GRAY)
    y += 13
    texto(draw, "explicito del usuario retratado.", (px, y), F_LABEL, C_GRAY)

    return img_pil

# ── Conversión OpenCV <-> Pillow ──────────────────────────────────────
def frame_a_pil(frame):
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

def pil_a_frame(img_pil):
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# ── Usuarios ──────────────────────────────────────────────────────────
def obtener_usuarios():
    if not os.path.exists(RUTA_DB):
        return []
    return [d for d in os.listdir(RUTA_DB) if os.path.isdir(os.path.join(RUTA_DB, d))]

def eliminar_usuario():
    usuarios = obtener_usuarios()
    if not usuarios:
        print("No hay usuarios registrados.")
        return
    print("\n=== ELIMINAR USUARIO ===")
    print("Usuarios:", ", ".join(u.upper() for u in usuarios))
    nombre  = input("Nombre a eliminar: ").strip().lower().replace(" ", "_")
    carpeta = os.path.join(RUTA_DB, nombre)
    if not os.path.exists(carpeta):
        print(f"No existe '{nombre.upper()}'.")
        return
    print(f"¿Eliminar todos los datos de '{nombre.upper()}'? (s/n): ", end="")
    if input().strip().lower() == "s":
        shutil.rmtree(carpeta)
        print(f"Usuario '{nombre.upper()}' eliminado correctamente.")
    else:
        print("Cancelado.")

# ── Loop principal ────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: No se pudo abrir la camara.")
        return

    identidad = "Iniciando..."
    usuarios  = obtener_usuarios()
    contador  = 0

    print("Sistema iniciado. R=Registrar, E=Eliminar, Q=Salir")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if contador % 15 == 0:
            try:
                identidad = reconocer_rostro(frame, RUTA_DB)
                usuarios  = obtener_usuarios()
            except Exception:
                identidad = "Error"
        contador += 1

        conocido    = identidad not in [
            "DESCONOCIDO", "Buscando rostro...", "Buscando...",
            "Iniciando...", "Modulo no encontrado", "Error"
        ]
        color_borde = C_GREEN if conocido else (C_RED if identidad == "DESCONOCIDO" else (80, 80, 80))

        canvas_cv = np.zeros((CAM_H, CAM_W + PANEL_W, 3), dtype=np.uint8)
        canvas_cv[:CAM_H, :CAM_W] = cv2.resize(frame, (CAM_W, CAM_H))
        cv2.rectangle(canvas_cv, (0, 0), (CAM_W - 1, CAM_H - 1),
                      tuple(reversed(color_borde)), 3)

        img_pil   = frame_a_pil(canvas_cv)
        img_pil   = dibujar_panel(img_pil, identidad, usuarios)
        canvas_cv = pil_a_frame(img_pil)

        cv2.imshow("Sistema de Acceso con Reconocimiento Facial", canvas_cv)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('r'):
            cv2.destroyAllWindows()
            nombre = input("\nNombre del usuario: ").strip().lower().replace(" ", "_")
            if nombre:
                print(f"\n¿La persona '{nombre.upper()}' autoriza almacenar su rostro? (s/n): ", end="")
                if input().strip().lower() == "s":
                    registrar_usuario_automatico(nombre, cap)
                    usuarios = obtener_usuarios()
                else:
                    print("Registro cancelado por falta de consentimiento.")
            else:
                print("Nombre vacio. Cancelado.")

        elif key == ord('e'):
            cv2.destroyAllWindows()
            eliminar_usuario()

    cap.release()
    cv2.destroyAllWindows()
    print("Sistema cerrado.")

if __name__ == "__main__":
    main()