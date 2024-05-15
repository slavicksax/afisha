import asyncio
import json
import re
import sqlite3
import time

import numpy as np
import schedule
import threading
import telebot
from groq import Groq
from telebot import types

import weather_api

client = Groq(api_key="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")
bot = telebot.TeleBot("6459013789:AAHX3Mf2XpLKzvU9c8grdAM5rZDB2sAYW1Y")
WEATHER = 'WEATHER'


def set_task(id, task, p='task'):
    query = f"UPDATE user_task SET {p} = ? WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (task, id))
    connection.commit()
def add_time(id,time):
    tim = get_field(id,'time_')
    if tim == None:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        query = f"UPDATE user_task SET time_ = ? WHERE id = ?;"
        cursor.execute(query, (time,id))
        connection.commit()
    else:
        set_task(id,time + " " + tim,p='time_')


def get_field(id,field):
    query = f"SELECT {field} FROM user_task WHERE id = ?;"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    connection.commit()
    return result[0]
def get_task(id):
    query = "SELECT EXISTS(SELECT 1 FROM user_task WHERE id = ?);"
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()[0]
    if result != 1:
        sql = "INSERT INTO user_task (id,task) VALUES (?,?)"
        cursor.execute(sql, (id, "NONE"))
        connection.commit()
        return None
    else:
        query = f"SELECT task FROM user_task WHERE id = ?;"
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        connection.commit()
        return result[0]


def extract_time(text):
    pattern = r"\b\d{1,2}:\d{2}\b"
    match = re.search(pattern, text)
    if match:
        return match.group()
    else:
        return None


def get_answer(id ,promt):
    history = get_field(id,'history')
    messagess = [
        {
            "role": "system",
            # "content": "Ты Мегумин, отвечаешь на русском"
            "content": "you are a cute anime girl,answer in Russian"
        }]
    if history != None:
        parsed_data = json.loads(history)

        for p in parsed_data:
            messagess.append(p)
    messagess.append({
        "role": "user",
        "content": promt,
    })
    response = client.chat.completions.create(model='llama3-70b-8192', messages=messagess, temperature=0)
    messagess.append({"role": "assistant",
        "content": response.choices[0].message.content,})
    if len(messagess) > 7:
        set_task(id,json.dumps(messagess[-6:]),'history')
    else:
        set_task(id, json.dumps(messagess[1:]), 'history')
    return response.choices[0].message.content

@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:
        print(message.location.latitude, message.location.longitude)
        set_task(message.from_user.id, str(message.location.latitude) + " " + str(message.location.longitude),'coord')
        answer = get_answer(message.from_user.id,'Скажи что теперь ты знаешь где я нахожусь')
        bot.send_message(message.from_user.id,answer,reply_markup=types.ReplyKeyboardRemove())



@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    task = get_task(message.from_user.id)
    if task == WEATHER:
        if message.text == 'Отправить местоположение':
            print(message)
        time = extract_time(message.text)
        if time is None:
            answer = get_answer(message.from_user.id,'Скажи мне что ты не поняла что я сказал')
            bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
        else:

            answer = get_answer(message.from_user.id,f'Скажи мне что ты запомнила время {time} и попроси сказать где я нахожусь')
            hour, minute = time.split(':')
            if len(hour) == 1:
                time = '0' + time
            print(time)
            add_time(message.from_user.id, time)
            add_task(message.from_user.id, time)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('Отправить местоположение', request_location=True)
            markup.add(btn)
            bot.send_message(message.from_user.id, answer, reply_markup=markup)
            set_task(message.from_user.id, 'NONE')
    else:
        if message.text == 'Помоги':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.InlineKeyboardButton('Подписаться на погоду', callback_data='Помоги подписаться на погоду')
            markup.add(btn1)
            answer = get_answer(message.from_user.id,message.text)
            bot.send_message(message.from_user.id, answer, reply_markup=markup)
        elif message.text == 'Подписаться на погоду':
            set_task(message.from_user.id, WEATHER)
            answer = get_answer(message.from_user.id,'Спроси у меня в какое время я хочу, что бы ты напоминала мне о погоде')
            bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
        else:
            answer = get_answer(message.from_user.id,message.text)
            bot.send_message(message.from_user.id, answer)


def polling():
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(10)
            continue


def send(id):
    loc = get_field(id,'coord').split()
    temp = weather_api.get_weather(loc[0],loc[1])
    answer = get_answer(id,f'скажи мне что сейчас на улице {temp} градусов, и что ты пожелаешь при этом')
    bot.send_message(id, answer, reply_markup=types.ReplyKeyboardRemove())


def add_task(id,time):
    schedule.every().day.at(time).do(send, id=id)


def giggles():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, time_ FROM user_task")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in results:
        id = row[0]
        times = row[1]
        if times != None:
            for time_ in times.split():
                add_task(id,time_)
    while True:
        schedule.run_pending()
        time.sleep(10)



#schedule.every(10).seconds.do(send,id=1375937821)
thread1 = threading.Thread(target=polling)
thread1.start()
thread2 = threading.Thread(target=giggles)

thread2.start()


