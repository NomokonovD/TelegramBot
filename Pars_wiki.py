import wikipedia
from icrawler.builtin import GoogleImageCrawler
import os
import sqlite3

def pars_wiki(city, userid):
    word = city.lower() #получаем город из параметров , который хочет найти пользователь и делаем его в нижний регистр

    #Проверяем ввел ли пользователь город , если нет , то вывводится сообщение что такого нет в базе

    city_name = city.capitalize()  # Название города, которое  хотитим проверить
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()

    query = "SELECT * FROM city WHERE LOWER(name_city) = LOWER(?)"
    cursor.execute(query, (city_name,))
    resultCity = cursor.fetchone()


    f = open('Attractions.txt', 'r', encoding='utf8')
    data = f.read()
    f.close()
    AttractionsWord = data.lower().find(word)
    print(resultCity,AttractionsWord)
    if resultCity == None and AttractionsWord == -1:
        return False
    else:
        wikipedia.set_lang('ru')
        page = wikipedia.page(f'город {city}')
        description = page.summary

        if not os.path.exists(f'./img/{userid}'):
            os.mkdir(f'./img/{userid}')

        google_crawler = GoogleImageCrawler(storage={'root_dir': f'./img/{userid}'})
        google_crawler.crawl(keyword=f'Красивые фото и достопримечательности города {city} jpg', max_num=4)
        return description


if __name__=="__main__":
    print(1)
    print(pars_wiki('Новосибирский государственный технический университет'))



