import telebot
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime
import time
import threading

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

URLS = [
    "https://habr.com/ru/hub/infosecurity/",
    "https://habr.com/ru/hub/programming/",
    "https://habr.com/ru/hub/education/"
]


#  Парсинг Хабра
def get_habr_articles():
    articles = []
    for url in URLS:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        for article in soup.find_all("article"):
            title_tag = article.find("h2")
            if title_tag:
                title = title_tag.text.strip()
                link = title_tag.find("a")["href"]

                if link.startswith("/"):
                    link = "https://habr.com" + link

                articles.append((title, link))
    return articles


#  Отправка статьи
def send_random_article():
    articles = get_habr_articles()
    if not articles:
        return

    title, url = random.choice(articles)

    message = (
        f"<b>{title}</b>\n\n"
        f"👉 Читать: {url}\n\n"
        f"<i>Источник: Хабр</i>"
    )

    bot.send_message(
        CHAT_ID,
        message,
        parse_mode="HTML",
        disable_web_page_preview=False
    )


#  Планировщик
def scheduler():
    # ВРЕМЕНА, когда бот будет публиковать пост
    #POST_TIMES = ["12:00", "18:00", "09:00"]
    POST_TIMES = ["18:00"]

    while True:
        now = datetime.now().strftime("%H:%M")
        if now in POST_TIMES:
            send_random_article()
            time.sleep(61)   # чтобы не повторять в ту же минуту
        else:
            time.sleep(20)


#  Запуск планировщика
def start_scheduler():
    time.sleep(3)
    scheduler()


#  Telegram команды
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(message, "Бот готов! Используйте /article для отправки статьи вручную.")
    # если нужно — расскоментировать:
    # send_random_article()


@bot.message_handler(commands=["article", "post"])
def send_article_command(message):
    send_random_article()



if __name__ == "__main__":
    threading.Thread(target=start_scheduler, daemon=True).start()
    bot.polling(none_stop=True, interval=2)