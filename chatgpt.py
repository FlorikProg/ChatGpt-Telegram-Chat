from g4f.client import Client
import sqlite3
from sqlite3 import Error
from threading import Lock, current_thread
import telebot
from telebot import types
bot = telebot.TeleBot("6807556217:AAETznOc9iRwu_TfqMbyzw2pGj3xiLduAcc")

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection_pool = {}
        self.lock = Lock()
          # Create the table if it does not exist
        self.create_table()

    def create_table(self):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_id (
                    id INTEGER PRIMARY KEY,
                    tokens INTEGER
                )
            """)
            connection.commit()
        except Error as e:
            print(e)

    def get_connection(self):
        thread_id = id(current_thread())
        if thread_id not in self.connection_pool:
            self.connection_pool[thread_id] = sqlite3.connect(self.db_file)
        return self.connection_pool[thread_id]

    def add_user(self, user_id):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()

            # Check if the user already exists
            cursor.execute(f"SELECT id FROM login_id WHERE id = {user_id}")
            existing_user = cursor.fetchone()

            if existing_user is None:
                print(f"Adding user {user_id} to the database.")
                cursor.execute("INSERT INTO login_id VALUES(?, ?);", (user_id, 5))  # Set initial tokens to 5
                connection.commit()
                print(f"User {user_id} added successfully.")
            else:
                print(f"User {user_id} already exists in the database.")

        except Error as e:
            print(e)

    def get_tokens(self, user_id):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"SELECT tokens FROM login_id WHERE id = {user_id}")
            tokens = cursor.fetchone()
            return tokens[0] if tokens else None
        except Error as e:
            print(e)
            return None

    def update_tokens(self, user_id, new_tokens):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"UPDATE login_id SET tokens = {new_tokens} WHERE id = {user_id}")
            connection.commit()
        except Error as e:
            print(e)

    def add_tokens(self, user_id, additional_tokens):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            current_tokens = self.get_tokens(user_id)
            if current_tokens is not None:
                new_tokens = current_tokens + additional_tokens
                cursor.execute(f"UPDATE login_id SET tokens = {new_tokens} WHERE id = {user_id}")
                connection.commit()
                return new_tokens
            else:
                return None
        except Error as e:
            print(e)
            return None
    def user_exists(self, user_id):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"SELECT id FROM login_id WHERE id = {user_id}")
            existing_user = cursor.fetchone()
            return existing_user is not None
        except Error as e:
            print(e)
            return False

    def getTokensByUserId(self, user_id):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"SELECT tokens FROM login_id WHERE id = {user_id}")
            tokens = cursor.fetchone()
            return tokens[0] if tokens else None
        except Error as e:
            print(e)
            return None

db = Database('users.db')
ADMIN_ID =  1529997307  # Replace with the actual admin ID

@bot.message_handler(commands=['start'])
def welcome(message):
    if not db.user_exists(message.chat.id):
        people_id = message.chat.id
        db.add_user(people_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    balance = types.KeyboardButton(text='Профиль😎')
    token = types.KeyboardButton(text='Купить Токены🪙')
    markup.add(balance, token)

    bot.send_message(message.chat.id, text='Привет друг!👋Этот бот использует ChatGpt 3.5🤖Просто напиши любой запрос и ChatGpt даст ответ😊Лучшие цены только в этом боте👌\nПо всем вопросам: @FlorikX', reply_markup=markup)





@bot.message_handler(commands=['add_tokens'])
def add_tokens(message):
    if message.chat.id == ADMIN_ID:
        try:
            _, user_id, additional_tokens = message.text.split()
            user_id = int(user_id)
            additional_tokens = int(additional_tokens)
            new_tokens = db.add_tokens(user_id, additional_tokens)
            if new_tokens is not None:
                bot.send_message(message.chat.id, f'🤖: Токены были зачисленны😊 Баланс: {new_tokens}, user_id={user_id}')
            else:
                bot.send_message(message.chat.id, '🤖: Пользователь не найден☹️.')
        except ValueError:
            bot.send_message(message.chat.id, '🤖Не правильная комманда. Используйте: /add_tokens {id} {amount}')
    else:
        bot.send_message(message.chat.id, 'Для этой комманды нужен админ статус🚫')

@bot.message_handler(content_types=['text'])
def talk(message):
    people_id = message.chat.id
    current_tokens = db.get_tokens(people_id)

    delete_message = bot.send_message(message.chat.id, 'Думаю⌛')

    if(message.text == 'Профиль😎'):
        tokens = db.getTokensByUserId(people_id)
        bot.send_message(message.chat.id, f'🪪Ваш профиль🪪:\nБаланс токенов🪙: {tokens}\nВаш ID🆔: {people_id}')
        return

    if(message.text == 'Купить Токены🪙'):
        mar = types.InlineKeyboardMarkup(row_width=True)
        button = types.InlineKeyboardButton(text='100 токенов = 100 руб', url='https://t.me/FlorikX')
        button1 = types.InlineKeyboardButton(text='200 токенов = 200 руб', url='https://t.me/FlorikX')
        button2 = types.InlineKeyboardButton(text='🔥250 токенов = 200 руб🔥', url='https://t.me/FlorikX')
        mar.add(button, button1, button2)
        tokens = db.getTokensByUserId(people_id)
        bot.send_message(message.chat.id, f'Для покупки токенов обратитесь к @FlorikX. \n 1 токен = 1 вопрос боту.', reply_markup=mar)
        return

    if current_tokens is not None and current_tokens > 0:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
    )
        bot.delete_message(message.chat.id, delete_message.message_id)
        bot.send_message(message.chat.id, response.choices[0].message.content)
        
        new_tokens = current_tokens - 1
        db.update_tokens(people_id, new_tokens)
    else:
        mark = types.InlineKeyboardMarkup(row_width=True)
        button = types.InlineKeyboardButton(text='100 токенов = 100 руб', url='https://t.me/FlorikX')
        button1 = types.InlineKeyboardButton(text='200 токенов = 200 руб', url='https://t.me/FlorikX')
        button2 = types.InlineKeyboardButton(text='🔥250 токенов = 200 руб🔥', url='https://t.me/FlorikX')
        mark.add(button, button1, button2)
        bot.send_message(message.chat.id, 'Упс...Похоже у вас закончились токены☹️\nЧтобы купить токены обратитесь к админу: @FlorikX', reply_markup=mark)





bot.infinity_polling(none_stop=True)