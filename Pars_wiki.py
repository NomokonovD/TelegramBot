import wikipedia
from icrawler.builtin import GoogleImageCrawler
import os

def pars_wiki(city, userid):
    word = city.lower()
    f = open('city.txt', 'r',encoding='utf8')
    data = f.read()
    f.close()
    CityWord = data.lower().find(word)
    f = open('Attractions.txt', 'r', encoding='utf8')
    data = f.read()
    f.close()
    DostWord = data.lower().find(word)
    print(CityWord,DostWord)
    if CityWord == -1 and DostWord == -1:
        return False
    else:
        wikipedia.set_lang('ru')
        page = wikipedia.page(city)
        description = page.summary

        if not os.path.exists(f'./img/{userid}'):
            os.mkdir(f'./img/{userid}')

        google_crawler = GoogleImageCrawler(storage={'root_dir': f'./img/{userid}'})
        google_crawler.crawl(keyword=f'Красивые фото {city} jpg', max_num=4)
        return description


if __name__=="__main__":
    print(1)
    print(pars_wiki('Новосибирский государственный технический университет'))



