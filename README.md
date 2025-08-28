# 🛡️ AMLBot — Telegram-бот

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Aiogram](https://img.shields.io/badge/aiogram-3.x-ff69b4)
![License](https://img.shields.io/badge/license-MIT-green)

AMLBot — многоюзерный Telegram‑бот на **aiogram 3**, с балансом, пополнениями через CryptoBot, профилем, реферальной системой и проверками адресов/транзакций. Конфигурация через `.env`. База данных — SQLite (асинхронно).

---

## ✨ Возможности
- 👤 Профиль пользователя
- 💰 Баланс и пополнение (CryptoBot)
- 🧩 Промокоды / акции
- 🧷 Реферальная система
- 🆘 Поддержка
- 🌐 Смена языка
- 🔎 Проверка адреса/транзакции (раздел `check`)
- 🗂️ Хранилище: SQLite (модели/запросы в `data/`)

> Список составлен по исходникам (`app/`, `data/`). При необходимости допишем разделы.

---

## 📂 Структура проекта (сокращённо)
```
AMLBot/
├─ app/                  # хендлеры (balance, profile, check, promo, etc)
├─ data/                 # работа с БД: users, promos (+ init script)
├─ keyboards/            # клавиатуры
├─ config.py             # загрузка .env и инициализация бота
├─ main.py               # запуск и регистрация роутеров
├─ .env                  # локальная конфигурация (не коммитим)
└─ results/              # артефакты (если нужны)
```

---

## ⚙️ Переменные окружения
Создайте `.env` на основе примера и заполните значения:
```dotenv
BOT_TOKEN=        # токен Telegram-бота (обязательно)
CRYPTO_TOKEN=     # токен CryptoBot (для пополнений)
```

> `BOT_TOKEN` используется в `config.py`. `CRYPTO_TOKEN` — в модуле пополнений (CryptoBot).

---

## 🚀 Установка и запуск

### 1) Клонирование
```bash
git clone https://github.com/<username>/AMLBot.git
cd AMLBot
```

### 2) Виртуальная среда и зависимости
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# зависимости
pip install -r req.txt  # если файл присутствует
# или вручную:
pip install aiogram python-dotenv aiosqlite
```

### 3) Настроить окружение
```bash
cp .env.example .env
# затем отредактируйте .env и вставьте ваши токены
```

### 4) Запуск
```bash
python main.py
```

> В `main.py` удаляется вебхук и запускается `start_polling()`.

---

## 🧪 Тесты/качество кода (опционально)
Рекомендуется добавить `pytest` и линтер (`ruff`/`flake8`) и настроить GitHub Actions.

---

## 🛠 Полезные команды
```bash
git init
git add .
git commit -m "init AMLBot repo"
git branch -M main
git remote add origin https://github.com/<username>/AMLBot.git
git push -u origin main
```

---

## 📜 Лицензия
MIT — см. `LICENSE`

---

**Автор:** Роберт • [Telegram](https://t.me/che1zi)
