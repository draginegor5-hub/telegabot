
import psycopg2
import os
from click import password_option
from dotenv import load_dotenv


class Response:
    def __init__(self, result: bool, error_code: int = 0, comment: str = "", data: dict = None):

        """коды ошибок:
        1 - Не найден Пользователь!
        2 - Пользователь уже существует!
        3 - Ошибка подключения к БД!
        4 - Чат уже существует!
        5 - Чат не найден!
        """

        self.result = result
        self.error_code = error_code
        self.comment = comment
        self.data = data

    def dict(self):
        return {
            "result": self.result,
            "error_code": self.error_code,
            "comment": self.comment,
            "data" : self.data
        }

load_dotenv()
DB = os.getenv("DB")

if not DB:
    raise ValueError("Токен не найден! Проверьте файл .env")

#внутренняя
def check_user (id_user):
    conn = None
    try:
        conn = psycopg2.connect(dbname='Telegram', user='postgres', password=DB, host='postgres')
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM users WHERE users_id = %s LIMIT 1', (str(id_user),))
            user = curs.fetchall()
        if not user:
            return Response(result=False, error_code=1)
        else:
            return Response(result=True)
    except:
        return Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()
#внутренняя
def check_chat (chat_id, user_id):
    conn = None
    try:
        conn = psycopg2.connect(dbname='Telegram', user='postgres', password=DB, host='postgres')
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM chats WHERE user_id = %s and chat_id = %s LIMIT 1', (str(user_id),str(chat_id),))
            chat = curs.fetchall()
        if not chat:
            return Response(result=False, error_code=5)
        else:
            return Response(result=True)
    except:
        return Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()



def create_user (id_user, first_name, last_name, username):
    if check_user(id_user).result is True:
        return Response(result=False, error_code=2, comment='Пользователь уже существует!')

    conn = None
    try:
        conn = psycopg2.connect(dbname='Telegram', user='postgres', password=DB, host='postgres')
        with conn.cursor() as curs:
            curs.execute('insert into users '
                             '(users_id, first_name, last_name, username)'
                            'values (%s,%s,%s,%s)', (id_user,first_name,last_name,username))
            conn.commit()
            return  Response(result=True)
    except:
        if conn:
            conn.rollback()
            return Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()

#внутренняя
def save_massage (message_id, user_id, date, text):
    conn = None
    try:
        conn = psycopg2.connect(dbname='Telegram', user='postgres', password=DB, host='postgres')

        with conn.cursor() as curs:
            curs.execute('insert into messages '
                         '(message_id, user_id, date, text)'
                         'values (%s,%s,%s,%s)', (message_id, user_id, date, text))
        conn.commit()
        return Response(result=True)
    except:
        if conn:
            conn.rollback()
        return Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()

#внутренняя
def save_chat (chat_id, user_id):
    if check_chat(chat_id, user_id).result is True:
        return Response(result=False,error_code=4)

    conn = None
    try:
        conn = psycopg2.connect(dbname='Telegram', user='postgres', password=DB, host='postgres')
        with conn.cursor() as curs:
            curs.execute('insert into chats '
                             '(chat_id, user_id)'
                            'values (%s,%s)', (str(chat_id), str(user_id)))
            conn.commit()
            return Response(result=True)
    except:
        if conn:
            conn.rollback()
            return Response(result=False,error_code=3)
    finally:
        if conn:
            conn.close()

#внутренняя
def save_ai_message (chat_id, timestamp, role, content):

    conn = None
    try:
        conn = psycopg2.connect(dbname='Telegram', user='postgres', password=DB, host='postgres')
        with conn.cursor() as curs:
            curs.execute('insert into ai_messages'
                             '(chat_id, timestamp, role, content)'
                            'values (%s,%s,%s,%s)', (str(chat_id), timestamp,role,content))
            conn.commit()
            return Response(result=True)
    except:
        if conn:
            conn.rollback()
            return Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()


def get_users (id_user):

    conn = None
    try:
        conn = psycopg2.connect(dbname = 'Telegram', user = 'postgres', password = DB, host = 'localhost')
        with conn.cursor() as curs:

            if id_user == 'all':
                curs.execute('select * from users')
            else:
                curs.execute('select * from users where users_id = %s', (id_user,))

            columns = [desc[0] for desc in curs.description]
            rez = curs.fetchall()
            rez = [dict(zip(columns,row)) for row in rez]

            return  Response (result=True, data=rez)
    except:
        return  Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()

def delete_users (id_user):

    if check_user(id_user).result is False:
        return Response(result=False, error_code=1, comment='Не найден пользователь')

    conn = None
    try:
        conn = psycopg2.connect(dbname = 'Telegram', user = 'postgres', password = DB, host = 'postgres')
        with conn.cursor() as curs:
            curs.execute('delete from users where users_id = %s', (id_user,))
            conn.commit()
            return Response(result=True)
    except:
        if conn:
            conn.rollback()
            return Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()

def update_user (id_user, first_name, last_name, username):
    if check_user(id_user).result is False:
        return Response(result=False, error_code=1, comment='Не найден пользователь')

    conn = None
    try:
        conn = psycopg2.connect(dbname='Telegram', user='postgres', password=DB, host='postgres')
        with conn.cursor() as curs:
            curs.execute('update users '
                             'set  first_name= %s, last_name= %s, username= %s'
                            ' where users_id = %s'
                            , (first_name,last_name,username,id_user,))
            conn.commit()
            return Response(result=True)
    except:
        if conn:
            conn.rollback()
            return Response(result=False, error_code=3)
    finally:
        if conn:
            conn.close()


