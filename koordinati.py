from geopandas.tools import geocode
def koordinati(city):
    loc = city
    location = geocode(loc, provider="nominatim" , user_agent = 'my_request')
    point = location.geometry.iloc[0]

    # print('complete address: '+ location.address.iloc[0])
    return [point.x,point.y]
if __name__=="__main__":
    print(koordinati("Памятник Пржевальскому Санкт-петербург"))
