import os
import sqlite3
import telebot
import requests
from Pars_wiki import *
from koordinati import *
from route import *
from Weather import *
import config

bot = telebot.TeleBot(config.bot_token) #Все ключи и токены лежат в файле config

#При команде /start или /hello выводится приветственное сообщение , где описан функционал
@bot.message_handler(commands=['start', 'hello'])
def start_bot(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button=telebot.types.InlineKeyboardButton(text="✅ Главное меню", callback_data="menu")
    keyboard.add(button)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\n{config.welcome_message}',reply_markup=keyboard)

#Функция, которая запускает menu() после нажатия на кнопку [Главное меню]
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data=='menu':
        menu(call.message)

#В функции создаются кнопки главного меню
def menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="🏰 Найти информацию о городе")
    keyboard.add(button)
    button = telebot.types.KeyboardButton(text="🍎 Поиск магазина/организации")
    keyboard.add(button)
    bot.send_message(message.chat.id, config.menu_message, reply_markup=keyboard)

#Функция срабатывает на любые сообщения, которые отправляет пользователь (Идет проверка на ввод какой-либо команды)
@bot.message_handler(content_types=['text'])
def menu_flag(message):
    hello = ['привет', 'хай', 'hello', 'hi', 'здравствуй', 'здравствуйте','ку']

    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="✅ Главное меню")
    keyboard.add(button)
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()
    query = """SELECT attraction.name_attraction ||' '|| city.name_city
                FROM attraction
                INNER JOIN city
                ON attraction.city_id=city.city_id
                WHERE attraction.name_attraction=?"""
    cursor.execute(query, (message.text,))
    resultAttaraction = cursor.fetchone()
    conn.close()
    if message.text=='🏰 Найти информацию о городе':
        bot.send_message(message.chat.id, "Введите название города, о котором хотели бы найти информацию.\n\nЕсли хотите вернуться в меню, то нажмите на кнопку [✅ Главное меню]", reply_markup=keyboard)
        bot.register_next_step_handler(message, city)

    elif message.text=='🍎 Поиск магазина/организации':
        bot.send_message(message.chat.id, "Введите название магазина/организации, которую хотели бы найти поблизости.\n\nЕсли хотите вернуться в меню, то нажмите на кнопку [✅ Главное меню]",reply_markup=keyboard)
        bot.register_next_step_handler(message, geolocation)

    elif "🇷🇺 Да, хочу увидеть достопримечательности города" in message.text:
        citys=message.text.removeprefix('🇷🇺 Да, хочу увидеть достопримечательности города ')
        attractions(message,citys)

    elif "🔙 Нет, выйти в главное менню ⬅️" in message.text:
        menu(message)

    elif "⛅️ Хочу узнать погоду в городе " in message.text:
        citys = message.text.removeprefix('⛅️ Хочу узнать погоду в городе ')
        weather_bot(message, citys)

    elif resultAttaraction!=None:
        resultAttaraction=resultAttaraction[0]
        dostoprimichatelnosti(message,resultAttaraction)
    elif message.text=="✅ Главное меню":
        menu(message)
    elif message.text.lower() in hello:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')
    else:
        bot.send_message(message.chat.id,"❌ Такой команды нет ❌\n Произошел 🔙 переход в главное меню")
        menu(message)

def city(message):
    try:
        if message.text =="✅ Главное меню":
            menu(message)
        else:
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

                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,  row_width=1)

                conn = sqlite3.connect('cities.db')
                cursor = conn.cursor()
                query = "SELECT name_city FROM city WHERE name_city = ? or alter_name_city=?"
                cursor.execute(query, (message_user.title(), message_user.title(),))
                resultCity = cursor.fetchone()
                conn.close()
                citys = resultCity[0]

                KY = telebot.types.KeyboardButton(
                    text=f"🇷🇺 Да, хочу увидеть достопримечательности города {citys}", )
                KN = telebot.types.KeyboardButton(
                    text="🔙 Нет, выйти в главное менню ⬅️")
                KP=telebot.types.KeyboardButton(text=f"⛅️ Хочу узнать погоду в городе {citys}")
                markup.add(KY, KN,KP)
                conn = sqlite3.connect('cities.db')
                cursor = conn.cursor()
                # Запрос для проверки о наличии достопримечательности в БД
                query = '''SELECT attraction.name_attraction
                                    FROM attraction
                                    INNER JOIN city
                                    ON attraction.city_id=city.city_id
                                    WHERE city.name_city = ? or city.alter_name_city=?'''
                cursor.execute(query, (message_user.title(),message_user.title(),))
                # Извлечение результатов запроса
                attractions = cursor.fetchall()
                BD = [attraction[0] for attraction in attractions]

                if len(BD)>=3:
                    bot.send_message(message.chat.id, "Хотите увидеть достопримечательности этого города или узнать погоду? 🔮", reply_markup=markup)
                else:
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    KN = telebot.types.KeyboardButton(text="✅ Главное меню")
                    markup.add(KN,KP)
                    bot.send_message(message.chat.id, "Хотите узнать погоду в этом городе?\n\nЕсли хотите вернуться в меню, то нажмите на кнопку [✅ Главное меню",reply_markup=markup)
            #если пользователь ввел не город , а рандомное слово , то выводится соответсвующее сообщение
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                KN = telebot.types.KeyboardButton(text="✅ Главное меню")
                markup.add(KN)
                bot.delete_message(message.chat.id, message.message_id + 1)
                bot.send_message(message.chat.id, 'Город по вашему запросу не найден. Вернитесь в главное меню и попробуйте еще! ',reply_markup=markup)
                bot.register_next_step_handler(message, city)
    except Exception as i:
        bot.send_message(message.chat.id,"📢 Непредвиденная ошибка 📢")
        print(i,1)
        menu(message)

