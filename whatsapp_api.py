# ==========================================
# WhatsApp API - Conexión y Publicación
# ✅ Compatible con Termux y PC
# ✅ Código de 8 dígitos
# ✅ Publicación automática de estados
# ==========================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import platform

class WhatsAppAPI:
    def __init__(self):
        self.driver = None
        self.sesion_activa = False

    def iniciar_sesion(self):
        """Inicia la conexión con WhatsApp Web, compatible con Termux y PC"""
        try:
            opciones = Options()
            # Configuraciones generales
            opciones.add_argument("--start-maximized")
            opciones.add_argument("--disable-notifications")
            opciones.add_argument("--lang=es")
            opciones.add_argument("--disable-gpu")
            opciones.add_argument("--no-sandbox")
            opciones.add_argument("--disable-dev-shm-usage")
            # Guardar sesión para no escanear siempre
            opciones.add_argument("user-data-dir=sesion")
            # Evitar detección de automatización
            opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
            opciones.add_experimental_option("useAutomationExtension", False)

            # Si estás en Termux, usamos configuración especial
            if platform.system() == "Linux" and "com.termux" in os.getcwd():
                # Para Termux usamos el navegador disponible
                opciones.binary_location = "/data/data/com.termux/files/usr/bin/chromium"
                self.driver = webdriver.Chrome(options=opciones)
            else:
                # Para PC usamos el instalador automático
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=opciones
                )

            # Abrir WhatsApp Web
            self.driver.get("https://web.whatsapp.com/")
            self.sesion_activa = True
            return True, "Sesión iniciada, espera a que cargue WhatsApp Web"

        except Exception as e:
            return False, f"Error al iniciar sesión: {str(e)}"

    def verificar_codigo(self, codigo_ingresado):
        """Verifica que el código ingresado cumpla con las reglas"""
        try:
            # Esperar a que cargue la interfaz principal
            WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="side"] | //header[@data-testid="chatlist-header"]'))
            )

            # Validación básica: debe ser 8 dígitos numéricos
            if len(codigo_ingresado) == 8 and codigo_ingresado.isdigit():
                return True, "Código válido, comenzando publicación..."
            else:
                return False, "El código debe tener exactamente 8 números"

        except Exception as e:
            return False, f"Error al verificar código: {str(e)}"

    def publicar_estado(self, ruta_video):
        """Publica un video como estado automáticamente"""
        try:
            # Verificar que el archivo exista
            if not os.path.exists(ruta_video):
                return False, f"Archivo no encontrado: {ruta_video}"

            # 1. Hacer clic en el botón de Estados
            btn_estado = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="status-outline"] | //div[@title="Estado"]'))
            )
            btn_estado.click()
            time.sleep(2)

            # 2. Hacer clic en el botón de agregar archivo
            btn_agregar = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/*"]'))
            )
            # Enviar la ruta completa del video
            btn_agregar.send_keys(os.path.abspath(ruta_video))
            time.sleep(4)

            # 3. Hacer clic en el botón de enviar
            btn_enviar = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"] | //div[@aria-label="Enviar"]'))
            )
            btn_enviar.click()
            time.sleep(5)

            # Volver a la pantalla principal para el siguiente archivo
            self.driver.get("https://web.whatsapp.com/")
            time.sleep(3)

            return True, f"Publicado correctamente: {os.path.basename(ruta_video)}"

        except Exception as e:
            return False, f"Error al publicar: {str(e)}"

    def cerrar_sesion(self):
        """Cierra el navegador al terminar"""
        if self.driver:
            self.driver.quit()
            self.sesion_activa = False
