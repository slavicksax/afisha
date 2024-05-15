import re
import sys
import time
import traceback
import telebot
from telebot import types
import sqlite3
import pytesseract
from PIL import Image
import numpy as np
from telebot.types import ReplyKeyboardRemove

import StableDiff3
import creator
import creator_pub
import io
from googletrans import Translator


rest_path = '/root/rest_path'
pub_path = '/root/pub_path'
ocr_path = r"/usr/bin/tesseract"

rest_bg = 'restbackground.png'
pub_bg = 'pubbackground.png'

bot = telebot.TeleBot('6770432743:AAH8Y03sR7yIf5F-wChVu3MOn9eyc9f041c')


afisha_1 = 'Restoran'
afisha_2 = 'Pub'
creator_ = 'Photo Generation'
finish_task_btn = '/Finish'
button_ok = 'Текст Норм'
message_1 = "Отправь фото или текст меню"
message_1_corect = 'Отредактируй и перешли'
message_2 = "Уже жду список матчей"
message_error = "Что ты мне написала, я шарю а 3 команды..."
message_help = ("/start - начать заново\n/add_image_to_rest - добавить фото блюда\n/add_image_to_pub - добавить эмблему команды\n/set_rest_back - изменить фон ресторана\n/set_pub_back - изменить фон паба")




def fin_key():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(finish_task_btn)
    markup.add(btn1)
    return markup