# @bot.callback_query_handler(func=lambda call: call.data.startswith(("KYES:", "KNO:")))
def attractions(message,city):
    try:
        city = city
        bot.send_message(message.chat.id, 'Ваш запрос обрабатывается...')
        koordinaten=[]
        koordinaten_city= {}

        # Подключение к базе данных
        conn = sqlite3.connect('cities.db')
        cursor = conn.cursor()

        #Запрос для проверки о наличии достопримечательности в БД
        query = '''SELECT attraction.name_attraction
                    FROM attraction
                    INNER JOIN city
                    ON attraction.city_id=city.city_id
                    WHERE city.name_city=? '''
        cursor.execute(query, (city,))

        # Извлечение результатов запроса
        attractions = cursor.fetchall()
        BD = [attraction[0] for attraction in attractions]
        print(BD)
        # Закрытие соединения с базой данных
        conn.close()
        for q in BD:
            try:
                e = q + " " + city
                k=koordinatens(e)
                koordinaten.append(k)
                koordinaten_city[q]=k
            except:
                pass

        if len(koordinaten)>2:
            sorted_attractions = driver(koordinaten)
        elif len(koordinaten)==2:
            sorted_attractions = [1,2]
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        gor = ""
        koordinaten_keys = list(koordinaten_city.keys())

        KN = telebot.types.KeyboardButton(text="✅ Главное меню")
        markup.add(KN)
        for w in sorted_attractions:
            gor += koordinaten_keys[w-1] + " ➡️ "
            KN = telebot.types.KeyboardButton(text=koordinaten_keys[w-1])
            markup.add(KN)

        gor = gor[:-3]
        bot.send_message(message.chat.id,
                         f"Достопримечательности города {city} лучше поситить в следующем порядке:\n{gor}\n\nЕсли хотите узнать о чём-нибудь подробней, нажмите на кнопки ниже",
                         reply_markup=markup)
        bot.delete_message(message.chat.id, message.message_id + 1)
    except Exception as i:
        print(i,2)
        bot.send_message(message.chat.id,"📢 Непредвиденная ошибка 📢")
        menu(message)

# @bot.callback_query_handler(func=lambda call: True)
def dostoprimichatelnosti(message,attar):
    try:

        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button = telebot.types.KeyboardButton(text="✅ Главное меню")
        keyboard.add(button)
        bot.send_message(message.chat.id, 'Ваш запрос обрабатывается...',reply_markup=telebot.types.ReplyKeyboardRemove())
        description = pars_wiki(attar, message.from_user.id, True)

        if description != False:
            bot.send_media_group(message.chat.id,
                                 [telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000001.jpg', 'rb')),
                                  telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000002.jpg', 'rb')),
                                  telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000003.jpg', 'rb')),
                                  telebot.types.InputMediaPhoto(open(f'./img/{message.from_user.id}/000004.jpg', 'rb'))])
            for i in range(1, 5):
                os.remove(f'./img/{message.from_user.id}/00000{i}.jpg')

            bot.send_message(message.chat.id, description,reply_markup=keyboard)
            bot.delete_message(message.chat.id, message.message_id + 1)
    except Exception as i:
        print(i,3)
        bot.send_message(message.chat.id,"📢 Непредвиденная ошибка 📢")
        menu(message)

#ФУНКЦИИ , КОТОРЫЕ ОТВЕЧАЮТ ЗА ГЕОЛОКАЦИЮ И ПОИСК БЛИЖАЙШЕЙ ОРГАНИЗАЦИИ
def geolocation(message):
    if message.text=="✅ Главное меню":
        menu(message)
    else:
        message_user = message.text
        # print(message_user)
        # Создаем кнопку с запросом геолокации
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button = telebot.types.KeyboardButton(text="🌐 Отправить геолокацию", request_location=True)
        keyboard.add(button)
        button = telebot.types.KeyboardButton(text="✅ Главное меню")
        keyboard.add(button)
        # Отправляем пользователю сообщение с кнопкой
        bot.send_message(message.chat.id, "👽 Нажмите кнопку для отправки геолокации \n\nЕсли хотите вернуться в меню, то нажмите на кнопку [✅ Главное меню", reply_markup=keyboard)
        bot.register_next_step_handler(message, process_shop, message_user)

# Обработчик ввода магазина/организации geolocation
def process_shop(message, mes_user):
    try:
        if mes_user=="✅ Главное меню":
            menu(message)
        else:
            # Получаем координаты геолокации
            latitude = message.location.latitude
            longitude = message.location.longitude

            # Вызываем функцию для поиска магазинов и передаем идентификатор пользователя
            find_shops(message.chat.id, mes_user, latitude, longitude)
    except Exception as i:
        print(i,4)
        bot.send_message(message.chat.id,"📢 Непредвиденная ошибка 📢")
        menu(message)

# Функция для поиска магазинов
def find_shops(user_id, shop, lat, lon):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("✅ Главное меню")
    markup.add(item1)

    req = str(lon) + ',' + str(lat)
    PARAMS = {
        "apikey": config.yandex_API,
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


def weather_bot(message,citys):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("✅ Главное меню")
    markup.add(item1)
    inp=''
    data=weather(citys)
    for i in data:
        inp=inp+i+" "+data[i]+"\n"
    bot.send_message(message.chat.id,inp,reply_markup=markup)


bot.infinity_polling()


