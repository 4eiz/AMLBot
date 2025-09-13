# 🛡️ AMLBot — Telegram Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)  
![Aiogram](https://img.shields.io/badge/aiogram-3.x-ff69b4)  
![License](https://img.shields.io/badge/license-MIT-green)  

**AMLBot** — a multi-user Telegram bot built with **aiogram 3**, featuring balance management, top-ups via CryptoBot, user profiles, referral system, and address/transaction checks. Configuration is handled through `.env`. The database is SQLite (asynchronous).  

> 💡 This project is a test and demo version developed for a developer from Croatia.  

---

## ✨ Features
- 👤 User profile  
- 💰 Balance and top-ups (CryptoBot)  
- 🧩 Promo codes / discounts  
- 🧷 Referral system  
- 🆘 Support section  
- 🌐 Multi-language support  
- 🔎 Address/transaction checks (`check` section)  
- 🗂️ Storage: SQLite (models/queries in `data/`)  

---

## 📂 Project Structure (simplified)
```
AMLBot/
├─ app/ # handlers (balance, profile, check, promo, etc.)
├─ data/ # database: users, promos (+ init script)
├─ keyboards/ # keyboards
├─ config.py # loads .env and bot initialization
├─ main.py # startup and router registration
├─ .env # local configuration (excluded from repo)
└─ results/ # artifacts (if needed)
```

---

## ⚙️ Environment Variables
Create a `.env` file based on the example and provide values:
```dotenv
BOT_TOKEN=        # Telegram bot token (required)
CRYPTO_TOKEN=     # CryptoBot token (for top-ups)

    BOT_TOKEN is used in config.py. CRYPTO_TOKEN is used in the CryptoBot top-up module.

🚀 Installation & Run
1) Clone the repository

git clone https://github.com/4eiz/AMLBot.git
cd AMLBot

2) Virtual environment & dependencies

python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# install dependencies
pip install -r req.txt  # if present
# or manually:
pip install aiogram python-dotenv aiosqlite

3) Configure environment

cp .env.example .env
# then edit .env and insert your tokens

4) Run the bot

python main.py

    In main.py, the webhook is removed and start_polling() is launched.

🧪 Tests / Code Quality (optional)

It is recommended to add pytest and a linter (ruff/flake8), and configure GitHub Actions.
🛠 Useful Git Commands

git init
git add .
git commit -m "init AMLBot repo"
git branch -M main
git remote add origin https://github.com/4eiz/AMLBot.git
git push -u origin main

📜 License

MIT — see LICENSE

Author: Robert • Telegram
