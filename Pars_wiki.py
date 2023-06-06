import wikipedia
from icrawler.builtin import GoogleImageCrawler
import os
import sqlite3

#Третий параметр в функции отвечает за то , что сейчас будет парситься
#TRUE -  достопримечательность
#FALSE - город
def pars_wiki(city, userid, flagAttractions):

    #Проверяем ввел ли пользователь город , если нет , то вывводится сообщение что такого нет в базе
    city_name = city.title()
    # Название города, которое  хотитим проверить (capitalize делает первую букву заглавной, остальные строчные)

    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()

    # Определяется SQL-запрос query, который выбирает все строки из таблицы "city", где значение столбца "name_city" равно заданному названию города.
    # Знак вопроса (?) является параметром, который будет заменен на значение city_name при выполнении запроса.
    query = "SELECT name_city FROM city WHERE name_city = ? or alter_name_city=?"
    cursor.execute(query, (city_name, city_name,))
    resultCity = cursor.fetchone()
    conn.close()
    if flagAttractions==False:
        city=resultCity[0]
    if resultCity == None and flagAttractions == False:
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



