-- ========================================
-- Инициализация базы данных для Telegram-бота
-- ========================================
-- 1. Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    users_id VARCHAR(100) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    username VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс по username (если нужно)
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
-- Индекс по users_id (уже есть как PK)

-- 2. Таблица чатов (связь user ↔ chat)
CREATE TABLE IF NOT EXISTS chats (
    chat_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    --UNIQUE(user_id, chat_id)
);

-- Индекс по user_id — для быстрого поиска всех чатов пользователя
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);

-- 3. Таблица сообщений (входящие от пользователя)
CREATE TABLE IF NOT EXISTS messages (
    message_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    date BIGINT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс по user_id и date — для выборки по времени
CREATE INDEX IF NOT EXISTS idx_messages_user_date ON messages(user_id, date DESC);

-- 4. Таблица AI-сообщений (ответы от модели)
CREATE TABLE IF NOT EXISTS ai_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id VARCHAR(100) NOT NULL REFERENCES chats(chat_id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс по chat_id и timestamp — для получения истории чата
CREATE INDEX IF NOT EXISTS idx_ai_messages_chat_time ON ai_messages(chat_id, timestamp DESC);

