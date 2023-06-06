from geopandas.tools import geocode

#получение координат города/достоприм
def koordinatens(city):
    location = geocode(city, provider="nominatim", user_agent='my_request')
    point = location.geometry.iloc[0]

    return [point.x, point.y]


if __name__ == "__main__":
    print(koordinatens("Останкинская башня Москва"))
