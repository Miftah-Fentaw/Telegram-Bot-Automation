<p align="center">
  <img src="banner.png" alt="Telegram Bot Automation Banner" width="100%">
</p>

🚀 **Telegram-Bot-Automation** is a Python-based bot designed to automatically fetch the latest tech news and updates from sources like Hacker News and deliver them straight to your Telegram channel.

## ✨ Features

- 📰 **Auto-Fetch News**: Scrapes RSS feeds (e.g., Hacker News) for the latest articles.
- 🔍 **Smart Filtering**: Detects keywords like Flutter, Android, AI, and Python to provide relevant insights.
- ✉️ **Telegram Integration**: Sends beautifully formatted updates directly to a specified Telegram channel.
- 💾 **Persistence**: Uses SQLite to keep track of posted links and avoid duplicates.
- 🕒 **Scheduled Updates**: Runs periodically to keep your channel fresh with new content.

## 🛠️ Tech Stack

- **Language**: Python
- **Libraries**: `requests`, `feedparser`, `sqlite3`, `schedule`, `beautifulsoup4`
- **Database**: SQLite

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A Telegram Channel ID

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Miftah-Fentaw/Telegram-Bot-Automation.git
   cd Telegram-Bot-Automation
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have `requests`, `feedparser`, `schedule`, `beautifulsoup4`, and `python-dotenv` installed.)*

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   CHANNEL_ID=your_telegram_channel_id
   ```

### Running the Bot

Start the bot by running:
```bash
python main.py
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTION.md](CONTRIBUTION.md) for guidelines on how to get started.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


