import os
import sqlite3
import telebot
from Pars_wiki import *
from koordinati import *
from marshrut import *

bot = telebot.TeleBot('6106225915:AAHnu2uBWMHvmHFCRlB0vsGc8VSmlZoDO24')

@bot.message_handler(commands=['start', 'hello'])
def start_bot(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')

@bot.message_handler(content_types=['text'])
def search_city(message):
    hello = ['привет', 'хай', 'hello', 'hi', 'здравствуй', 'здравствуйте']
    if message.text.lower() in hello:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')

    else:
        bot.send_message(message.chat.id, 'Ваш запрос обрабатывается...')
        description=pars_wiki(message.text, message.from_user.id)
        if description != False:
            f = open(f"img/{message.chat.id}.txt", "w", encoding="utf8")
            print(message.text, file=f)
            f.close()
            bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000001.jpg','rb')),
                                                   telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000002.jpg','rb')),
                                                   telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000003.jpg','rb')),
                                                   telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000004.jpg','rb'))])
            for i in range(1,5):
                os.remove(f'./img/{message.from_user.id}/00000{i}.jpg')

            bot.send_message(message.chat.id,description)
            bot.delete_message(message.chat.id, message.message_id+1)
            markup=telebot.types.InlineKeyboardMarkup()
            KY=telebot.types.InlineKeyboardButton(text="Да",callback_data="KYES")
            KN=telebot.types.InlineKeyboardButton(text="Нет",callback_data="KNO")
            markup.add(KY,KN)
            bot.send_message(message.chat.id,"Хотите увидеть достопримечательности этого города",reply_markup=markup)


        else:
            bot.delete_message(message.chat.id, message.message_id + 1)
            bot.send_message(message.chat.id, 'Город по вашему запросу не найден. Попробуйте снова')

@bot.callback_query_handler(func=lambda call: call.data in ["KYES","KNO"])
def dostoprim(call):
    if call.data=="KYES":
        bot.send_message(call.message.chat.id, 'Ваш запрос обрабатывается...')
        kor=[]
        f=open("Attractions.txt","r",encoding="utf8")
        BD=f.readlines()
        f.close()
        f=open(f"img/{call.message.chat.id}.txt","r",encoding="utf8")
        city=f.readlines()
        f.close()
        city=city[0].rstrip()

        try:
            for i in BD:
                if i.find(city)!=-1:
                    mas=i.split(":")
                    mas=mas[1].rstrip().split(",")
                    for q in mas:
                        e=q+" "+city
                        kor.append(koordinati(e))
                    print(kor)
                    por=driver(kor)
                    print(por)
                    markup = telebot.types.InlineKeyboardMarkup()
                    gor=""
                    for w in por:
                        gor+=mas[w-1]+","
                        KN = telebot.types.InlineKeyboardButton(text=mas[w-1], callback_data=mas[w-1])
                        markup.add( KN)

                    bot.send_message(call.message.chat.id, f"Достропримечательства города {city} лучше поситить в следующем порядке {gor} если хотите узнать о чёмнибудь по подробние нажмите на кнопки ниже", reply_markup=markup)
                    raise StopIteration
        except StopIteration:
            pass

@bot.callback_query_handler(func=lambda call: True)
def dostoprimichatelnosti(call):
    bot.send_message(call.message.chat.id, 'Ваш запрос обрабатывается...')
    description = pars_wiki(call.data, call.message.from_user.id)
    if description != False:
        bot.send_media_group(call.message.chat.id,
                             [telebot.types.InputMediaPhoto(open(f'./img/{call.message.from_user.id}/000001.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{call.message.from_user.id}/000002.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{call.message.from_user.id}/000003.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{call.message.from_user.id}/000004.jpg', 'rb'))])
        for i in range(1, 5):
            os.remove(f'./img/{call.message.from_user.id}/00000{i}.jpg')

        bot.send_message(call.message.chat.id, description)
        bot.delete_message(call.message.chat.id, call.message.message_id + 1)


bot.infinity_polling()

# connect = sqlite3.connect('city.db')
# curs = connect.cursor()
#
# res=curs.execute("""
# SELECT name FROM city
#
# """)
# print(res.fetchall())
#
# connect.close()

#---------------------------------------------------------------
# @bot.message_handler(content_types=['photo'])
# def get_photo(message):
#     markup=telebot.types.InlineKeyboardMarkup()
#     btn1 = telebot.types.InlineKeyboardButton('Save', callback_data='save')
#     markup.row(btn1)
#     btn2 = telebot.types.InlineKeyboardButton('No', callback_data='no')
#     markup.row(btn2)
#     bot.reply_to(message, 'Какое красивое фото!\nСохранить в БД?', reply_markup=markup)
#     #СКАЧИВАЕМ ОТПРАВЛЕННОЕ ФОТО
#
#
# @bot.callback_query_handler(func=lambda callback: callback.data in ['save','no'])
# def answer(callback):
#     if callback.data=='no':
#         #Удаляем последнее фото из БД , т.к. оно у нас автоматически при отправке
#         # будет сохраняться в БД
#         bot.send_message(callback.message.chat.id, 'Фото не будет сохранено в базе данных!')
#     else:
#         bot.send_message(callback.message.chat.id, 'Фото успешно сохранено!')
