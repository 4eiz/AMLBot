CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,  -- Уникальный идентификатор пользователя
    bought_checks INTEGER DEFAULT 0,             -- Количество купленных проверок
    free_checks INTEGER DEFAULT 0,               -- Количество бесплатных проверок
    referrer_id INTEGER,                         -- ID пользователя, который пригласил (реферер)
    ref_code VARCHAR(50) UNIQUE,             -- Реферальный код пользователя
    lang TEXT NOT NULL,
    FOREIGN KEY (referrer_id) REFERENCES users(user_id)  -- Связь с самим собой (реферер)
);

CREATE TABLE IF NOT EXISTS promo_codes (
    promo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    promo_name TEXT NOT NULL UNIQUE,
    discount_percent REAL NOT NULL,
    expiration_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_discounts (
    discount_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный идентификатор скидки
    user_id INTEGER NOT NULL,                      -- ID пользователя
    discount_percent REAL NOT NULL,                -- Процент скидки (например, 10.5 для 10.5%)
    created_at TEXT DEFAULT (datetime('now')),     -- Дата создания скидки
    FOREIGN KEY (user_id) REFERENCES users(user_id) -- Связь с таблицей users
);