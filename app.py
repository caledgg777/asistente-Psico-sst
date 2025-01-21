import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pywhatkit as kit
import schedule
import threading
import requests
from requests.exceptions import RequestException

app = Flask(__name__)

# Ruta principal
@app.route('/')
def home():
    return "La IA está activa y funcionando."

# Ruta para obtener noticias del Ministerio de Trabajo y del otro sitio web
@app.route('/noticias', methods=['GET'])
def noticias():
    try:
        noticias_mintrabajo = obtener_noticias_ministerio()
        noticias_seguridad_laboral = obtener_noticias_seguridad_laboral()
        return jsonify({"noticias_mintrabajo": noticias_mintrabajo, "noticias_seguridad_laboral": noticias_seguridad_laboral}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# Configuración común para el navegador
def configurar_navegador():
    service = Service('./chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Opcional, elimina si necesitas ver el navegador
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument("--disable-extensions")  # Desactivar extensiones
    options.add_argument("--incognito")          # Modo incógnito
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--ignore-certificate-errors')  # Ignorar errores de certificado
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Retorna el navegador configurado
    return webdriver.Chrome(service=service, options=options)

# Función para obtener noticias del Ministerio de Trabajo
def obtener_noticias_ministerio():
    driver = configurar_navegador()

    try:
        url = "https://www.mintrabajo.gov.co/"
        driver.get(url)

        # Esperar a que se cargue el contenido relevante
        WebDriverWait(driver, 30).until(  # Incrementamos el tiempo de espera a 30 segundos
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Guardar el HTML para depuración
        with open("pagina_mintrabajo.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        # Usar BeautifulSoup para buscar elementos
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        noticias = soup.find_all('h2', class_='title-section-mintra borde-Turquesa-100')

        # Validar si se encontraron noticias y decodificar caracteres especiales
        if noticias:
            lista_noticias = [noticia.text.strip().encode('latin1').decode('utf-8') for noticia in noticias[:10]]  # Extraemos hasta 10 noticias
        else:
            print("No se encontraron noticias en el Ministerio de Trabajo.")
            lista_noticias = []

        return lista_noticias

    except Exception as e:
        print("Error al obtener noticias del Ministerio:", e)
        return []

    finally:
        driver.quit()

# Función para obtener noticias de Seguridad Laboral
def obtener_noticias_seguridad_laboral():
    driver = configurar_navegador()

    try:
        url = "https://www.seguridad-laboral.es/sl-latam/colombia/normatividad-en-seguridad-y-salud-en-el-trabajo-2019-2020-colombia_20200630.html"
        driver.get(url)

        # Esperar a que se cargue el contenido relevante
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Guardar el HTML para depuración
        with open("pagina_seguridad_laboral.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        # Usar BeautifulSoup para buscar elementos
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        noticias = soup.find_all('h2')

        # Validar si se encontraron noticias y decodificar caracteres especiales
        if noticias:
            lista_noticias = [noticia.text.strip().encode('latin1').decode('utf-8') for noticia in noticias[:10]]  # Extraemos hasta 10 noticias
        else:
            print("No se encontraron noticias en Seguridad Laboral.")
            lista_noticias = []

        return lista_noticias

    except Exception as e:
        print("Error al obtener noticias de Seguridad Laboral:", e)
        return []

    finally:
        driver.quit()

# Función para hacer la solicitud con reintento
def obtener_datos_con_reintento(url, max_intentos=3):
    for intento in range(max_intentos):
        try:
            # Desactivar la verificación del certificado SSL
            response = requests.get(url, verify=False)  # Desactivar la verificación de SSL
            response.raise_for_status()
            return response.text
        except RequestException as e:
            print(f"Error en intento {intento + 1}: {e}")
            time.sleep(5)  # Esperar 5 segundos antes de reintentar
    return None

# Función para enviar las noticias por WhatsApp
def enviar_noticias_por_whatsapp():
    try:
        noticias_mintrabajo = obtener_noticias_ministerio()
        noticias_seguridad_laboral = obtener_noticias_seguridad_laboral()

        mensaje = "📢 Noticias de Seguridad y Salud en el Trabajo:\n\n"
        if noticias_mintrabajo:
            mensaje += "Ministerio de Trabajo:\n"
            for i, noticia in enumerate(noticias_mintrabajo, 1):
                mensaje += f"{i}. {noticia}\n"

        if noticias_seguridad_laboral:
            mensaje += "\nSeguridad Laboral:\n"
            for i, noticia in enumerate(noticias_seguridad_laboral, 1):
                mensaje += f"{i}. {noticia}\n"

        # Lista de números de teléfono
        numeros_telefono = {
            "+573166258715": "Luz",
            "+573103113231": "Mary",
            "+573165240838": "Diana",
            "+573216118812": "Sirley",
            "+573004448459": "Marco"
        }

        # Enviar el mensaje por WhatsApp a cada número
        for numero, nombre in numeros_telefono.items():
            mensaje_personalizado = f"Hola {nombre}, {mensaje}"
            kit.sendwhatmsg(numero, mensaje_personalizado, 8, 0)  # Cambia el número al destinatario deseado
            print(f"Mensaje enviado a {nombre} ({numero}) con éxito.")

    except Exception as e:
        print("Error al enviar mensaje por WhatsApp:", e)

# Programar la tarea diaria
def programar_tareas_diarias():
    schedule.every().day.at("09:25").do(enviar_noticias_por_whatsapp)
    schedule.every().day.at("20:30").do(enviar_noticias_por_whatsapp)

    while True:
        schedule.run_pending()
        time.sleep(5)

# Ejecutar el servidor Flask y las tareas en paralelo
if __name__ == "__main__":
    print("Iniciando el servidor Flask...")

    threading.Thread(target=programar_tareas_diarias, daemon=True).start()
    app.run(debug=True)
