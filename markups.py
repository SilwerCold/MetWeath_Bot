from telebot import types

start_markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
start_markup_btn1 = types.KeyboardButton('/start')
start_markup_btn2 = types.KeyboardButton('/help')
start_markup_btn3 = types.KeyboardButton('/weather')
start_markup.add(start_markup_btn1, start_markup_btn2, start_markup_btn3)

city_markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
city_markup_btn1 = types.KeyboardButton('Москва')
city_markup_btn2 = types.KeyboardButton('Санкт-Петербург')
city_markup_btn3 = types.KeyboardButton('Самара')
city_markup.add(city_markup_btn1,city_markup_btn2,city_markup_btn3)

