import requests
import feedparser
import sqlite3
import time
from bs4 import BeautifulSoup
from config import BOT_TOKEN, CHANNEL_ID, HUGGINGFACE_API_KEY

# -------- DATABASE -------- #
conn = sqlite3.connect("ai_database.db")
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

# -------- CONFIGURATION -------- #
FEEDS = [
    "https://news.ycombinator.com/rss",          # Hacker News
    "https://dev.to/feed",                       # Dev.to
    "https://android-developers.googleblog.com/feeds/posts/default", # Android Devs
    "https://flutter.dev/feed",                  # Flutter
    "https://www.darkreading.com/rss.xml",        # Cybersecurity
]

TECH_KEYWORDS = [
    "flutter", "android", "kotlin", "java", "python", "javascript", "react", "vue",
    "compiler", "api", "architecture", "security", "vulnerability", "encryption",
    "backend", "frontend", "mobile", "ios", "swift", "dart", "database", "sql",
    "cicd", "devops", "kubernetes", "docker", "git", "linux", "kernel", "malware",
    "bytecode", "optimization", "firmware", "exploit"
]

def is_technical(text):
    text = text.lower()
    return any(keyword in text for keyword in TECH_KEYWORDS)

# -------- FETCH NEWS -------- #
def fetch_news():
    for url in FEEDS:
        print(f"Checking feed: {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Check if technical before processing
            content = (entry.title + " " + entry.get("summary", "")).lower()
            if is_technical(content) and not already_posted(entry.link):
                return entry
    return None

# -------- EXTRACT ARTICLE -------- #
def extract_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        paragraphs = soup.find_all("p")
        text = ""
        for p in paragraphs:
            t = p.get_text().strip()
            if len(t) > 60:
                text += t + " "
            if len(text) > 800:
                break
        return text[:800]
    except:
        return ""

# -------- AI REWRITE USING HUGGING FACE -------- #
def rewrite_with_ai(title, content, link):
    system_prompt = (
        "You are a professional tech news curator for a hacker-friendly Telegram channel. "
        "Your role is to create short, engaging posts strictly about development and cybersecurity. "
        "\n\nRules:\n"
        "1. ONLY process content related to: Mobile/Web development, Programming, Android, Flutter, Kotlin, or Cybersecurity.\n"
        "2. If the topic is non-technical (e.g., general business, politics, non-dev news), return the string 'REJECT'.\n"
        "3. Start with a relevant emoji and a *Bold Title*.\n"
        "4. Provide a concise summary in 2-3 bullet points.\n"
        "5. Tone: professional, direct, developer-focused. No marketing fluff.\n"
        "6. Mandatory hashtags at the very bottom: #Programming #TechNews #DevLife #ManceTech\n"
        "7. Source link at the end.\n"
        "8. Use ONLY single asterisks (*) for bold text. DO NOT use HTML tags, double asterisks (**), underscores (_), or backticks (`)."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Title: {title}\n\nContent: {content}\n\nLink: {link}"}
    ]

    model = "meta-llama/Llama-3.2-3B-Instruct"

    try:
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
            json={
                "model": model,
                "messages": messages,
                "max_tokens": 400,
                "temperature": 0.4 # Lower temperature for more factual summaries
            }
        )

        if response.status_code != 200:
            print("AI error:", response.text)
            return None

        result = response.json()
        output = result["choices"][0]["message"]["content"].strip()
        
        if "REJECT" in output.upper() and len(output) < 15:
            print(f"AI rejected non-technical content: {title}")
            return None
            
        # Clean up output to prevent markdown parsing errors in Telegram
        output = output.replace('**', '*')  # Use single asterisk for bold
        output = output.replace('_', '')     # Remove underscores
        output = output.replace('`', '')     # Remove backticks
        output = output.replace('<font', '').replace('</font>', '') # Remove font tags if any
        output = output.replace('<b>', '*').replace('</b>', '*')  # Convert any b tags to asterisk
            
        return output
    except Exception as e:
        print("AI Process error:", e)
        return None

# -------- TELEGRAM -------- #
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown", # Enable bold and markdown
        "disable_web_page_preview": False
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print("Telegram error (Markdown mode):", r.text)
        print("Retrying as plain text...")
        del data["parse_mode"]
        r = requests.post(url, data=data)
        if r.status_code != 200:
            print("Telegram error (Plain text mode):", r.text)

# -------- MAIN LOOP -------- #
def run():
    print("AI bot running with technical filters...")
    while True:
        entry = fetch_news()
        if entry:
            article = extract_article_text(entry.link)
            if not article:
                article = entry.get("summary", entry.title)

            ai_post = rewrite_with_ai(
                entry.title,
                article,
                entry.link
            )

            if ai_post:
                send_to_telegram(ai_post)
                save_post(entry.link)
                print("Posted:", entry.title)
            else:
                # If rejected/error, we still mark as "seen" to not stuck on it
                save_post(entry.link)
        else:
            print("No new technical news found, waiting...")

        time.sleep(600)  # every 10 minutes

if __name__ == "__main__":
    run()