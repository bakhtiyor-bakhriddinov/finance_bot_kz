from typing import Optional
from uuid import UUID

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from configs.variables import WEB_URL
from utils.api_requests import api_routes, access_token
from datetime import datetime, date
import calendar


async def home_keyboard(client_id: Optional[str] = None):
    reply_keyboard = [
        [
            KeyboardButton(text="Подать заявку"),
            KeyboardButton(text="Мои заявки")
        ],
        [
            KeyboardButton(text="Регламент подачи")
        ]
    ]
    if client_id is not None:
        url = f"{WEB_URL}?client={client_id}&token={access_token}"
        reply_keyboard.append(
            [
                KeyboardButton(text="Кабинет руководителя", web_app=WebAppInfo(url=url))
            ]
        )
    text = "Главная страница"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict



async def home_inline_keyboard(client_id):
    url = f"{WEB_URL}?client={client_id}&token={access_token}"
    inline_keyboard = [
        [
            InlineKeyboardButton(text="Домой", web_app=WebAppInfo(url=url))
        ]
    ]
    text = "Главная страница"
    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict



async def departments_keyboard():
    departments = api_routes.get_departments()["items"]
    departments = [department["name"] for department in departments]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(departments), 3):
        reply_keyboard.append(departments[i: i+3])

    text = "Укажите отдел, откуда подаёте заявку"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def expense_types_keyboard(department_id):
    # Get today's date
    today = date.today()

    # First day of current month
    first_day = today.replace(day=1)
    # first_day = datetime(year=2025, month=7, day=1).date()

    # Last day of current month
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    # last_day = datetime(year=2025, month=7, day=31).date()

    objs = api_routes.get_expense_types(department_id=department_id, start_date=first_day, finish_date=last_day)
    # objs = api_routes.get_expense_types()
    # print(objs)
    # objs = [obj["name"] for obj in objs]
    objs = [obj["expense_type"]["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i+3])

    if objs:
        text = "Укажите тип затраты"
    else:
        text = "Бюджет вашего отдела пустой !\nСвяжитесь с финансовым отделом."
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def buyers_keyboard():
    objs = api_routes.get_buyers()
    objs = [obj["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i+3])

    text = "Укажите Закупщика"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def suppliers_keyboard():
    objs = api_routes.get_suppliers()
    objs = [obj["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i+3])

    text = "Укажите поставщика"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def payment_types_keyboard():
    objs = api_routes.get_payment_types()
    objs = [obj["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i+3])

    text = "Выберите тип оплаты"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def currency_keyboard():
    currencies = ["Сум", "Доллар", "Евро", "Тенге", "Фунт", "Рубль", "Другое"]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(currencies), 3):
        reply_keyboard.append(currencies[i: i+3])

    text = "Выберите валюту"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def payer_companies_keyboard():
    response = api_routes.get_payer_companies()
    objs = response.json()['items']
    objs = [obj["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i + 3])

    text = 'Выбрите плательщика (фирму)'
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def countries_keyboard():
    objs = api_routes.get_countries()
    objs = [obj["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i+3])

    text = "Выберите страну"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def cities_keyboard(country_id: UUID):
    objs = api_routes.get_cities(country_id=country_id)
    objs = [obj["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i+3])

    text = "Выберите направление"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def request_with_receipts_keyboard():
    responses = ["Да", "Нет"]
    reply_keyboard = [["Назад ⬅️"], responses]

    text = "Ваша заявка имеет счёт-фактуру ?\nВыберите ответ:"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict