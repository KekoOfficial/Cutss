from flask import Flask, render_template, request, jsonify
import os
import threading
import queue
import subprocess
from core.cortar import extraer_segmento
from core.enviar_whatsapp import enviar_codigo_al_usuario, despachar_a_whatsapp
import config

app = Flask(__name__)

# Carpetas de trabajo
INPUT_FOLDER = config.INPUT_FOLDER
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(config.TEMP_FOLDER, exist_ok=True)

# Estados del sistema
PROCESANDO = False
ESPERANDO_CODIGO = False
cola = queue.Queue()

class MallyLogger:
    def __init__(self, nombre, total):
        self.nombre = nombre.strip().upper()
        self.total = total

    def exito(self, n):
        return (f"🎬 {self.nombre}\n"
                f"💎 PARTE: {n} / {self.total}\n"
                f"✅ Contenido verificado y publicado\n"
                f"🔗 @MallyUmbrae")

# --- HILOS DE TRABAJO ---
def productor(ruta_video, total_partes, log):
    """Corta el video en fragmentos y los agrega a la cola"""
    for n in range(1, total_partes + 1):
        print(f"⚡ Cortando parte {n}/{total_partes}")
        ruta_parte = extraer_segmento(ruta_video, n, total_partes)
        if os.path.exists(ruta_parte):
            cola.put({
                'numero_parte': n,
                'ruta_archivo': ruta_parte,
                'mensaje': log.exito(n)
            })
    cola.put(None) # Marcador de fin de proceso

def consumidor():
    """Toma los fragmentos de la cola y los publica automáticamente"""
    while True:
        elemento = cola.get()
        if elemento is None:
            break
        print(f"📤 Enviando parte {elemento['numero_parte']}")
        ok = despachar_a_whatsapp(elemento['ruta_archivo'], elemento['mensaje'])
        if ok:
            print(f"✅ Parte {elemento['numero_parte']} publicada correctamente")
        # Eliminamos el archivo temporal
        if os.path.exists(elemento['ruta_archivo']):
            os.remove(elemento['ruta_archivo'])
        cola.task_done()

# --- RUTAS DE LA APLICACIÓN WEB ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/solicitar-codigo", methods=["POST"])
def solicitar_codigo():
    """Cuando pedís el código, nosotros te lo enviamos a tu WhatsApp"""
    global ESPERANDO_CODIGO

    if ESPERANDO_CODIGO:
        return jsonify({
            "estado": "ocupado",
            "mensaje": "Ya te enviamos un código, revisá tus mensajes"
        })

    # Enviamos el código a tu número
    exito, mensaje = enviar_codigo_al_usuario()

    if exito:
        ESPERANDO_CODIGO = True
        return jsonify({
            "estado": "ok",
            "mensaje": mensaje
        })
    else:
        return jsonify({
            "estado": "error",
            "mensaje": mensaje
        })

@app.route("/procesar", methods=["POST"])
def procesar():
    global PROCESANDO, ESPERANDO_CODIGO

    if PROCESANDO:
        return jsonify({
            "estado": "ocupado",
            "mensaje": "⏳ Ya estoy trabajando en tu contenido, esperá..."
        })

    # Recibimos los datos que ingresaste
    codigo_ingresado = request.form.get("codigo", "").strip()
    archivo_video = request.files.get("video")
    titulo_contenido = request.form.get("titulo", "SIN TÍTULO")

    # Verificaciones
    if not codigo_ingresado:
        return jsonify({"estado": "error", "mensaje": "Ingresá el código que te enviamos"})
    
    # Comprobamos que el código sea el mismo que te mandamos
    if not config.verificar_codigo_ingresado(codigo_ingresado):
        return jsonify({"estado": "error", "mensaje": "❌ Código incorrecto. Usá el que te enviamos a tu WhatsApp"})

    if not archivo_video:
        return jsonify({"estado": "error", "mensaje": "Seleccioná el video que querés procesar"})

    # Guardamos el video original
    ruta_entrada = os.path.join(INPUT_FOLDER, archivo_video.filename)
    archivo_video.save(ruta_entrada)

    PROCESANDO = True
    ESPERANDO_CODIGO = False

    def proceso_completo():
        global PROCESANDO

        # Calculamos la duración total y la cantidad de partes
        resultado = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', ruta_entrada
        ], capture_output=True, text=True)

        duracion_total = float(resultado.stdout)
        cantidad_partes = int(duracion_total // config.CLIP_DURATION) + 1

        registro = MallyLogger(titulo_contenido, cantidad_partes)

        print(f"🚀 Iniciando procesamiento: {titulo_contenido} | Total de partes: {cantidad_partes}")

        # Ejecutamos cortado y publicación al mismo tiempo
        hilo_cortar = threading.Thread(target=productor, args=(ruta_entrada, cantidad_partes, registro))
        hilo_publicar = threading.Thread(target=consumidor)

        hilo_cortar.start()
        hilo_publicar.start()

        hilo_cortar.join()
        hilo_publicar.join()

        # Limpiamos archivos
        if os.path.exists(ruta_entrada):
            os.remove(ruta_entrada)

        PROCESANDO = False
        print("✅ PROCESO FINALIZADO - TODOS LOS ESTADOS PUBLICADOS")

    # Iniciamos el trabajo en segundo plano
    threading.Thread(target=proceso_completo, daemon=True).start()

    return jsonify({
        "estado": "ok",
        "mensaje": f"✅ Código correcto. Se están procesando y publicando {cantidad_partes} partes automáticamente"
    })

if __name__ == "__main__":
    print("="*60)
    print("🌑 UMBRAE CUTS - SISTEMA INICIADO")
    print("📱 Número configurado: " + config.NUMERO_USUARIO)
    print("✉️ Nosotros te enviamos el código de verificación")
    print("="*60)
    app.run(host="0.0.0.0", port=5000, debug=False)
