import time
import os
import config
from whatsapp_api import WhatsAppAPI

# Inicializamos la conexión con WhatsApp
whatsapp = WhatsAppAPI()
sesion_conectada = False

def enviar_codigo_al_usuario():
    """NOSOTROS TE ENVIAMOS EL CÓDIGO A TU WHATSAPP"""
    global sesion_conectada

    # Si no estamos conectados, iniciamos sesión
    if not sesion_conectada:
        print("🔄 Conectando con WhatsApp Web...")
        exito, mensaje = whatsapp.iniciar_sesion()
        if not exito:
            print(f"❌ Error de conexión: {mensaje}")
            return False, mensaje
        sesion_conectada = True
        print("✅ Conexión establecida")

    # Generamos el código y lo guardamos
    codigo = config.generar_y_guardar_codigo()

    # El mensaje que te va a llegar
    mensaje = f"""🔐 *CÓDIGO DE VERIFICACIÓN - UMBRAE CUTS*

Tu código de acceso es: *{codigo}*

Ingresá este código en la aplicación para confirmar y empezar a procesar tus videos.

🔒 Código válido por 10 minutos
🔗 @MallyUmbrae
"""

    # Te enviamos el mensaje a tu número
    enviado, detalle = whatsapp.enviar_mensaje(config.NUMERO_USUARIO, mensaje)
    
    if enviado:
        print(f"✅ CÓDIGO {codigo} ENVIADO CORRECTAMENTE A {config.NUMERO_USUARIO}")
        return True, "Código enviado a tu WhatsApp, revisá tus mensajes"
    else:
        print(f"❌ No se pudo enviar el código: {detalle}")
        return False, f"No se pudo enviar el código: {detalle}"

def despachar_a_whatsapp(path_archivo, texto_descripcion):
    """Publica los videos cortados como estados de WhatsApp"""
    for intento in range(1, config.MAX_RETRIES + 1):
        try:
            if not os.path.exists(path_archivo):
                print(f"❌ Archivo no encontrado: {path_archivo}")
                return False

            print(f"📤 Publicando: {os.path.basename(path_archivo)}")
            resultado, detalle = whatsapp.publicar_estado(path_archivo, texto_descripcion)
            
            if resultado:
                print(f"✅ Publicado exitosamente: {os.path.basename(path_archivo)}")
                return True
            else:
                raise Exception(detalle)

        except Exception as e:
            error = str(e)
            print(f"⚠️ Intento {intento} fallido: {error}")
            if intento < config.MAX_RETRIES:
                time.sleep(5)
            else:
                print(f"❌ Falló después de {config.MAX_RETRIES} intentos")
                return False
