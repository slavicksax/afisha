import requests

api_key = "b0fcf94e8d6349ee8e341d2a8dc9492c"

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        #print(data['main']['temp']-273.15)
        return round((data['main']['temp']-272.65))
    else:
        print("Ошибка при выполнении запроса:", response.status_code)
