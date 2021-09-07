# -*- coding: utf-8 -*-
import telebot
import re
import sqlite3

bot = telebot.TeleBot("Token")
password = '*******'
chat_observe = False
send_null_codes_info = False

db = sqlite3.connect('user_db.db', check_same_thread=False)
sql = db.cursor()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, f'Welcome {message.from_user.first_name}')


@bot.message_handler(commands=['uploadcodes'])
def upload_codes(message):
    global chat_observe, send_null_codes_info
    upload_pass = message.text.replace('/uploadcodes ', '').strip().split('\n')[0]
    if upload_pass.replace(' ', '') == password:
        restart()
        codes = re.findall(r'\w{5}-\w{5}-\w{5}-\w{5}-\w{5}', message.text.replace('/uploadcodes a7H6BvF66b', ''))
        while '' in codes:
            codes.remove('')
        if len(codes) > 100:
            bot.send_message(message.chat.id, 'Ошибка, можно загружать только 100 кодов')
            return 0
        for i in range(len(codes)):
            add_code(codes[i])
        if len(codes) == 0:
            return 0
        bot.send_message(-1001259856561, """Доступны коды для арены! Чтобы получить код:
            1. Напишите в личные сообщения чат-боту mw_arena_bot “/start”. Достаточно сделать это всего один раз, потом этот шаг можно пропускать.
            2. Напишите в в личные сообщения боту команду /getcode
            3. Один человек может получить один код
            """)
        chat_observe = False
    else:
        bot.send_message(message.chat.id, "Неправильный пароль")


@bot.message_handler(commands=['getcode'])
def get_code(message):
    global chat_observe, send_null_codes_info
    if len(db_codes().fetchall()) == 0:
        bot.send_message(message.from_user.id, 'Уже все коды разобрали, но я сообщу если будут еще')
        if not chat_observe:
            bot.send_message(-1001259856561, 'На сегодня всё, все коды разобрали, но я сообщу если будут еще')
            chat_observe = True
        return 0
    if (check_user_not_in_db(message.from_user.id)) and (message.chat.id == message.from_user.id):
        bot.send_message(message.from_user.id, get_db_code(message.from_user.id))
    elif check_user_in_db(message.from_user.id):
        bot.send_message(message.chat.id, 'ЕДХ - лучший формат магии, приходите в пятницу на вечер коммандера')
    elif message.chat.id != message.from_user.id:
        bot.send_message(message.chat.id, '/getcode работает только в личном чате с ботом')


@bot.message_handler(commands=['deletecodes'])
def deletecodes(message):
    sql = db.cursor()
    delete_pass = message.text.replace('/deletecodes', '').replace(' ', '').strip().split('\n')[0]
    if delete_pass == password:
        sql.execute("DELETE FROM codes")
        db.commit()
        bot.send_message(message.chat.id, 'Коды удалены')
    else:
        bot.send_message(message.chat.id, 'Неправильный пароль')


def restart():
    global chat_observe
    sql.execute("DELETE FROM users")
    db.commit()
    sql.execute("DELETE FROM codes")
    db.commit()
    chat_observe = False


def get_db_code(user_id):
    code = sql.execute(f"SELECT code FROM codes LIMIT 1").fetchall()[0][0]
    db.commit()
    sql.execute("DELETE from codes LIMIT 1")
    db.commit()
    sql.execute(f"INSERT INTO users VALUES({user_id})")
    db.commit()
    return code


def add_code(code):
    sql.execute(f"INSERT INTO codes VALUES(?)", (code,))
    db.commit()


def all_users():
    users =  sql.execute("""SELECT * FROM users""")
    db.commit()
    return users


def check_user_not_in_db(user_id):
    return len(sql.execute(f"""SELECT user_id FROM users WHERE user_id={user_id}""").fetchall()) == 0


def check_user_in_db(user_id):
    return len(sql.execute(f""" SELECT user_id FROM users WHERE user_id={user_id}""").fetchall()) == 1


def db_codes():
    db_codes = sql.execute("""SELECT * FROM codes""")
    db.commit()
    return db_codes


bot.polling(none_stop=True)
