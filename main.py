import ai
import telebot
from pyexpat.errors import messages
from telebot import types
import logging
import os
from dotenv import load_dotenv
import database as db
import  qpt

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден! Проверьте файл .env")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


user_states = {}

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):

    #Блок проверок и созданий пользователей и чата в БД
    rez = db.create_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
    if rez.error_code ==3 :
        return bot.send_message(message.chat.id, "Бот временно не доступен")

    rez1 = db.save_chat(message.chat.id, message.from_user.id)
    if rez.error_code ==3:
        return bot.send_message(message.chat.id, "Бот временно не доступен")
    # Конец блока проверок и создания пользователей и чата в БД

    user = message.from_user
    welcome_text = f"Привет, {user.first_name}!\nЯ просто ботик котик.\nВведи /help для списка команд."
    bot.reply_to(message, welcome_text)

    # Можно отправить сообщение с клавиатурой
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔮 Режим ИИ GigaChat SBER")
    btn2 = types.KeyboardButton("🔮 Режим ИИ GPT 4 Mini")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
Доступные команды:
/start - начать работу с ботом
/help - получить справку по командам
/about - информация о боте

Также попробуйте нажать на кнопки!
"""
    bot.reply_to(message, help_text)


@bot.message_handler(func = lambda message:  "🔮 Режим ИИ" in message.text)
def enable_ai_mode(message):
    if message.text == "🔮 Режим ИИ GigaChat SBER":
        user_states[message.chat.id] =  {"ai_mode_sber": True}
    elif message.text == "🔮 Режим ИИ GPT 4 Mini":
        user_states[message.chat.id] = {"ai_mode_qpt": True}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_exit = types.KeyboardButton("Выйти из режима ИИ")
    markup.add(btn_exit)
    bot.send_message(message.chat.id, "Введите ваш запрос:", reply_markup=markup)


@bot.message_handler(func = lambda message: message.text == "Выйти из режима ИИ")
def exit_ai_mode(message):
    if message.chat.id in user_states:
        del user_states[message.chat.id]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔮 Режим ИИ GigaChat SBER")
    btn2 = types.KeyboardButton("🔮 Режим ИИ GPT 4 Mini")
    markup.add(btn1, btn2)

    bot.send_message(message.chat.id,
                     "Режим ИИ деактивирован.",
                     reply_markup=markup)

@bot.message_handler(func= lambda message:message.chat.id in user_states and user_states[message.chat.id].get('ai_mode_sber'))
def get_ai_answer_sber(message):

    answer = ai.ask_gigachat(message.chat.id, message.text)
    if answer is False:
        bot.send_message(message.chat.id, "Ошибка ИИ")
        return

    bot.send_message(message.chat.id, answer)


@bot.message_handler(func= lambda message:message.chat.id in user_states and user_states[message.chat.id].get('ai_mode_qpt'))
def get_ai_answer_qpt(message):

    answer = qpt.ask_qpt(message.chat.id, message.text)
    if answer["result"] is False:
        bot.send_message(message.chat.id, "Ошибка ИИ")
        return

    bot.send_message(message.chat.id, answer["answer"])


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    rez = db.save_massage(message.id, message.from_user.id, message.date, message.text)
    if rez.result is False:
        return bot.send_message(message.chat.id, "Бот временно не доступен")


    else:
        bot.send_message(message.chat.id, f"Мяу")



# Обработчик ошибок
@bot.message_handler(func=lambda message: True)
def error_handler(message):
    try:
        # Пытаемся обработать сообщение
        pass
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке вашего запроса.")


if __name__ == '__main__':
    logger.info("Бот запущен!")
    bot.infinity_polling()