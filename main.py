import time

import telebot
from telebot import types
import sqlite3
import pytesseract
import cv2
import numpy as np

import creator
import creator_pub
import io


ocr_path = "D:\\App(x86)\\tesseract.exe"

bot = telebot.TeleBot('6770432743:AAH8Y03sR7yIf5F-wChVu3MOn9eyc9f041c')


afisha_1 = 'Restoran'
afisha_2 = 'Pub'
button_ok = 'Текст Норм'
message_1 = "Отправь фото или текст меню"
message_1_corect = 'Отредактируй текст и перешли его'
message_2 = "Уже жду список матчей"
message_error = "Что ты мне написала, я шарю а 3 команды..."
message_help = ("/start - начать заново\n/erase - стереть\n/add_image_to_rest - добавить фото блюда\n/add_image_to_pub - добавить эмблему команды")

def main_request(id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(afisha_1)
    markup.add(btn1)
    btn2 = types.KeyboardButton(afisha_2)
    markup.add(btn2)
    bot.send_message(id, "Что делаем?", reply_markup=markup)

def set_task(id,task):
    query = f"UPDATE user_task SET task = ? WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (task, id))
    connection.commit()

def add_menu(id,menu):
    query = f"UPDATE user_task SET text = ? WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (menu, id))
    connection.commit()

def get_menu(id):
    query = f"SELECT text FROM user_task WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    return result[0]


@bot.message_handler(commands=['start'])
def start(message):
    id = message.from_user.id
    query = "SELECT EXISTS(SELECT 1 FROM user_task WHERE id = ?);"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()[0]
    if result != 1:
        sql = "INSERT INTO user_task (id,task) VALUES (?,?)"
        cursor.execute(sql, (id,"NONE"))
    else:
        query = f"UPDATE user_task SET task = ? WHERE id = ?;"
        cursor.execute(query, ('NONE', id))
    connection.commit()

    main_request(id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    id = message.from_user.id
    query = f"SELECT task FROM user_task WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    if result[0] == 'NONE':
        if message.text == afisha_1:
            bot.send_message(message.from_user.id,message_1,reply_markup=types.ReplyKeyboardRemove())
            set_task(id,"RESTORAN")

        elif message.text == afisha_2:
            bot.send_message(message.from_user.id,message_2,reply_markup=types.ReplyKeyboardRemove())
            set_task(id,"PUB")
        else:
            bot.send_message(message.from_user.id, message_error, reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(message.from_user.id, message_help, reply_markup=types.ReplyKeyboardRemove())
            main_request(message.from_user.id)
    elif result[0] == 'RESTORAN':
        if message.text == button_ok:
            menu = get_menu(id)
            date = menu.splitlines()[0]
            time = menu.splitlines()[1]
            menu = '\n'.join(menu.splitlines()[2:])

            image = creator.create('background.png', date, time, menu, 'D:\\rest_lanches')
            bot.send_photo(message.from_user.id, image)
        else:
            date = message.text.splitlines()[0]
            time = message.text.splitlines()[1]
            menu = '\n'.join(message.text.splitlines()[2:])
            #print(menu)
            image = creator.create('background.png',date,time,menu,'D:\\rest_lanches')
            image.save("temp.png")
            with open("temp.png", "rb") as file:
                bot.send_document(message.chat.id, document=file)
    elif result[0] == 'PUB':

        image = creator_pub.create('background.png',message.text,'D:\\pub_emblems')

        image.save("temp.png")
        with open("temp.png", "rb") as file:
            bot.send_document(message.chat.id, document=file)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    id = message.from_user.id
    query = f"SELECT task FROM user_task WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    if result[0] == 'NONE':
        bot.send_message(message.from_user.id, message_error, reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.from_user.id, message_help, reply_markup=types.ReplyKeyboardRemove())
        main_request(message.from_user.id)
    elif result[0] == 'RESTORAN':

        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        file_path = file_info.file_path
        file_bytes = bot.download_file(file_path)
        np_array = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        pytesseract.pytesseract.tesseract_cmd = ocr_path
        menu = pytesseract.image_to_string(image, config='--psm 6', lang='rus')
        add_menu(id,menu)
        bot.send_message(message.from_user.id, menu, reply_markup=types.ReplyKeyboardRemove())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(button_ok)
        markup.add(btn1)
        bot.send_message(message.from_user.id, message_1_corect, reply_markup=markup)


while True:
    try:
        bot.polling(non_stop=True, interval=0)
    except Exception as e:
        print(e)
        time.sleep(5)
        continue