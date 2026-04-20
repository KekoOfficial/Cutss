from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class WhatsAppAPI:
    def __init__(self):
        self.driver = None
        self.sesion_activa = False

    def iniciar_sesion(self):
        """Inicia conexión con WhatsApp Web"""
        try:
            opciones = Options()
            opciones.add_argument("--start-maximized")
            opciones.add_argument("--disable-notifications")
            opciones.add_argument("--lang=es")
            opciones.add_argument("--disable-gpu")
            opciones.add_argument("--no-sandbox")
            opciones.add_argument("--disable-dev-shm-usage")
            opciones.add_argument("user-data-dir=sesion")
            opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
            opciones.add_experimental_option("useAutomationExtension", False)

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=opciones
            )

            self.driver.get("https://web.whatsapp.com/")
            print("🔄 Cargando WhatsApp Web... Escanea el código QR si es necesario")
            self.sesion_activa = True
            return True, "Sesión iniciada"

        except Exception as e:
            return False, f"Error al iniciar: {str(e)}"

    def verificar_codigo(self, codigo_ingresado):
        """Valida que el código ingresado sea de 8 dígitos"""
        try:
            WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="side"] | //header[@data-testid="chatlist-header"]'))
            )

            if len(codigo_ingresado) == 8 and codigo_ingresado.isdigit():
                return True, "Código válido"
            else:
                return False, "El código debe tener 8 dígitos numéricos"

        except Exception as e:
            return False, f"Error al verificar: {str(e)}"

    def publicar_estado(self, ruta_video, descripcion):
        """Publica video y mensaje como estado"""
        try:
            # Botón de Estados
            btn_estado = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="status-outline"] | //div[@title="Estado"]'))
            )
            btn_estado.click()
            time.sleep(2)

            # Botón para agregar archivo
            input_archivo = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/*"]'))
            )
            input_archivo.send_keys(os.path.abspath(ruta_video))
            time.sleep(4)

            # Agregar descripción si hay
            if descripcion:
                campo_texto = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Añade un pie de foto"]'))
                )
                campo_texto.click()
                campo_texto.send_keys(descripcion)
                time.sleep(1)

            # Botón de enviar
            btn_enviar = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"] | //div[@aria-label="Enviar"]'))
            )
            btn_enviar.click()
            time.sleep(5)

            # Volver a la pantalla principal
            self.driver.get("https://web.whatsapp.com/")
            time.sleep(3)

            return True, "Publicado correctamente"

        except Exception as e:
            return False, f"Error al publicar: {str(e)}"
