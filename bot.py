import telebot
import config
import time
import schedule
import pyowm
import sqlite3
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from pyowm.utils import timestamps, formatting
from sqliter import SQLighter
import markups as m

#подключаем токены и язык

bot = telebot.TeleBot(config.TOKEN)
config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = OWM(config.OWM_TOKEN, config_dict)
mgr = owm.weather_manager()


# инициализируем соединение с БД
db = SQLighter('/home/silwercold/db.db')

# Команда активации подписки
@bot.message_handler(commands=['subscribe'])
def subscribe(message):
	if(not db.subscriber_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его
		keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
		button_geo = telebot.types.KeyboardButton(text="Отправить местоположение", request_location=True)
		keyboard.add(button_geo)

		send = bot.send_message(message.chat.id, "Нажми на кнопку и передай мне свое местоположение", reply_markup=keyboard )
		bot.register_next_step_handler(send, sub_geo)
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_subscription(message.from_user.id, True)
		time.sleep(1)
		bot.send_message(message.chat.id, "Вы уже в базе!\n")

def sub_geo(message):
    lat = message.location.latitude
    lon = message.location.longitude
    if(lat!=None and lon!=None):
        db.add_subscriber(message.from_user.id, lat, lon)
        bot.send_message(message.chat.id, "Вы успешно подписались! 👍\n")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так\nПопробуйте включить геолокацию")
        return bot.send_message(message.chat.id, "/start")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
	if(not db.subscriber_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
		db.add_subscriber(message.from_user.id, None, None, False)
		time.sleep(1)
		bot.send_message(message.chat.id, "Вы итак не подписаны.")
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_subscription(message.from_user.id, False)
		time.sleep(1)
		bot.send_message(message.chat.id, "Вы успешно отписаны.")




#handler для /start
@bot.message_handler(commands = ['start'])
def start_command(message):
	bot.send_message(message.chat.id, 'Здесь ты можешь узнать погоду для своего города или страны\n')

#handler для /help
@bot.message_handler(commands = ['help'])
def help_command(message):
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.add(telebot.types.InlineKeyboardButton('Message the developer', url='telegram.me/Arubeon'))
	bot.send_message(message.chat.id, 'Здесь ты можешь узнать погоду для своего города или страны\n' +
		'Команды:\n' +
		'/locweather - погода по геолокации\n' +
		'/weather - погода в каком-то городе\n' +
		'/subscribe - подписаться\n' +
		'/unsubscribe - отписаться\n' +
		'если найдешь баг - тыкай по ссылке ниже и пиши',
		reply_markup=keyboard )


@bot.message_handler(commands = ['locweather'])
def loc_weather(message):
    if db.subscriber_exists(message.from_user.id):
    	info = db.coord_give(message.from_user.id)

    	for row in info:
    		lat = row[3]
    		lon = row[4]

    	one_call = mgr.one_call(lat=lat, lon=lon)


    	weather = one_call.current.detailed_status
    	temp = one_call.current.temperature('celsius')["temp"]
    	hum = one_call.current.humidity
    	time = one_call.current.reference_time(timeformat='iso')
    	wind = one_call.current.wind()["speed"]
    	clouds = one_call.current.clouds
    	tom_weather = one_call.forecast_daily[0].detailed_status
    	tom_temp = one_call.forecast_daily[0].temperature('celsius').get('morn', 0)
    	tom_hum = one_call.forecast_daily[0].humidity
    	tom_wind = one_call.forecast_daily[0].wind().get('speed', 0)
    	tom_clouds = one_call.forecast_daily[0].clouds

    	answer = 'СЕГОДНЯ:\n'
    	answer += '\U000026C5 Погода: {}\n'.format(weather)
    	answer += '⏱ Время: {}\n'.format(time)
    	answer += '\U0001F321 Температура: {} °C\n'.format(temp)
    	answer += '💦 Влажность: {}%\n'.format(hum)
    	answer += '\U0001F343 Ветер:  {} м/с\n'.format(wind)
    	answer += '\U00002601 Облака:  {} %\n\n'.format(clouds)
    	answer += 'ЗАВТРА:\n'
    	answer += '\U000026C5 Погода: {}\n'.format(tom_weather)
    	answer += 'Температура: {}°C\n'.format(tom_temp)
    	answer += '💦 Влажность: {}%\n'.format(tom_hum)
    	answer += '\U0001F343 Ветер:  {} м/с\n'.format(tom_wind)
    	answer += '\U00002601 Облака:  {} %\n\n'.format(tom_clouds)

    	bot.send_message(message.chat.id, answer,reply_markup=m.start_markup)
    else:
        bot.send_message(message.chat.id, "Для начала подпишись(/subscribe)")

#handler для /weather
@bot.message_handler(commands=['weather'])
def cmd_city(message):#***ввод города***
    send = bot.send_message(message.chat.id, 'Введи город', reply_markup = m.city_markup)
    bot.register_next_step_handler(send, send_weather)

def send_weather(message):
	try:#***выдача погоды по городу***
		city=message.text
		bot.send_message(message.chat.id, 'Ищу погоду в городе {}'.format(city))
		observation = mgr.weather_at_place(city)
		w = observation.weather
		weather = w.detailed_status
		temp = w.temperature('celsius')["temp"]
		hum = w.humidity
		time = w.reference_time(timeformat='iso')
		wind = w.wind()["speed"]
		clouds = w.clouds

		answer = '\U000026C5 Погода: {}\n'.format(weather)
		answer += '⏱ Время: {}\n'.format(time)
		answer += '\U0001F321 Температура: {} °C\n'.format(temp)
		answer += '💦 Влажность: {}%\n'.format(hum)
		answer += '\U0001F343 Ветер:  {} м/с\n'.format(wind)
		answer += '\U00002601 Облака:  {} %\n'.format(clouds)

		if temp < 11:
			answer += "Сейчас очень холодно."
		elif temp < 20:
			answer += "Сейчас прохладно, лучше одеться потеплее."
		else:
			answer += "Температура в норме!"

		bot.send_message(message.chat.id, answer,reply_markup=m.start_markup)
	except:
		bot.send_message(message.chat.id, 'Я не знаю такого города',reply_markup=m.start_markup)


def scheduled():
    newsletter = bot.send_locweater()
    subscriptions = db.get_subscriptions()
    for s in subscriptions:
        try:
            bot.send_message(s, newsletter)
        except:
            continue
    schedule.every(2).minutes.do(scheduled())
    while True:
        schedule.run_pending()
        time.sleep(1)

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling( none_stop = True)
