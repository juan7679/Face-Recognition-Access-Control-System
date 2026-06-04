
import cv2
import os
import shutil
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from conocedor import reconocer_rostro
from captura import registrar_usuario_automatico

# ── Cargar módulo del compañero ───────────────────────────────────────
print("Iniciando sistema, por favor espere...")
try:
    from conocedor import reconocer_rostro
    print("Modelos listos.")
except ImportError:
    print("conocedor.py no encontrado.")
    def reconocer_rostro(frame, ruta_db="base_datos"):
        return "Modulo no encontrado"

# ── Configuración ─────────────────────────────────────────────────────
RUTA_DB  = "base_datos"
PANEL_W  = 300
CAM_W    = 640
CAM_H    = 480

# ── Colores RGB (Pillow usa RGB, OpenCV BGR) ──────────────────────────
C_BG       = (13,  13,  15)
C_PANEL    = (20,  20,  25)
C_CARD     = (28,  28,  36)
C_BORDER   = (42,  42,  55)
C_CYAN     = (0,   210, 255)
C_GREEN    = (0,   230, 140)
C_RED      = (255, 60,  80)
C_WHITE    = (220, 220, 230)
C_GRAY     = (110, 110, 140)
C_ACCENT2  = (140, 80,  255)

# ── Fuentes ───────────────────────────────────────────────────────────
def cargar_fuente(size):
    """Intenta cargar una fuente del sistema, si no usa la default."""
    rutas = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
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


def texto(draw, txt, pos, fuente, color, centrado=False, max_w=None):
    #Dibuja texto con soporte de centrado.
    if centrado and max_w:
        bbox = draw.textbbox((0, 0), txt, font=fuente)
        tw = bbox[2] - bbox[0]
        pos = (pos[0] + (max_w - tw) // 2, pos[1])
    draw.text(pos, txt, font=fuente, fill=color)


def linea_h(draw, x1, y, x2, color=C_BORDER):
    draw.line([(x1, y), (x2, y)], fill=color, width=1)


def rect_redondeado(draw, x1, y1, x2, y2, r, color):
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=r, fill=color)


def dibujar_panel(img_pil, identidad, usuarios):
    #Dibuja el panel lateral con Pillow.
    draw = ImageDraw.Draw(img_pil)
    W    = CAM_W + PANEL_W
    H    = CAM_H
    px   = CAM_W + 12  # margen izquierdo del panel
    pw   = PANEL_W - 14

    # Fondo panel
    draw.rectangle([(CAM_W, 0), (W, H)], fill=C_PANEL)
    draw.line([(CAM_W, 0), (CAM_W, H)], fill=C_CYAN, width=2)

    y = 16

    # ── Título ──
    texto(draw, "FaceGuard", (px, y), F_TITLE, C_CYAN)
    y += 30
    texto(draw, "Sistema de Reconocimiento Facial", (px, y), F_SMALL, C_GRAY)
    y += 18
    linea_h(draw, px, y, CAM_W + PANEL_W - 12)
    y += 14

    # ── Identidad ──
    texto(draw, "IDENTIDAD DETECTADA", (px, y), F_LABEL, C_CYAN)
    y += 16

    conocido = identidad not in [
        "DESCONOCIDO", "Buscando rostro...", "Buscando...",
        "Iniciando...", "Modulo no encontrado", "Error"
    ]
    color_id = C_GREEN if conocido else (C_RED if identidad == "DESCONOCIDO" else C_WHITE)

    # Tarjeta de identidad
    rect_redondeado(draw, px - 4, y, px + pw + 4, y + 58, 8, C_CARD)
    nombre_txt = identidad[:18] if len(identidad) > 18 else identidad
    texto(draw, nombre_txt, (px + 4, y + 6), F_NAME, color_id)

    estado_txt = "Acceso autorizado" if conocido else ("Acceso denegado" if identidad == "DESCONOCIDO" else f"   {identidad}")
    texto(draw, estado_txt, (px + 4, y + 36), F_NORMAL, color_id)
    y += 68

    linea_h(draw, px, y, CAM_W + PANEL_W - 12)
    y += 14

    # ── Usuarios ──
    texto(draw, "USUARIOS REGISTRADOS", (px, y), F_LABEL, C_CYAN)
    y += 16

    rect_redondeado(draw, px - 4, y, px + pw + 4, y + max(len(usuarios), 1) * 20 + 10, 8, C_CARD)
    y += 6
    if usuarios:
        for u in usuarios[:8]:
            texto(draw, f"  ▸  {u.upper()}", (px + 4, y), F_NORMAL, C_WHITE)
            y += 20
    else:
        texto(draw, "   (base de datos vacía)", (px + 4, y), F_NORMAL, C_GRAY)
        y += 20
    y += 10

    linea_h(draw, px, y, CAM_W + PANEL_W - 12)
    y += 14

    # ── Controles ──
    texto(draw, "CONTROLES", (px, y), F_LABEL, C_CYAN)
    y += 16

    controles = [
        ("R", "Registrar usuario", C_ACCENT2),
        ("E", "Eliminar usuario",  C_RED),
        ("Q", "Salir",             C_GRAY),
    ]
    for tecla, desc, color_t in controles:
        rect_redondeado(draw, px - 4, y, px + 22, y + 20, 4, color_t)
        texto(draw, tecla, (px + 4, y + 3), F_SMALL, C_BG)
        texto(draw, desc,  (px + 30, y + 3), F_NORMAL, C_WHITE)
        y += 26

    # ── Footer ético ──
    y = H - 36
    linea_h(draw, px, y, CAM_W + PANEL_W - 12, C_BORDER)
    y += 8
    texto(draw, "Solo rostros con consentimiento", (px, y), F_LABEL, C_GRAY)
    y += 13
    texto(draw, "   explícito del usuario retratado.", (px, y), F_LABEL, C_GRAY)

    return img_pil


