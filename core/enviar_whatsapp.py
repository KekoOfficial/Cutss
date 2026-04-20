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
        print("🔑 Conectando con WhatsApp Web...")
        exito, mensaje_sesion = whatsapp.iniciar_sesion()
        if not exito:
            print(f"❌ Error de conexión: {mensaje_sesion}")
            return False
        
        # Verificar código de 8 dígitos
        valido, mensaje_validacion = whatsapp.verificar_codigo(config.CODIGO_SESION)
        if not valido:
            print(f"❌ Código incorrecto: {mensaje_validacion}")
            return False
        
        sesion_iniciada = True
        print("✅ Conectado correctamente a WhatsApp")

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
            
            # Si es error de tamaño, seguimos intentando
            if "413" in error or "Too Large" in error or "archivo muy grande" in error:
                print("ℹ️ Archivo pesado, reintentando...")

            if intento < config.MAX_RETRIES:
                time.sleep(5) # Espera 5s antes de volver a intentar
            else:
                print(f"❌ No se pudo publicar después de {config.MAX_RETRIES} intentos")
                return False
