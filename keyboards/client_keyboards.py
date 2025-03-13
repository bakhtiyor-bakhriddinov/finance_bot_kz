from telegram import ReplyKeyboardMarkup, KeyboardButton

from utils.api_requests import api_routes


async def home_keyboard():
    reply_keyboard = [
        [
            KeyboardButton(text="Подать заявку"),
            KeyboardButton(text="Мои заявки")
        ],
        [
            KeyboardButton(text="Регламент подачи")
        ]
    ]
    text = "Главная страница"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def departments_keyboard():
    departments = api_routes.get_departments()["items"]
    departments = [department["name"] for department in departments]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(departments), 3):
        reply_keyboard.append(departments[i: i+3])

    text = "Укажите отдел, откуда подаёте заявку"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


async def expense_types_keyboard():
    objs = api_routes.get_expense_types()
    objs = [obj["name"] for obj in objs]
    reply_keyboard = [["Назад ⬅️"]]
    for i in range(0, len(objs), 3):
        reply_keyboard.append(objs[i: i+3])

    text = "Укажите тип затраты"
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
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
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    data_dict = {'text': text, 'markup': reply_markup}
    return data_dict


