
from gigachat import GigaChat
import os
from dotenv import load_dotenv
from gigachat.models import ChatCompletion
from collections import defaultdict
from datetime import datetime
import database as db

chat_histories = defaultdict(list)


load_dotenv()
api_key_sber = os.getenv("api_key_sber")

if not api_key_sber:
    raise ValueError("api_key_sber не найден! Проверьте файл .env")


def ask_gigachat(chat_id, question):
    try:
        user_message = {
            "chat_id": chat_id,
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": question
        }
        chat_histories[chat_id].append(user_message)

        savemessage = db.save_ai_message (chat_id, datetime.now().isoformat(), 'user', question)
        if savemessage is False:
            return ('Ошибка связи с БД')


        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in chat_histories[chat_id][-10:]  # Последние 10 сообщений
        ]

        giga = GigaChat(
            credentials=api_key_sber,
            verify_ssl_certs=False,
            timeout=30  # Таймаут в секундах
        )
        response = giga.chat({"messages": messages})
        answer = response.choices[0].message.content

        assistant_message = {
            "chat_id": chat_id,
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": answer
        }
        chat_histories[chat_id].append(assistant_message)

        savemessage = db.save_ai_message(chat_id, datetime.now().isoformat(), 'assistant', answer)
        if savemessage.result is False:
            return ('Ошибка связи с БД')

        trim_chat_history(chat_id)
        return answer


    except Exception as e:
        return f"Ошибка GigaChat API: {str(e)}"

def trim_chat_history(chat_id, max_messages=10):
    """Оставляет только последние max_messages сообщений в истории чата."""
    if chat_id in chat_histories:
        chat_histories[chat_id] = chat_histories[chat_id][-max_messages:]
