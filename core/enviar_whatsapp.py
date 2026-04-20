import time
import os
import config
from whatsapp_api import WhatsAppAPI

# Inicializamos la conexión
whatsapp = WhatsAppAPI()
sesion_iniciada = False

def despachar_a_whatsapp(path_archivo, mensaje):
    """
    Publica el video como estado de WhatsApp con sistema de reintentos
    """
    global sesion_iniciada

    # Iniciar sesión solo la primera vez
    if not sesion_iniciada:
        print("🔑 Conectando con WhatsApp...")
        exito, mensaje_sesion = whatsapp.iniciar_sesion()
        if not exito:
            print(f"❌ Error de conexión: {mensaje_sesion}")
            return False
        
        # Generar y enviar código al usuario
        codigo = config.generar_codigo()
        print(f"📩 Enviando código {codigo} al número {config.NUMERO_USUARIO}")
        enviado = whatsapp.enviar_mensaje(
            config.NUMERO_USUARIO, 
            f"🔐 Código de verificación Umbrae Cuts:\n\n{codigo}\n\nIngresá este código en la aplicación para empezar."
        )

        if not enviado:
            print(f"❌ No se pudo enviar el código")
            return False
        
        sesion_iniciada = True
        print("✅ Código enviado correctamente")

    # Sistema de reintentos igual que tu código
    for intento in range(1, config.MAX_RETRIES + 1):
        try:
            if not os.path.exists(path_archivo):
                print(f"❌ Archivo no encontrado: {path_archivo}")
                return False

            print(f"📤 Publicando {os.path.basename(path_archivo)}...")
            resultado, detalle = whatsapp.publicar_estado(path_archivo, mensaje)
            
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
                print(f"❌ No se pudo publicar después de {config.MAX_RETRIES} intentos")
                return False

def verificar_codigo_ingresado(codigo_usuario):
    """Verifica si el código que puso el usuario es el mismo que se le envió"""
    return codigo_usuario == config.CODIGO_GENERADO
