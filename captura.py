import cv2
import os
import time

from detector import detectar_rostro

def registrar_usuario_automatico(nombre_usuario, camara):
    # Crear carpeta para almacenar las imágenes del usuario
    ruta_usuario = os.path.join("base_datos", nombre_usuario)

    if not os.path.exists(ruta_usuario):
        os.makedirs(ruta_usuario)


    # Verificar que la cámara se abrió correctamente
    if not camara.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        exit()

    # ==================================================
    # VARIABLES DE CONTROL
    # ==================================================

    contador = 0               # Número de imágenes guardadas
    ultimo_guardado = time.time()  # Tiempo de la última captura

    print("\nIniciando captura facial...")
    print("Presiona ESC para salir.")
    print("El sistema capturará automáticamente 20 imágenes.\n")

    # ==================================================
    # FUNCIÓN AUXILIAR
    # Devuelve el rostro recortado y redimensionado
    # ==================================================

    def obtener_rostro(frame):
        resultados = detectar_rostro(frame)
        
        if len(resultados) == 0:
            return None

        x, y, ancho, alto = resultados[0]['box']

        # Evitar coordenadas negativas
        x = max(0, x)
        y = max(0, y)

        cara = frame[y:y + alto, x:x + ancho]

        # Tamaño recomendado para FaceNet
        cara = cv2.resize(cara, (160, 160))

        return cara


    # ==================================================
    # BUCLE PRINCIPAL
    # ==================================================

    while True:

        # Capturar frame de la cámara
        ret, frame = camara.read()

        if not ret:
            continue

        # Detectar rostros
        resultados = detectar_rostro(frame)

        # Dibujar rectángulos sobre cada rostro detectado
        for rostro in resultados:

            x, y, ancho, alto = rostro['box']

            # Evitar coordenadas negativas
            x = max(0, x)
            y = max(0, y)

            cv2.rectangle(
                frame,
                (x, y),
                (x + ancho, y + alto),
                (0, 255, 0),
                2
            )

        # Mostrar contador en pantalla
        cv2.putText(
            frame,
            f"Capturas: {contador}/20",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Mostrar ventana
        cv2.imshow("Captura Facial", frame)

        # Leer teclado
        tecla = cv2.waitKey(1)

        # ==================================================
        # GUARDADO AUTOMÁTICO CADA 0.5 SEGUNDOS
        # ==================================================

        if len(resultados) > 0 and contador < 20:

            tiempo_actual = time.time()

            # Esperar medio segundo entre capturas
            if tiempo_actual - ultimo_guardado >= 0.5:

                rostro = resultados[0]

                x, y, ancho, alto = rostro['box']

                # Evitar coordenadas negativas
                x = max(0, x)
                y = max(0, y)

                # Recortar rostro
                cara = frame[y:y + alto, x:x + ancho]

                # Redimensionar para FaceNet
                cara = cv2.resize(cara, (160, 160))

                # Nombre del archivo
                archivo = os.path.join(
                    ruta_usuario,
                    f"rostro_{contador}.jpg"
                )

                # Guardar imagen
                cv2.imwrite(archivo, cara)

                contador += 1
                ultimo_guardado = tiempo_actual

                print(f"Captura {contador}/20 guardada")

        # ==================================================
        # FINALIZAR AL COMPLETAR 20 IMÁGENES
        # ==================================================

        if contador >= 20:
            print("\nCaptura finalizada correctamente.")
            print(f"Las imágenes fueron guardadas en: {ruta_usuario}")
            break

        # ==================================================
        # SALIR CON ESC
        # ==================================================

        if tecla == 27:
            print("\nCaptura cancelada por el usuario.")
            break

    # ==================================================
    # LIBERAR RECURSOS
    # ==================================================
    cv2.destroyAllWindows()
    