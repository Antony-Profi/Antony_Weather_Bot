import requests
import datetime
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from config_app_weather import weather_token, open_weather_token
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


bot = Bot(token=weather_token)
dp = Dispatcher(bot)


async def start(_):
    print('Бот был успешно запущен!')


HELP_COMMAND = """
<b>/start</b> - <em>при вызове этой команде мы запускаем бота</em>
<b>/vote</b> - <em>при вызове этой команде нам отправляют картинку, которую мы можем оценить</em>
<b>/help</b> - <em>при вызове этой команде мы запрашиваем объяснения, при котором нам всё объяснят</em>
"""


menu = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='/help')
button_2 = KeyboardButton(text='/vote')
menu.add(button_1, button_2)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='<b>Привет! Напиши мне название города и я пришлю сводку погоды!</b>',
                           reply_markup=menu,
                           parse_mode='HTML')

    ikb = InlineKeyboardMarkup(row_width=2)
    ib_1 = InlineKeyboardButton(text='👍', callback_data='like')
    ib_2 = InlineKeyboardButton(text='👎', callback_data='dislike')
    ikb.add(ib_1, ib_2)
    await bot.send_photo(chat_id=message.from_user.id,
                         photo='https://play.google.com/store/apps/details?id=com.weather.forcast.accurate.weatherlive&hl=ru',
                         caption='Нравится ли тебе эта фотка?',
                         reply_markup=ikb)
    await message.delete()


@dp.message_handler(commands=['vote'])
async def vote_command(message: types.Message):
    ikb = InlineKeyboardMarkup(row_width=2)
    ib_1 = InlineKeyboardButton(text='👍', callback_data='like')
    ib_2 = InlineKeyboardButton(text='👎', callback_data='dislike')
    ikb.add(ib_1, ib_2)
    await bot.send_photo(chat_id=message.from_user.id,
                         photo='https://hips.hearstapps.com/hmg-prod/images/766/benefits-of-lemon-water-1517535074.jpg?crop=0.848xw:1xh;center,top&resize=1200:*',
                         caption='Нравится ли тебе эта фотка?',
                         reply_markup=ikb)
    await message.delete()


@dp.callback_query_handler()
async def vote_callback(callback: types.CallbackQuery):
    if callback.data == 'like':
        await callback.answer(text='Ура! Спасибо что оценил!')
    await callback.answer(text='Жалко, я старался!')


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text=HELP_COMMAND,
                         parse_mode='HTML')
    await message.delete()


@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_smile = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F32B'
    }

    try:
        r = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric'
        )
        data = r.json()

        city = data['name']
        cur_weather = data['main']['temp']

        weather_description = data['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = 'Посмотри пожалуйста в окно, не пойму что там за погода!'

        humidity = data['main']['humidity']
        temp_max = data['main']['temp_max']
        temp_min = data['main']['temp_min']
        pressure = data['main']['pressure']
        wind = data['wind']['speed']
        country = data['sys']['country']
        sunrise_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        sunset_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        length_of_the_day = datetime.datetime.fromtimestamp(data['sys']['sunset']) - datetime.datetime.fromtimestamp(
            data['sys']['sunrise'])

        await message.reply(f"<b>{datetime.datetime.now().strftime('Дата: %Y-%m-%d  Время: %H:%M:%S')}</b>\n"
              f'\nПогода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n'
              f'Влажность: {humidity}\nМаксимальная температура: {temp_max}\n'
              f'Минимальная температура: {temp_min}\nДавление: {pressure} мм.рт.ст\n'
              f'Ветер: {wind} м/с\nРасширение страны: {country}\nВосход солнца: {sunrise_timestamp}\n'
              f'Закат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n'
              f'\n<b>              Хорошего дня 😎!</b>',
                            parse_mode='HTML'
              )

    except:
        await message.reply('\U0001F605 Проверьте название города \U0001F605')


executor.start_polling(dispatcher=dp, on_startup=start, skip_updates=True)