def frame_a_pil(frame):
    #Convierte frame BGR de OpenCV a imagen Pillow RGB.
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


def pil_a_frame(img_pil):
    #Convierte imagen Pillow RGB a frame BGR de OpenCV.
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def obtener_usuarios():
    if not os.path.exists(RUTA_DB):
        return []
    return [d for d in os.listdir(RUTA_DB) if os.path.isdir(os.path.join(RUTA_DB, d))]
    print("\n=== REGISTRAR NUEVO USUARIO ===")
    nombre = input("Nombre del usuario: ").strip().lower().replace(" ", "_")
    if not nombre:
        print("Nombre vacío. Cancelado.")
        return

    print(f"\n¿La persona '{nombre.upper()}' está presente y da su CONSENTIMIENTO")
    print("explícito para almacenar su rostro en este sistema? (s/n): ", end="")
    if input().strip().lower() != "s":
        print("Sin consentimiento. Registro cancelado.")
        return

    carpeta = os.path.join(RUTA_DB, nombre)
    os.makedirs(carpeta, exist_ok=True)

    print(f"\nSe tomarán 5 fotos. Presiona ESPACIO para capturar, Q para cancelar.")

    guardadas = 0
    ventana   = "Captura del usuario " + nombre.upper()
    while guardadas < 5:
        ret, frame = cap.read()
        if not ret:
            break
        # Overlay en la ventana de captura
        img  = frame_a_pil(frame)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (CAM_W, 40)], fill=(0, 0, 0, 180))
        texto(draw, f"Foto {guardadas+1}/5  —  ESPACIO: capturar  |  Q: cancelar",
              (10, 10), F_NORMAL, C_CYAN)
        cv2.imshow(ventana, pil_a_frame(img))

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            cv2.imwrite(os.path.join(carpeta, f"{nombre}_{guardadas+1}.jpg"), frame)
            guardadas += 1
            print(f"  ✔ Foto {guardadas} guardada.")
        elif key == ord('q'):
            break

    cv2.destroyWindow(ventana)
    print(f"[OK] {guardadas} foto(s) guardadas para '{nombre.upper()}'.")


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
        print(f"[!] No existe '{nombre.upper()}'.")
        return
    print(f"¿Eliminar todos los datos de '{nombre.upper()}'? (s/n): ", end="")
    if input().strip().lower() == "s":
        shutil.rmtree(carpeta)
        print(f"El Usuario '{nombre.upper()}'se elimino correctamente.")
    else:
        print("!!Cancelado!!.")


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR No se pudo abrir la cámara.")
        return

    identidad = "Iniciando..."
    usuarios  = obtener_usuarios()
    contador  = 0

    print("Sistema iniciado. R=Registrar, E=Eliminar, Q=Salir")

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

        conocido    = identidad not in [
            "DESCONOCIDO", "Buscando rostro...", "Buscando...",
            "Iniciando...", "Modulo no encontrado", "Error"
        ]
        color_borde = C_GREEN if conocido else (C_RED if identidad == "DESCONOCIDO" else (80, 80, 80))

        # Canvas con panel
        canvas_cv = np.zeros((CAM_H, CAM_W + PANEL_W, 3), dtype=np.uint8)
        canvas_cv[:CAM_H, :CAM_W] = cv2.resize(frame, (CAM_W, CAM_H))

        # Borde coloreado en el video
        cv2.rectangle(canvas_cv, (0, 0), (CAM_W - 1, CAM_H - 1),
                      tuple(reversed(color_borde)), 3)

        # Pasar a Pillow para dibujar el panel
        img_pil = frame_a_pil(canvas_cv)
        img_pil = dibujar_panel(img_pil, identidad, usuarios)
        canvas_cv = pil_a_frame(img_pil)

        cv2.imshow("Sistema de Acceso con Reconocimiento Facial", canvas_cv)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('r'):

            cv2.destroyAllWindows()

            nombre = input(
            "\nNombre del usuario: "
            ).strip().lower().replace(" ", "_")

            if nombre:

                print(
                    f"\n¿La persona '{nombre.upper()}' autoriza almacenar su rostro? (s/n): ",
                    end=""
                )

            consentimiento = input().strip().lower()

            if consentimiento == "s":

                registrar_usuario_automatico(nombre, cap)

                usuarios = obtener_usuarios()

            else:

                print(
                "Registro cancelado por falta de consentimiento."
                )

        elif key == ord('e'):
            cv2.destroyAllWindows()

            eliminar_usuario()

    time.sleep(2)
    print("Sistema cerrado.")
    

if __name__ == "__main__":
    main()