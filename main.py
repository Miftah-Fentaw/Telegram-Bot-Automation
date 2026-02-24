import requests
import feedparser
import sqlite3
import schedule
import time
from config import BOT_TOKEN, CHANNEL_ID
from bs4 import BeautifulSoup


KEYWORDS = [
    "flutter", "android", "kotlin", "react", "vue",
    "node", "backend", "api", "javascript",
    "web", "mobile", "cyber", "security",
    "linux", "docker", "kubernetes",
    "ai", "machine learning", "python"
]

# ---------------- DATABASE SETUP ---------------- #

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    link TEXT PRIMARY KEY
)
""")
conn.commit()


def already_posted(link):
    cursor.execute("SELECT link FROM posts WHERE link=?", (link,))
    return cursor.fetchone()


def save_post(link):
    cursor.execute("INSERT INTO posts (link) VALUES (?)", (link,))
    conn.commit()


# ---------------- FETCH NEWS ---------------- #

# def fetch_news():
#     feed = feedparser.parse("https://news.ycombinator.com/rss")
#
#     for entry in feed.entries:
#         title_lower = entry.title.lower()
#
#         # Keyword filter
#         if any(keyword in title_lower for keyword in KEYWORDS):
#
#             if not already_posted(entry.link):
#                 return entry
#
#     return None
def fetch_news():
    feed = feedparser.parse("https://news.ycombinator.com/rss")

    for entry in feed.entries:
        if not already_posted(entry.link):
            return entry

    return None


# ---------------- TELEGRAM SEND ---------------- #

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "disable_web_page_preview": False
    }

    response = requests.post(url, data=data)

    if response.status_code != 200:
        print("Error sending message:", response.text)


# ---------------- KEYWORD DETECTION ---------------- #

def detect_keyword(title):
    title_lower = title.lower()
    for keyword in KEYWORDS:
        if keyword in title_lower:
            return keyword
    return "modern development"


# ---------------- MAIN JOB ---------------- #

def clean_summary(text):
    # Remove HTML tags if any
    import re
    clean = re.sub('<.*?>', '', text)
    return clean.strip()



def extract_article_text(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        text_content = ""

        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 80:  # ignore short junk lines
                text_content += text + " "
            if len(text_content) > 500:
                break

        return text_content[:400]
    except:
        return ""





def job():
    entry = fetch_news()

    if entry:
        keyword = detect_keyword(entry.title)

        # Extract real article content
        article_text = extract_article_text(entry.link)

        if article_text and len(article_text) > 100:
            summary = article_text
        else:
            summary = "A new update in the tech ecosystem that developers should keep an eye on."

        message = f"""🔥 Dev Stack Update

📰 {entry.title}

📌 What’s happening:
{summary}

💡 Developer Insight:
If you're working with {keyword}, this could impact tooling, architecture decisions, or future trends in your stack.

🔗 Read more:
{entry.link}
"""

        send_to_telegram(message)
        save_post(entry.link)
        print("Posted:", entry.title)

    else:
        print("No new matching articles found.")


# ---------------- SCHEDULER ---------------- #


print("Bot running...")

while True:
    try:
        schedule.run_pending()
        time.sleep(30)
    except Exception as e:
        print("Error:", e)
        time.sleep(10)