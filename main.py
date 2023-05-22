import os
import sqlite3
import telebot
import requests
from Pars_wiki import *
from koordinati import *
from marshrut import *

bot = telebot.TeleBot('6106225915:AAHnu2uBWMHvmHFCRlB0vsGc8VSmlZoDO24')

@bot.message_handler(commands=['start', 'hello'])
def start_bot(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')

@bot.message_handler(commands=['city'])
def search_city(message):
    bot.send_message(message.chat.id, "Введите название города, о котором хотели бы найти информацию")
    bot.register_next_step_handler(message, city)

@bot.message_handler(commands=['search'])
def search_organizations(message):
    bot.send_message(message.chat.id, "Введите название магазина/организации, которую хотели бы найти поблизости")
    bot.register_next_step_handler(message, geolocation)


def city(message):
    message_user = message.text
    print(message_user)
    bot.send_message(message.chat.id, 'Ваш запрос обрабатывается...')
    description = pars_wiki(message_user, message.from_user.id)
    if description != False:
        f = open(f"img/{message.chat.id}.txt", "w", encoding="utf8")
        print(message.text, file=f)
        f.close()
        bot.send_media_group(message.chat.id,
                             [telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000001.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000002.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000003.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000004.jpg', 'rb'))])
        for i in range(1, 5):
            os.remove(f'./img/{message.from_user.id}/00000{i}.jpg')

        bot.send_message(message.chat.id, description)
        bot.delete_message(message.chat.id, message.message_id + 1)
        markup = telebot.types.InlineKeyboardMarkup()
        KY = telebot.types.InlineKeyboardButton(text="Да", callback_data="KYES")
        KN = telebot.types.InlineKeyboardButton(text="Нет", callback_data="KNO")
        markup.add(KY, KN)
        bot.send_message(message.chat.id, "Хотите увидеть достопримечательности этого города", reply_markup=markup)

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


#ФУНКЦИИ , КОТОРЫЕ ОТВЕЧАЮТ ЗА ФУНКЦИОНАЛ ГЕОЛОКАЦИИ И ПОИСКА БЛИЖАЙШЕЙ ОРГАНИЗАЦИИ

def geolocation(message):
    message_user = message.text
    print(message_user)
    # Создаем кнопку с запросом геолокации
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="🌐 Отправить геолокацию", request_location=True)
    keyboard.add(button)
    # Отправляем пользователю сообщение с кнопкой
    bot.send_message(message.chat.id, "👽 Нажмите кнопку для отправки геолокации", reply_markup=keyboard)
    bot.register_next_step_handler(message, process_shop, message_user)

# Обработчик ввода магазина/организации geolocation
def process_shop(message, mes_user):
    # Получаем координаты геолокации
    latitude = message.location.latitude
    longitude = message.location.longitude

    # Вызываем функцию для поиска магазинов и передаем идентификатор пользователя
    find_shops(message.chat.id, mes_user, latitude, longitude)


# Функция для поиска магазинов
def find_shops(user_id, shop, lat, lon):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("✅ Главное меню")
    item2 = telebot.types.KeyboardButton("📢 Информация")
    markup.add(item1,item2)

    req = str(lon) + ',' + str(lat)
    PARAMS = {
        "apikey": "10a9f041-f0b0-4821-89a5-ab19250b8c72",
        "text": shop,
        "lang": "ru_RU",
        "type": "biz",
        "results": "5",
        "ll": req,
        "spn": "0.021206,0.021055",
        "rspn": "1"
    }
    request = requests.get(url="https://search-maps.yandex.ru/v1/", params=PARAMS)
    json_data = request.json()

    if "features" in json_data and len(json_data["features"]) > 0:
        # Магазины найдены, выводим информацию
        coord_str1 = json_data["features"][0]["geometry"]["coordinates"][0]
        coord_str2 = json_data["features"][0]["geometry"]["coordinates"][1]
        shop_addr = json_data["features"][0]["properties"]["CompanyMetaData"]["address"]
        shop_hours = json_data["features"][0]["properties"]["CompanyMetaData"]["Hours"]["text"]
        #shop_category = json_data["features"][0]["properties"]["CompanyMetaData"]["Categories"][1]["name"]
        shop_name = json_data["features"][0]["properties"]["CompanyMetaData"]["name"]
        bot.send_message(user_id, f'{shop_name}\nАдрес: {shop_addr}\nВремя работы: {shop_hours}')
        map_link = f"http://maps.yandex.ru/?ll={coord_str1},{coord_str2}&spn=0.067205,0.018782&z=15&l=map,stv"
        bot.send_location(user_id, coord_str2, coord_str1, reply_markup=markup)
    else:
        # Ничего не найдено
        bot.send_message(user_id, "😥 По вашему запросу вблизи ничего не найдено", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def hi(message):
    hello = ['привет', 'хай', 'hello', 'hi', 'здравствуй', 'здравствуйте']
    if message.text.lower() in hello:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')

bot.infinity_polling()


