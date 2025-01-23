import requests
from bs4 import BeautifulSoup

def scrape_mintrabajo():
    url = "https://www.mintrabajo.gov.co"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    noticias = []
    for item in soup.find_all("a", class_="noticia"):  # Ajusta según la estructura de la página
        title = item.text.strip()
        link = url + item["href"]
        noticias.append({"title": title, "link": link})
    return noticias

def scrape_fondo_riesgos():
    url = "https://www.fondoriesgoslaborales.gov.co/noticias/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    noticias = []
    for item in soup.find_all("a", class_="news-title"):  # Ajusta según la estructura de la página
        title = item.text.strip()
        link = url + item["href"]
        noticias.append({"title": title, "link": link})
    return noticias
