import requests
import time
import json
import os
from bs4 import BeautifulSoup

# Prende il token e l'ID chat dalle variabili d'ambiente di Railway
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Lista dei manga con genere associato
MANGA_LIST = {
    "The Selfish Romance": {
        "url": "https://www.mangago.me/read-manga/the_selfish_romance/",
        "genere": "Josei"
    },
    "Tears on a Withered Flower": {
        "url": "https://www.mangago.me/read-manga/tears_on_a_withered_flower/",
        "genere": "Josei"
    },
}

# File per salvare gli ultimi capitoli trovati
DATA_FILE = "manga_list.json"

# Messaggi personalizzati per ogni genere
GENERE_MESSAGES = {
    "Shonen": "🔥 Un nuovo capitolo di un avvincente shonen è disponibile!",
    "Seinen": "🖤 Un nuovo capitolo di un seinen oscuro e intenso!",
    "Shoujo": "🖤 Un nuovo capitolo di una storia d'amore!",
    "Isekai": "🌍 Un nuovo viaggio in un altro mondo ti aspetta!",
    "Josei": "💖 Nuovo capitolo di una storia romantica e coinvolgente!",
    "Horror": "👻 Un nuovo capitolo di terrore è arrivato...",
    "Commedia": "😂 Pronto a ridere? Ecco il nuovo capitolo!",
}

def get_latest_chapter(url):
    """Recupera l'ultimo capitolo disponibile dalla pagina del manga"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    latest_chapter = soup.find("div", class_="latest")
    
    return latest_chapter.text.strip() if latest_chapter else None


def send_telegram_message(message):
    """Manda un messaggio su Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)


def load_last_chapters():
    """Carica i dati dal file locale"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_last_chapters(data):
    """Salva i nuovi dati nel file locale"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def check_for_updates():
    """Controlla gli aggiornamenti e invia notifiche"""
    last_chapters = load_last_chapters()

    for title, info in MANGA_LIST.items():
        latest_chapter = get_latest_chapter(info["url"])
        genere = info["genere"]
        
        if latest_chapter and latest_chapter != last_chapters.get(title):
            message_intro = GENERE_MESSAGES.get(genere, "📢 Un nuovo capitolo è disponibile!")  # Messaggio predefinito se il genere non è trovato
            message = f"{message_intro}\n\n📖 *{title} - {latest_chapter}*\n🔗 [Leggilo qui]({info['url']})"
            send_telegram_message(message)
            last_chapters[title] = latest_chapter

    save_last_chapters(last_chapters)


if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(600)  # Controlla ogni 10 minuti
