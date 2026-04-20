# ==========================================
# UMBRAE CUTS - SISTEMA PRINCIPAL
# ✅ Corta videos 60s | ✅ Nombra archivos | ✅ Publica automático
# ✅ Interfaz web | ✅ Conexión WhatsApp
# ==========================================

from flask import Flask, render_template, request, jsonify
from whatsapp_api import WhatsAppAPI
from moviepy.editor import VideoFileClip
import os
import random
import string

# Inicializar aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'umbrae_cuts_2024'

# Carpetas de trabajo
CARPETA_ENTRADA = "videos_entrada"
CARPETA_SALIDA = "videos_salida"

# Crear carpetas si no existen
os.makedirs(CARPETA_ENTRADA, exist_ok=True)
os.makedirs(CARPETA_SALIDA, exist_ok=True)

# Inicializar API de WhatsApp
whatsapp = WhatsAppAPI()

# Variable global para guardar lista de archivos generados
archivos_generados = []

# ==========================================
# RUTAS PRINCIPALES
# ==========================================

@app.route('/')
def index():
    """Cargar interfaz principal"""
    return render_template('index.html')

# ==========================================
# FUNCIÓN DE CORTE DE VIDEOS
# ==========================================

@app.route('/cortar-video', methods=['POST'])
def cortar_video():
    global archivos_generados
    archivos_generados.clear()

    try:
        # Recibir el archivo enviado desde la web
        archivo = request.files['video']
        if not archivo:
            return jsonify({
                "exito": False,
                "mensaje": "No se recibió ningún archivo"
            })

        # Guardar video original
        ruta_original = os.path.join(CARPETA_ENTRADA, archivo.filename)
        archivo.save(ruta_original)

        # Cargar video con MoviePy
        video = VideoFileClip(ruta_original)
        duracion_total = int(video.duration)
        duracion_fragmento = 60  # 60 segundos exactos
        cantidad_fragmentos = duracion_total // duracion_fragmento
        resto = duracion_total % duracion_fragmento

        # Si el video es más corto de 60s, lo guardamos como un solo fragmento
        if cantidad_fragmentos == 0:
            cantidad_fragmentos = 1
            resto = 0

        print(f"📹 Duración total: {duracion_total}s")
        print(f"✂️ Se generarán {cantidad_fragmentos} fragmentos de 60s")

        # Cortar el video
        numero = 1
        tiempo_inicio = 0

        while tiempo_inicio < duracion_total:
            # Definir tiempo final del fragmento
            tiempo_final = tiempo_inicio + duracion_fragmento

            # Si es el último fragmento y sobra tiempo, ajustamos
            if tiempo_final > duracion_total:
                tiempo_final = duracion_total

            # Crear fragmento
            fragmento = video.subclip(tiempo_inicio, tiempo_final)

            # Nombre del archivo según lo pedido: 1.mp4, 2.mp4... hasta 0000.mp4 al final
            if numero == cantidad_fragmentos and resto == 0:
                nombre_archivo = "0000.mp4"
            else:
                nombre_archivo = f"{numero}.mp4"

            ruta_salida = os.path.join(CARPETA_SALIDA, nombre_archivo)

            # Guardar fragmento con calidad alta
            fragmento.write_videofile(
                ruta_salida,
                codec="libx264",
                audio_codec="aac",
                bitrate="8000k",  # Calidad alta 4K/HD
                fps=30,
                threads=4,
                verbose=False,
                logger=None
            )

            # Agregar a la lista
            archivos_generados.append(nombre_archivo)
            print(f"✅ Generado: {nombre_archivo}")

            # Liberar memoria
            fragmento.close()

            # Pasar al siguiente
            tiempo_inicio = tiempo_final
            numero += 1

        # Cerrar video original
        video.close()

        # Generar código temporal de 8 dígitos para mostrar al usuario
        codigo_temporal = ''.join(random.choices(string.digits, k=8))

        return jsonify({
            "exito": True,
            "cantidad": cantidad_fragmentos,
            "archivos": archivos_generados,
            "codigo_temporal": codigo_temporal,
            "mensaje": "Video cortado correctamente"
        })

    except Exception as e:
        return jsonify({
            "exito": False,
            "mensaje": f"Error al procesar: {str(e)}"
        })

# ==========================================
# FUNCIÓN DE PUBLICACIÓN AUTOMÁTICA
# ==========================================

@app.route('/publicar-estados', methods=['POST'])
def publicar_estados():
    global archivos_generados

    try:
        # Recibir código ingresado por el usuario
        datos = request.get_json()
        codigo_ingresado = datos.get('codigo', '')

        if not codigo_ingresado or len(codigo_ingresado) != 8:
            return jsonify({
                "exito": False,
                "mensaje": "El código debe tener exactamente 8 dígitos"
            })

        if not archivos_generados:
            return jsonify({
                "exito": False,
                "mensaje": "No hay videos preparados para publicar"
            })

        # Conectar con WhatsApp
        estado_conexion = whatsapp.iniciar_sesion()
        print(f"🔌 {estado_conexion}")

        # Verificar código
        valido, mensaje = whatsapp.verificar_codigo(codigo_ingresado)
        if not valido:
            return jsonify({
                "exito": False,
                "mensaje": mensaje
            })

        # Publicar cada video automáticamente
        publicados = 0
        errores = 0

        for nombre_archivo in archivos_generados:
            ruta_completa = os.path.join(CARPETA_SALIDA, nombre_archivo)
            print(f"📤 Publicando: {nombre_archivo}")

            resultado, detalle = whatsapp.publicar_estado(ruta_completa)
            
            if resultado:
                publicados += 1
                print(f"✅ Publicado correctamente: {nombre_archivo}")
            else:
                errores += 1
                print(f"❌ Error al publicar {nombre_archivo}: {detalle}")

        # Resumen final
        return jsonify({
            "exito": True,
            "publicados": publicados,
            "errores": errores,
            "mensaje": f"Proceso finalizado. {publicados} estados publicados correctamente."
        })

    except Exception as e:
        return jsonify({
            "exito": False,
            "mensaje": f"Error en la publicación: {str(e)}"
        })

# ==========================================
# LIMPIEZA DE ARCHIVOS TEMPORALES
# ==========================================

@app.route('/limpiar', methods=['POST'])
def limpiar_archivos():
    """Elimina los archivos generados para liberar espacio"""
    try:
        # Borrar archivos de entrada
        for archivo in os.listdir(CARPETA_ENTRADA):
            ruta = os.path.join(CARPETA_ENTRADA, archivo)
            if os.path.isfile(ruta):
                os.remove(ruta)

        # Borrar archivos de salida
        for archivo in os.listdir(CARPETA_SALIDA):
            ruta = os.path.join(CARPETA_SALIDA, archivo)
            if os.path.isfile(ruta):
                os.remove(ruta)

        archivos_generados.clear()

        return jsonify({
            "exito": True,
            "mensaje": "Archivos eliminados correctamente"
        })

    except Exception as e:
        return jsonify({
            "exito": False,
            "mensaje": f"Error al limpiar: {str(e)}"
        })

# ==========================================
# EJECUTAR APLICACIÓN
# ==========================================

if __name__ == '__main__':
    print("="*60)
    print("🌑 UMBRAE CUTS - SISTEMA INICIADO")
    print("✅ Cortador de videos 60s")
    print("✅ Nomenclatura automática")
    print("✅ Publicación automática WhatsApp")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)
