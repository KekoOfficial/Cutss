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
# Tu número de teléfono con código de país (ya lo configuré)
NUMERO_USUARIO = "+595984067983"  

# Código que genera el sistema y te envía
CODIGO_GENERADO = ""

def generar_codigo():
    """Genera un código aleatorio de 8 dígitos para enviarte por WhatsApp"""
    global CODIGO_GENERADO
    CODIGO_GENERADO = ''.join(random.choices('0123456789', k=8))
    return CODIGO_GENERADO
