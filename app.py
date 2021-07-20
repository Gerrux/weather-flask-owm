from flask import Flask, render_template, request
import pyowm
from pyowm.utils.config import get_default_config
import datetime
import requests
import json

API_KEY_OWM = 'YOUR_OWM_TOKEN'

app = Flask(__name__)

config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = pyowm.OWM(API_KEY_OWM, config_dict)
mgr = owm.weather_manager()

icon01d = '/img/01d.png'
icon02d = '/img/02d.png'
icon03d = '/img/03d.png'
icon04d = '/img/04d.png'
icon09d = '/img/09d.png'
icon10d = '/img/10d.png'
icon11d = '/img/11d.png'
icon13d = '/img/13d.png'
icon50d = '/img/50d.png'
icon01n = '/img/01n.png'
icon02n = '/img/02n.png'
icon03n = '/img/03n.png'
icon04n = '/img/04n.png'
icon09n = '/img/09n.png'
icon10n = '/img/10n.png'
icon11n = '/img/11n.png'
icon13n = '/img/13n.png'
icon50n = '/img/50n.png'
error_icon = '/img/error.png'


def get_icon(icon_name):
    icon_status = ''
    if icon_name == "01d":
        icon = icon01d
        icon_status = 'sun'
    elif icon_name == "02d":
        icon = icon02d
        icon_status = 'cloud'
    elif icon_name == "03d":
        icon = icon03d
        icon_status = 'cloud'
    elif icon_name == "04d":
        icon = icon04d
        icon_status = 'cloud'
    elif icon_name == "09d":
        icon = icon09d
        icon_status = 'cloud-drizzle'
    elif icon_name == "10d":
        icon = icon10d
        icon_status = 'cloud-rain'
    elif icon_name == "11d":
        icon = icon11d
        icon_status = 'cloud-lightning'
    elif icon_name == "13d":
        icon = icon13d
        icon_status = 'cloud-snow'
    elif icon_name == "50d":
        icon = icon50d
        icon_status = 'eye-off'
    elif icon_name == "01n":
        icon = icon01n
        icon_status = 'moon'
    elif icon_name == "02n":
        icon = icon02n
        icon_status = 'cloud'
    elif icon_name == "03n":
        icon = icon03n
        icon_status = 'cloud'
    elif icon_name == "04n":
        icon = icon04n
        icon_status = 'cloud'
    elif icon_name == "09n":
        icon = icon09n
        icon_status = 'cloud-drizzle'
    elif icon_name == "10n":
        icon = icon10n
        icon_status = 'cloud-rain'
    elif icon_name == "11n":
        icon = icon11n
        icon_status = 'cloud-lightning'
    elif icon_name == "13n":
        icon = icon13n
        icon_status = 'cloud-snow'
    elif icon_name == "50n":
        icon = icon50n
        icon_status = 'eye-off'
    else:
        icon = error_icon
    return icon, icon_status


def wind_direction(wind):
    direction = ''
    deg = float(wind['deg'])
    if 0 <= deg < 22.5 or 337.5 < deg <= 360:
        direction = 'север'
    elif 22.5 < deg < 67.5:
        direction = 'северо-восток'
    elif 67.5 < deg < 112.5:
        direction = 'восток'
    elif 112.5 < deg < 157.5:
        direction = 'юго-восток'
    elif 157.5 < deg < 202.5:
        direction = 'юг'
    elif 202.5 < deg < 247.5:
        direction = 'юго-запад'
    elif 247.5 < deg < 292.5:
        direction = 'запад'
    elif 292.5 < deg < 337.5:
        direction = 'северо-запад'
    return direction


def current_weather(place="Москва"):
    try:
        # pyowm
        observation = mgr.weather_at_place(place)
        w = observation.weather
        answer = []
        answer.append(place)  # 0

        temp = w.temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
        answer.append(str(round(temp['temp'], 1)) + '°C')  # 1

        wind = w.wind()  # {'speed': 4.6, 'deg': 330}
        speed_wind = str(round(wind['speed'], 1))
        answer.append(speed_wind)  # 2
        direction = wind_direction(wind)
        answer.append(direction)  # 3

        humidity = str(w.humidity)  # 87
        answer.append(humidity)  # 4

        detailed_status = w.detailed_status.split(' ')
        detailed_status[0] = detailed_status[0].title()
        detailed_status = ' '.join(detailed_status)
        answer.append(detailed_status)  # 5

        pressure = str(round(float(w.pressure['press']) * 0.750064))
        answer.append(pressure)  # 6

        icon_name = w.weather_icon_name
        icon = get_icon(icon_name)
        answer.append(icon[0])  # 7

        date = str(datetime.date.today())
        answer.append(date.replace('-', '.'))  # 8
        day_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресение']
        answer.append(day_name[datetime.datetime.today().isoweekday() - 1])  # 9

        answer.append(icon[1])  # 10

        answer.append(forecast_weather(place))  # 11

        # answer = 'На данный момент в городе ' + place.title() + ':'
        # answer += 'Температура воздуха: ' + str(temp['temp']) + ' °C'
        # answer += 'Статус: ' + detailed_status
        # answer += 'Скорость ветра: ' + str(wind['speed']) + ' км/ч'
        # answer += 'Направление ветра: ' + direction
        # answer += 'Давление: ' + str(pressure['press']) + ' мбар'
        # answer += 'Влажность: ' + str(humidity) + ' %'
        return render_template("answer.html", answer=answer)

    except:
        return current_weather()


def forecast_weather(place="Москва"):
    observation = mgr.weather_at_place(place)
    lat = round(observation.location.lat, 2)
    lon = round(observation.location.lon, 2)
    request = requests.get(
        f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=hourly,current,minutely,alerts&appid={API_KEY_OWM}&lang=ru&units=metric")
    forecast = json.loads(request.content)
    forecast_weather_ans = {
        "temp": [],
        "data-icon": [],
        "daily-name": [],
    }
    daily_name = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    for i in range(1,5):
        forecast_weather_ans['temp'].append(round(forecast['daily'][i]['temp']['day'], 1))
        forecast_weather_ans['data-icon'].append(get_icon(forecast['daily'][i]['weather'][0]['icon'])[1])
        forecast_weather_ans['daily-name'].append(daily_name[datetime.datetime.today().isoweekday() - 1 + i])
    # print(forecast['daily'][1]['temp']['day'])
    return forecast_weather_ans


@app.route('/', methods=['GET', "POST"])
def index():
    if request.method == 'POST':
        return current_weather(request.form['title'])
    return current_weather()


if __name__ == '__main__':
    app.run()
