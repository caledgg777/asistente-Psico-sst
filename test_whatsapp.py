from scraper import scrape_mintrabajo, scrape_fondo_riesgos
import pywhatkit as kit
from datetime import datetime, timedelta

# Obtener noticias de las páginas
noticias = scrape_mintrabajo() + scrape_fondo_riesgos()

# Preparar el mensaje
message = "Noticias relevantes de SST:\n"
for noticia in noticias:
    message += f"{noticia['title']} - {noticia['link']}\n"

# Configurar la hora de envío (2 minutos después de ejecutar el script)
current_time = datetime.now()
send_time = current_time + timedelta(minutes=2)
hour = send_time.hour
minute = send_time.minute

# Enviar mensaje usando pywhatkit
kit.sendwhatmsg("+573168241257", message, hour, minute)
