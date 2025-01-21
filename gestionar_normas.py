import sqlite3
import requests
from bs4 import BeautifulSoup
import urllib3
import pywhatkit
import schedule
import time
from datetime import datetime  # Importar la librería datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Conexión a la base de datos
def conectar_bd():
    return sqlite3.connect("normas_sst.db")

# Función para obtener el saludo según la hora del día
def saludo_inicial():
    # Obtener la hora actual
    hora_actual = datetime.now().hour

    # Saludo basado en la hora del día
    if 6 <= hora_actual < 12:
        saludo = "¡Buenos días!"
    elif 12 <= hora_actual < 18:
        saludo = "¡Buenas tardes!"
    else:
        saludo = "¡Buenas noches!"

    print(f"\n{saludo}")
    print("Soy tu asistente virtual, aquí para ayudarte a mantenerte actualizado con las normas y leyes sobre seguridad y salud en el trabajo.")
    print("Tengo novedades en Seguridad y Salud en el Trabajo que pueden que te interesen de las siguientes páginas:\n")

# Buscar normas, resoluciones y noticias en las páginas oficiales
def buscar_normas():
    urls = [
        "https://www.mintrabajo.gov.co/",  # Página oficial del Ministerio de Trabajo
        "https://www.fondoriesgoslaborales.gov.co/",  # Página oficial del Fondo de Riesgos Laborales
        "https://www.minsalud.gov.co/"  # Página oficial del Ministerio de Salud y Protección Social
    ]
    
    normas = []
    for url in urls:
        print(f"\nBuscando en: {url}")
        try:
            response = requests.get(url, verify=False, timeout=10)
            response.raise_for_status()  # Verificar que la respuesta sea exitosa (200)
            soup = BeautifulSoup(response.text, "html.parser")

            enlaces_encontrados = 0
            for link in soup.find_all("a", href=True):
                titulo = link.text.strip()
                enlace = link["href"]

                # Filtrar enlaces que contienen palabras clave relacionadas con normatividad SST, resoluciones, etc.
                if any(keyword in titulo.lower() for keyword in ["sst", "seguridad", "trabajo", "resolución", "norma", "ley"]):
                    if enlace.startswith("/"):
                        enlace = url.rstrip("/") + enlace
                    normas.append((titulo, enlace))
                    enlaces_encontrados += 1

            print(f"Enlaces encontrados en {url}: {enlaces_encontrados}")
        except Exception as e:
            print(f"Error al acceder a {url}: {e}")

    return normas

# Registrar normas nuevas en la base de datos
def registrar_normas(normas):
    conn = conectar_bd()
    cursor = conn.cursor()

    for titulo, enlace in normas:
        cursor.execute("SELECT * FROM normas WHERE enlace = ?", (enlace,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO normas (titulo, enlace) VALUES (?, ?)", (titulo, enlace))
            print(f"Norma registrada: {titulo}")
    conn.commit()
    conn.close()

# Consultar registros en la base de datos
def consultar_normas():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("SELECT id, titulo, enlace FROM normas ORDER BY id DESC")
    registros = cursor.fetchall()

    conn.close()
    return registros

# Mostrar registros en pantalla
def mostrar_normas(registros):
    print("\n=== Normas registradas en la base de datos ===\n")
    if not registros:
        print("No se encontraron registros.")
    else:
        for norma in registros:
            print(f"ID: {norma[0]}")
            print(f"Título: {norma[1]}")
            print(f"Enlace: {norma[2]}")
            print("-" * 50)

# Automatizar la búsqueda diaria
def tarea_diaria():
    saludo_inicial()
    print("\n[Automatización] Iniciando búsqueda diaria de normas...")
    normas = buscar_normas()
    registrar_normas(normas)
    print("[Automatización] Búsqueda diaria completada.")

# Enviar normas registradas por WhatsApp
def enviar_normas_por_whatsapp(numeros_telefonos):
    registros = consultar_normas()
    if not registros:
        print("No hay normas para enviar.")
        return

    mensaje = "=== Normas SST Registradas ===\n\n"
    for norma in registros:
        mensaje += f"ID: {norma[0]}\nTítulo: {norma[1]}\nEnlace: {norma[2]}\n\n"

    # Limitar el tamaño del mensaje
    if len(mensaje) > 1600:
        print("El mensaje es demasiado largo, se truncará.")
        mensaje = mensaje[:1600]  # Recortar el mensaje si es necesario

    for numero_telefono in numeros_telefonos:
        try:
            if not numero_telefono.startswith('+') or len(numero_telefono) < 12:
                print(f"El número {numero_telefono} no tiene el formato internacional correcto.")
                continue

            print(f"Enviando mensaje a {numero_telefono}...")
            pywhatkit.sendwhatmsg_instantly(numero_telefono, mensaje, wait_time=30, tab_close=True)
            print(f"Mensaje enviado a {numero_telefono} exitosamente.")
        except Exception as e:
            print(f"Error al enviar el mensaje a {numero_telefono}: {e}")

if __name__ == "__main__":
    print("=== Gestor de Normas en SST ===")
    print("1. Buscar y registrar nuevas normas")
    print("2. Consultar normas registradas")
    print("3. Activar automatización diaria")
    print("4. Enviar normas por WhatsApp")
    opcion = input("Selecciona una opción (1, 2, 3 o 4): ")

    if opcion == "1":
        saludo_inicial()
        print("\nIniciando búsqueda de normas...")
        normas = buscar_normas()
        registrar_normas(normas)
        print("\nBúsqueda y registro completados.")
    elif opcion == "2":
        registros = consultar_normas()
        mostrar_normas(registros)
    elif opcion == "3":
        saludo_inicial()
        print("\nActivando automatización diaria. El script buscará normas todos los días a las 8:00 AM.")
        schedule.every().day.at("08:00").do(tarea_diaria)

        while True:
            schedule.run_pending()
            time.sleep(60)  # Esperar un minuto entre cada revisión
    elif opcion == "4":
        numeros = input("Introduce los números de teléfono separados por coma (por ejemplo, +57XXXXXXXXXX,+57YYYYYYYYY): ")
        numeros_lista = numeros.split(",")
        enviar_normas_por_whatsapp(numeros_lista)
    else:
        print("Opción no válida. Por favor, selecciona 1, 2, 3 o 4.")
