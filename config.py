import random

# ⚙️ CONFIGURACIÓN GENERAL
# ⏱️ Duración de cada fragmento en segundos
CLIP_DURATION = 60  

# 🔁 Reintentos si falla el envío
MAX_RETRIES = 3
# ⏳ Tiempo de espera máximo por publicación
TIMEOUT_SEND = 300

# 📂 Rutas de trabajo
TEMP_FOLDER = "videos/output"
INPUT_FOLDER = "videos/input"

# 📱 DATOS DE WHATSAPP
# Tu número de teléfono ya configurado
NUMERO_USUARIO = "+595984067983"  

# Aquí se guarda el código que NOSOTROS TE ENVIAMOS
CODIGO_ENVIADO = ""

def generar_y_guardar_codigo():
    """Genera el código de 8 dígitos y lo guarda para enviártelo"""
    global CODIGO_ENVIADO
    # Generamos el código aleatorio
    CODIGO_ENVIADO = ''.join(random.choices('0123456789', k=8))
    print(f"📌 CÓDIGO GENERADO PARA ENVIAR: {CODIGO_ENVIADO}")
    return CODIGO_ENVIADO

def verificar_codigo_ingresado(codigo_usuario):
    """Comprueba que el código que pusiste sea el mismo que te enviamos"""
    return codigo_usuario.strip() == CODIGO_ENVIADO
