import requests,json
import datetime,time
import config
def weather(city,API_KEY=config.weather_api_key):

    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        r=requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric")
        data=r.json()
        # pprint (data)
        time_zone_local = int(-(time.timezone / 3600))
        # city=data["name"]
        temp=int(data['main']['temp'])
        humidity = data['main']['humidity']
        speed_wind=data["wind"]["speed"]
        sunrise_timestamp=datetime.datetime.fromtimestamp(data["sys"]["sunrise"])-datetime.timedelta(hours=time_zone_local)+datetime.timedelta(seconds=data['timezone'])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])-datetime.timedelta(hours=time_zone_local)+datetime.timedelta(seconds=data['timezone'])
        length_of_the_day=datetime.datetime.fromtimestamp(data["sys"]["sunset"])-datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        main_weather=data["weather"][0]["main"]
        if main_weather in code_to_smile:
            wd=code_to_smile[main_weather]
        else:
            wd="Посмотри в окно, не пойму что там за погода!"

        info={'Погода в городе': city,'Температура': f'{temp}C° {wd}',
                 'Влажность': f'{humidity}%','Скорость ветра': f'{speed_wind} м/с',
                 'Восход солнца': f'{sunrise_timestamp}','Закат солнца': f'{sunset_timestamp}',
                 'Продолжительность дня': f'{length_of_the_day}'}

        return info
    except Exception as ex:
        print(ex)
        return (ex)


if __name__=="__main__":
    weather("Санкт-петербург")