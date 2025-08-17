
import database as db
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
api_key_qpt = os.getenv("api_key_qpt")

client = OpenAI(api_key=api_key_qpt)
MAX_HISTORY = 10
messages = []

def ask_qpt (chat_id, question):

    messages.append({"chat_id": chat_id, "history":{"role": "user", "content": question},  "timestamp": datetime.now().isoformat()})
    db.save_ai_message(chat_id,datetime.now().isoformat(), 'user',question)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=get_messages_for_response(chat_id) ,
            max_tokens=500,
            temperature=0.7
        )

        assistant_reply = response.choices[0].message.content
        messages.append({"chat_id": chat_id, "history": {"role": "assistant", "content": assistant_reply}, "timestamp": datetime.now().isoformat()})
        db.save_ai_message(chat_id, datetime.now().isoformat(), 'assistant', assistant_reply)

        rez = {"result": True, "answer": assistant_reply}
        clean_history_gpt(chat_id)

        return rez

    except Exception as e:
        rez = {"result": False, "answer": {e}}
        return rez


def get_messages_for_response (chat_id):
    messages_gpt = [
        {"role": "system", "content": "Ты — технический специалист, отвечающий на вопросы на русском языке."}
    ]
    for msg in messages:
        if msg["chat_id"] == chat_id:
            messages_gpt.append(msg["history"])
    return messages_gpt


def clean_history_gpt(chat_id):
    global messages
    chat_messages = []
    other_messages = []

    for msg in messages:
        if msg["chat_id"] == chat_id:
            chat_messages.append(msg)
        else:
            other_messages.append(msg)

    chat_messages.sort(key=lambda x: x["timestamp"])

    recent_messages = chat_messages[-10:]

    messages = other_messages + recent_messages

