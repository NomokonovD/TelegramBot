import os
import sqlite3
import telebot
import requests
from Pars_wiki import *
from koordinati import *
from route import *

bot = telebot.TeleBot('6106225915:AAHnu2uBWMHvmHFCRlB0vsGc8VSmlZoDO24')

#При команде /start или /hello выводится приветственное сообщение , где кратко описан функционал
@bot.message_handler(commands=['start', 'hello'])
def start_bot(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')

#При команде /city
@bot.message_handler(commands=['city'])
def search_city(message):
    bot.send_message(message.chat.id, "Введите название города, о котором хотели бы найти информацию")
    bot.register_next_step_handler(message, city)

#При команде /search
@bot.message_handler(commands=['search'])
def search_organizations(message):
    bot.send_message(message.chat.id, "Введите название магазина/организации, которую хотели бы найти поблизости")
    bot.register_next_step_handler(message, geolocation)


def city(message):
    message_user = message.text #ожидается ввод от пользователя после команды /city
    bot.send_message(message.chat.id, 'Ваш запрос обрабатывается...')
    description = pars_wiki(message_user, message.from_user.id, False) #вызов функции, в которой происохдит парсинг с википедии по запросу пользователя
    if description != False: #если информация по запросу найдена

        #отправка фотографий и описания города , по запросу пользователя
        bot.send_media_group(message.chat.id,
                             [telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000001.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000002.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000003.jpg', 'rb')),
                              telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000004.jpg', 'rb'))])
        #после отправки фотографий, которые хранились в папке с названием id пользователя, они удаляются
        for i in range(1, 5):
            os.remove(f'./img/{message.from_user.id}/00000{i}.jpg')

        bot.send_message(message.chat.id, description)
        bot.delete_message(message.chat.id, message.message_id + 1) #после отправки сообщений по запросу удаляется сообщение 'Ваш запрос обрабатывается...'
        #Создание кнопок с предложением о выводе списка достопримечательностей
        markup = telebot.types.InlineKeyboardMarkup()

        KY = telebot.types.InlineKeyboardButton(text="Да", callback_data=f"KYES:{message_user.capitalize()}")
        KN = telebot.types.InlineKeyboardButton(text="Нет", callback_data=f"KNO:{message_user.capitalize()}")
        markup.add(KY, KN)
        bot.send_message(message.chat.id, "Хотите увидеть достопримечательности этого города", reply_markup=markup)
    #если пользователь ввел не город , а рандомное слово , то выводится соответсвующее сообщение
    else:
        bot.delete_message(message.chat.id, message.message_id + 1)
        bot.send_message(message.chat.id, 'Город по вашему запросу не найден. Попробуйте снова')


@bot.callback_query_handler(func=lambda call: call.data.startswith(("KYES:", "KNO:")))
def attractions(call):
    city = call.data.split(":")[1] # получаем город, по которому пользователь хочет получить список достопримечательностей

    if call.data ==f"KYES:{city}": #Если пользователь выбрал "Да"
        bot.send_message(call.message.chat.id, 'Ваш запрос обрабатывается...')
        koordinaten=[]

        #Получаем ID города из БД, о котором делал запрос пользователь
        connection = sqlite3.connect("cities.db")
        cursor = connection.cursor()
        query_cityID = '''SELECT city_id
                       FROM city
                       WHERE name_city = ?'''

        cursor.execute(query_cityID, (city,))

        city_id = cursor.fetchall()[0][0]  #ID города из DATABASE
        connection.close()

        #Получаем все достопримечательности из БД по ID города
        connection = sqlite3.connect("cities.db")
        cursor = connection.cursor()
        query = '''SELECT name_attraction
                       FROM attraction
                       WHERE city_id = ?'''
        # Выполнение запроса с использованием ID города
        cursor.execute(query, (city_id,))
        attractions = cursor.fetchall()

        # Преобразование результатов в массив названий достопримечательностей
        BD = [attraction[0] for attraction in attractions]
        connection.close()
        print(BD)
        # Закрытие соединения с базой данных

        for q in BD:
            e = q + " " + city
            koordinaten.append(koordinatens(e))

        sorted_attractions = driver(koordinaten)

        markup = telebot.types.InlineKeyboardMarkup()
        gor = ""
        for w in sorted_attractions:
            gor += BD[w - 1] + ","
            KN = telebot.types.InlineKeyboardButton(text=BD[w - 1], callback_data=BD[w - 1])
            markup.add(KN)

        bot.send_message(call.message.chat.id,
                         f"Достропримечательства города {city} лучше поситить в следующем порядке {gor} если хотите узнать о чёмнибудь по подробние нажмите на кнопки ниже",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def dostoprimichatelnosti(call):
    bot.send_message(call.message.chat.id, 'Ваш запрос обрабатывается...')
    print(call.data)
    description = pars_wiki(call.data, call.message.from_user.id, True)
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


#ФУНКЦИИ , КОТОРЫЕ ОТВЕЧАЮТ ЗА ГЕОЛОКАЦИЮ И ПОИСК БЛИЖАЙШЕЙ ОРГАНИЗАЦИИ
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
        "apikey": "f60ca0c9-9813-4936-881f-e625597d9c7b",
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

#приветсвенное сообщение , если пользователь не воспользовался командой /start
@bot.message_handler(content_types=['text'])
def hi(message):
    hello = ['привет', 'хай', 'hello', 'hi', 'здравствуй', 'здравствуйте']
    if message.text.lower() in hello:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')

bot.infinity_polling()