def main_request(id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(afisha_1)
    markup.add(btn1)
    btn2 = types.KeyboardButton(afisha_2)
    markup.add(btn2)
    btn3 = types.KeyboardButton(creator_)
    markup.add(btn3)
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


def get_task(id):
    query = f"SELECT task FROM user_task WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    return result[0]
def get_menu(id):
    query = f"SELECT text FROM user_task WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    return result[0]

@bot.message_handler(commands=['set_rest_back'])
def set_r(message):
    set_task(message.from_user.id,'BACK_REST')
    bot.send_message(message.from_user.id, 'Отправь фон ресторана', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['set_pub_back'])
def set_p(message):
    set_task(message.from_user.id,'BACK_PUB')
    bot.send_message(message.from_user.id, 'Отправь фон паба', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['add_image_to_pub'])
def add_p(message):
    set_task(message.from_user.id, 'ADD_PUB')
    bot.send_message(message.from_user.id, 'Отправь название команды', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['add_image_to_rest'])
def add_r(message):
    set_task(message.from_user.id, 'ADD_REST')
    bot.send_message(message.from_user.id, 'Отправь название блюда', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['stop'])
def stop(message):
    bot.stop_polling()
#	bot.stop_polling()
   # a.split()


@bot.message_handler(commands=['Finish'])
def finish(message):
    set_task(message.from_user.id,'NONE')
    main_request(message.from_user.id)



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
    try:
        id = message.from_user.id
        result = get_task(id)
        if result == 'NONE':
            if message.text == afisha_1:
                bot.send_message(message.from_user.id, message_1, reply_markup=types.ReplyKeyboardRemove())
                set_task(id, "RESTORAN")
            elif message.text == creator_:
                bot.send_message(message.from_user.id, 'Жду промт на английском и больше деталей',
                                 reply_markup=types.ReplyKeyboardRemove())
                set_task(id, "SD3")
            elif message.text == afisha_2:
                bot.send_message(message.from_user.id, message_2, reply_markup=ReplyKeyboardRemove())
                set_task(id, "PUB")
            else:
                bot.send_message(message.from_user.id, message_error, reply_markup=ReplyKeyboardRemove())
                bot.send_message(message.from_user.id, message_help, reply_markup=ReplyKeyboardRemove())
                main_request(message.from_user.id)
        elif result == 'RESTORAN':
            if message.text == button_ok:
                menu = get_menu(id)
                date = menu.splitlines()[0]
                time = menu.splitlines()[1]
                menu = '\n'.join(menu.splitlines()[2:])
                if not bool(re.fullmatch(r'\d{2}.\d{2}.\d{4}', date)):
                    bot.send_message(message.from_user.id, "Добавь дату первой строкой", reply_markup=ReplyKeyboardRemove())
                if not bool(re.fullmatch(r'\d{2}:\d{2}-\d{2}:\d{2}', time)):
                    bot.send_message(message.from_user.id, "Добавь время второй строкой", reply_markup=ReplyKeyboardRemove())
                image = creator.create(rest_bg, date, time, menu, rest_path)
                bot.send_photo(message.from_user.id, image)
            else:

                date = message.text.splitlines()[0]
                time = message.text.splitlines()[1]
                menu = '\n'.join(message.text.splitlines()[2:])
                # print(menu)
                image = creator.create(rest_bg, date, time, menu, rest_path)
                image.save("temp.png")
                with open("temp.png", "rb") as file:
                    bot.send_document(message.chat.id, document=file)
        elif result == 'PUB':
            image = creator_pub.create(pub_bg, message.text, pub_path)
            image.save("temp.png")
            with open("temp.png", "rb") as file:
                bot.send_document(message.chat.id, document=file)
        elif result == 'ADD_REST' or result == 'ADD_PUB':
            connection = sqlite3.connect('my_database.db')
            cursor = connection.cursor()
            query = f"UPDATE user_task SET  text = ? WHERE id = ?;"
            cursor.execute(query, (message.text, id))
            connection.commit()
            bot.send_message(message.from_user.id, 'Отправь фото', reply_markup=types.ReplyKeyboardRemove())
        elif result == 'SD3':
            translator = Translator(service_urls=['translate.google.com'])

            translation = translator.translate(message.text, src='ru', dest='en')

            image = StableDiff3.getImage(translation.text)
            image.name = 'ans.png'
            bot.send_document(message.chat.id, document=image)
            bot.send_message(message.chat.id,translation.text)
            #bot.send_photo(message.chat.id,image)
    except Exception as e:
        bot.send_message(message.from_user.id, traceback.format_exc(), reply_markup=types.ReplyKeyboardRemove())
        print('Ошибка:\n', traceback.format_exc())







@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        id = message.from_user.id
        result = get_task(id)
        if result == 'NONE' or result == 'PUB':
            bot.send_message(message.from_user.id, message_error, reply_markup=ReplyKeyboardRemove())
            bot.send_message(message.from_user.id, message_help, reply_markup=ReplyKeyboardRemove())
            main_request(message.from_user.id)
        elif result == 'RESTORAN':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            pytesseract.pytesseract.tesseract_cmd = ocr_path
            menu = pytesseract.image_to_string(image, config='--psm 6', lang='rus')
            add_menu(id, menu)
            bot.send_message(message.from_user.id, menu, reply_markup=types.ReplyKeyboardRemove())
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(button_ok)
            markup.add(btn1)
            bot.send_message(message.from_user.id, message_1_corect, reply_markup=markup)
        elif result == 'ADD_REST':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            result = get_menu(id)
            image.save(rest_path + '/' + result + '.png')
            bot.send_message(message.from_user.id, "Добавлено", reply_markup=ReplyKeyboardRemove())
            set_task(id, 'NONE')
        elif result == 'ADD_PUB':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            result = get_menu(id)
            image.save(pub_path + '/' + result + '.png')
            bot.send_message(message.from_user.id, "Добавлено", reply_markup=ReplyKeyboardRemove())
            set_task(id, 'NONE')
        elif result == 'BACK_PUB':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            image.save(pub_bg)
            bot.send_message(message.from_user.id, "Добавлено", reply_markup=ReplyKeyboardRemove())
            set_task(id, 'NONE')
        elif result == 'BACK_REST':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            image.save(rest_bg)
            bot.send_message(message.from_user.id, "Добавлено", reply_markup=ReplyKeyboardRemove())
            set_task(id, 'NONE')
    except:
        bot.send_message(message.from_user.id, traceback.format_exc(), reply_markup=ReplyKeyboardRemove())
        print('Ошибка:\n', traceback.format_exc())



@bot.message_handler(content_types=['document'])
def save_document(message):
    try:
        id = message.from_user.id
        result = get_task(id)
        if result == 'NONE' or result == 'PUB':
            bot.send_message(message.from_user.id, message_error, reply_markup=ReplyKeyboardRemove())
            bot.send_message(message.from_user.id, message_help, reply_markup=ReplyKeyboardRemove())
            main_request(message.from_user.id)
        elif result == 'BACK_REST':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            image.save(rest_bg)
            bot.send_message(message.from_user.id,"Добавлено", reply_markup=ReplyKeyboardRemove())

        elif result == 'BACK_PUB':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            image.save(pub_bg)
            bot.send_message(message.from_user.id, "Добавлено", reply_markup=ReplyKeyboardRemove())
            set_task(id, 'NONE')
        elif result == 'ADD_REST':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            result = get_menu(id)
            image.save(rest_path + '/' + result + '.png')
            bot.send_message(message.from_user.id, "Добавлено", reply_markup=ReplyKeyboardRemove())
            set_task(id, 'NONE')
        elif result == 'ADD_PUB':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_bytes = io.BytesIO(downloaded_file)
            image = Image.open(image_bytes)
            result = get_menu(id)
            image.save(pub_path + '/' + result + '.png')
            bot.send_message(message.from_user.id, "Добавлено", reply_markup=ReplyKeyboardRemove())
            set_task(id,'NONE')
    except:
        bot.send_message(message.from_user.id, traceback.format_exc(), reply_markup=ReplyKeyboardRemove())
        print('Ошибка:\n', traceback.format_exc())



bot.polling(non_stop=True, interval=0)

while True:
    try:
        bot.polling(non_stop=True, interval=0)
    except Exception as e:
        print(e)
        time.sleep(5)
        continue

