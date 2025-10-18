# import logging
from datetime import datetime, date
from uuid import UUID

import requests
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton
)
from telegram.ext import ContextTypes

from configs.variables import APPROVE_GROUP, PROJECT_PATH, PURCHASE_GROUP
from keyboards import client_keyboards
from utils.api_requests import api_routes
from utils.utils import format_phone_number, error_sender, is_valid_date

# Define states
(
    AUTH,
    USER_REG,
    HOME,
    MY_REQUESTS,
    DEPARTMENTS,
    EXPENSE_TYPE,
    COUNTRY,
    CITY,
    TRIP_DAYS,
    BUYER,
    SUPPLIER,
    DESCRIPTION,
    CURRENCY,
    SUM,
    PAYMENT_TYPE,
    PAYER_COMPANY,
    CONTRACT,
    PAYMENT_CARD,
    SAP_CODE,
    PAYMENT_TIME,
    CONTRACT_NUMBER,
    RECEIPT,
    CONFIRM
) = range(23)




async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_password = update.message.text
    if user_password == "safia12":
        await update.message.reply_text(
            text='Пройдите регистрацию. \n'
                 'Укажите своё имя'
        )
        context.user_data["client"]["fullname"] = None
        return USER_REG

    else:
        await update.message.reply_text('Неправильный пароль !\nВведите пароль ещё раз!')
        return AUTH


async def user_reg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    if context.user_data["client"]["fullname"] is None and "phone" not in context.user_data["client"]:
        context.user_data["client"]["fullname"] = user_input
        await update.message.reply_text(
            text='Укажите свой номер в формате: +998933886989 или нажмите кнопку "Поделиться контактом ☎️"',
            reply_markup=ReplyKeyboardMarkup(keyboard=[[
                KeyboardButton(text="Поделиться контактом ☎️", request_contact=True)
            ]], resize_keyboard=True)
        )
        context.user_data["client"]["phone"] = None
        return USER_REG

    elif context.user_data["client"]["phone"] is None:
        contact = update.message.contact
        phone = ''
        if user_input:
            phone = user_input
        elif contact:
            phone = contact.phone_number

        phone_number = format_phone_number(phone)
        if phone_number is None:
            await update.message.reply_text(
                text='Укажите свой номер в формате: +998933886989 или нажмите кнопку "Поделиться контактом ☎️"',
                reply_markup=ReplyKeyboardMarkup(keyboard=[[
                    KeyboardButton(text="Поделиться контактом ☎️", request_contact=True)
                ]], resize_keyboard=True)
            )
            context.user_data["client"]["phone"] = None
            return USER_REG

        context.user_data["client"]["phone"] = phone_number


    if context.user_data["client"]["fullname"] is not None and context.user_data["client"]["phone"] is not None:
        body = {
            "tg_id": context.user_data["client"]["tg_id"],
            "fullname": context.user_data["client"]["fullname"],
            "language": context.user_data["client"]["language"],
            "phone": context.user_data["client"]["phone"]
        }
        response = api_routes.create_client(body=body)
        if response.status_code == 200:
            client = response.json()
            context.user_data["client"]["id"] = client["id"]
            await update.message.reply_text(text="Вы успешно прошли регистрацию")
            keyboard = (await client_keyboards.home_keyboard())
            await update.message.reply_text(
                text=keyboard['text'],
                reply_markup=keyboard['markup']
            )
            return HOME
        else:
            error_sender(error_message=f"FINANCE BOT: \n{response.text}")
            await update.message.reply_text(text="Что-то пошло не так, отправьте заново комманду /start")


async def home_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selection = update.message.text
    if selection == "Подать заявку":
        keyboard = (await client_keyboards.departments_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        context.user_data["new_request"] = {}
        context.user_data["request_details"] = {}
        return DEPARTMENTS

    elif selection == "Мои заявки":
        await update.message.reply_text(
            text="Выберите раздел",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    ["Назад ⬅️"],
                    ["Актив", "Архив"]
                ],
                resize_keyboard=True
            )
        )
        return MY_REQUESTS

    # if selection == "Настройки":
    #     text = f"Ваши данные:\n\n" \
    #            f"Должность: {user_role}\n" \
    #            f"Филиал: {user_branch}"
    #     await update.message.reply_text(text)
    #     keyboard = (await common_keyboards.settings_keyboard())
    #     await update.message.reply_text(
    #         text=keyboard['text'],
    #         reply_markup=keyboard['markup']
    #     )
    #     return SETTINGS


# async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     tg_id = update.message.chat.id
#     user_input = update.message.text
#     response = api_routes.get_client(tg_id)
#     user = response.json()
#     user_role = user["group_id"]
#     user_branch = user["branch_id"]
#     if user_input == "Назад":
#         keyboard = {}
#         if user_role == 34:
#             keyboard = (await seller_keyboards.home_keyboard(tg_id))
#         elif user_role == 35:
#             keyboard = (await freezer_keyboards.home_keyboard(tg_id))
#         await update.message.reply_text(
#             text=keyboard['text'],
#             reply_markup=keyboard['markup']
#         )
#         return HOME
#
#     elif user_input == "Поменять филиал":
#         keyboard = (await common_keyboards.store_search_keyboard())
#         await update.message.reply_text(
#             text=keyboard['text'],
#             reply_markup=keyboard['markup']
#         )
#         return STORE_SELECTION
#
#     elif user_input == "Поменять должность":
#         ids = [34, 35]
#         roles = api_routes.get_roles(ids=ids)
#         role_names = [role["name"] for role in roles]
#         await update.message.reply_text(
#             text='Выберите должность 👇',
#             reply_markup=ReplyKeyboardMarkup([role_names], resize_keyboard=True, one_time_keyboard=True)
#         )
#         return ROLE_SELECTION


async def department_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    department_name = update.message.text
    if department_name == "Назад ⬅️":
        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return HOME

    response = api_routes.get_departments(name=department_name)
    department = response["items"][0]
    department_id = department["id"]
    over_budget = department["over_budget"]
    context.user_data["new_request"]["status"] = 0
    context.user_data["new_request"]["department_id"] = department_id
    context.user_data["request_details"]["department_name"] = department_name
    context.user_data["request_details"]["department_purchasable"] = department["purchasable"]
    # context.user_data["request_details"]["over_budget"] = bool(over_budget == "True")
    context.user_data["request_details"]["over_budget"] = over_budget

    keyboard = (await client_keyboards.expense_types_keyboard(department_id=UUID(department_id)))
    await update.message.reply_text(
        text=keyboard['text'],
        reply_markup=keyboard['markup']
    )
    return EXPENSE_TYPE



async def expense_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    expense_type_name = update.message.text
    if expense_type_name == "Назад ⬅️":
        keyboard = (await client_keyboards.departments_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        context.user_data["new_request"] = {}
        context.user_data["request_details"] = {}
        return DEPARTMENTS

    response = api_routes.get_expense_types(name=expense_type_name)
    expense_type = response[0]
    expense_type_id = expense_type["id"]
    context.user_data["new_request"]["expense_type_id"] = expense_type_id
    context.user_data["request_details"]["expense_type_name"] = expense_type_name
    context.user_data["request_details"]["expense_type_purchasable"] = expense_type["purchasable"]
    context.user_data["request_details"]["expense_type_checkable"] = expense_type["checkable"]


    if expense_type_name == "Командировочные расходы":
        keyboard = (await client_keyboards.countries_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return COUNTRY

    # keyboard = (await client_keyboards.buyers_keyboard())
    await update.message.reply_text(
        text="Укажите Заказчика",
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True)
    )
    return BUYER



async def country_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    country_name = update.message.text
    if country_name == "Назад ⬅️":
        keyboard = (await client_keyboards.expense_types_keyboard(department_id=UUID(context.user_data["new_request"]["department_id"])))
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return EXPENSE_TYPE

    response = api_routes.get_countries(name=country_name)
    country_obj = response[0]
    country_id = country_obj["id"]
    context.user_data["request_details"]["country_id"] = country_id
    context.user_data["request_details"]["country"] = country_name

    keyboard = (await client_keyboards.cities_keyboard(country_id=country_id))
    await update.message.reply_text(
        text=keyboard['text'],
        reply_markup=keyboard['markup']
    )
    return CITY


async def city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city_name = update.message.text
    if city_name == "Назад ⬅️":
        keyboard = (await client_keyboards.countries_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return COUNTRY

    response = api_routes.get_cities(name=city_name)
    city_obj = response[0]
    city_id = city_obj["id"]
    city_desc = city_obj["description"]
    context.user_data["new_request"]["city_id"] = city_id
    context.user_data["request_details"]["city"] = city_name

    await update.message.reply_text(
        text=f"Информация по выбранному направлению: \n{city_desc}"
    )

    await update.message.reply_text(
        text="Введите количество дней в числах !",
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True)
    )
    return TRIP_DAYS


async def trip_days_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    amount_days = update.message.text
    if amount_days == "Назад ⬅️":
        keyboard = (await client_keyboards.cities_keyboard(country_id=context.user_data["request_details"]["country_id"]))
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return CITY

    if not amount_days.isdigit():
        await update.message.reply_text(
            text="Введите только числа !"
        )
        return TRIP_DAYS

    context.user_data["new_request"]["trip_days"] = int(amount_days)
    context.user_data["request_details"]["trip_days"] = int(amount_days)

    await update.message.reply_text(
        text="Укажите Заказчика",
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True)
    )
    return BUYER



async def buyer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buyer_name = update.message.text
    if buyer_name == "Назад ⬅️":
        keyboard = (await client_keyboards.expense_types_keyboard(department_id=UUID(context.user_data["new_request"]["department_id"])))
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return EXPENSE_TYPE

    # response = api_routes.get_buyers(name=buyer_name)
    # buyer_id = response[0]["id"]
    # context.user_data["new_request"]["buyer_id"] = buyer_id
    context.user_data["new_request"]["buyer"] = buyer_name
    context.user_data["request_details"]["buyer_name"] = buyer_name

    # keyboard = (await client_keyboards.suppliers_keyboard())
    await update.message.reply_text(
        text="Укажите поставщика",
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True)
    )
    return SUPPLIER


async def supplier_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    supplier_name = update.message.text
    if supplier_name == "Назад ⬅️":
        # keyboard = (await client_keyboards.buyers_keyboard())
        await update.message.reply_text(
            text="Укажите Заказчика",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True)
        )
        return BUYER

    # response = api_routes.get_suppliers(name=supplier_name)
    # supplier_id = response[0]["id"]
    # context.user_data["new_request"]["supplier_id"] = supplier_id
    context.user_data["new_request"]["supplier"] = supplier_name
    context.user_data["request_details"]["supplier_name"] = supplier_name

    await update.message.reply_text(
        text='Введите комментарии',
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return DESCRIPTION


async def description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    description = update.message.text
    if description == "Назад ⬅️":
        # keyboard = (await client_keyboards.suppliers_keyboard())
        await update.message.reply_text(
            text="Укажите поставщика",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True)
        )
        return SUPPLIER

    if context.user_data.get("new_request", None) is not None:
        context.user_data["new_request"]["description"] = description

    if context.user_data.get("request_details", None) is not None:
        context.user_data["request_details"]["description"] = description

    if context.user_data.get("new_request", None) is None and context.user_data.get("request_details", None) is None:
        context.user_data["request_updates"]["delay_reason"] = description

        data = context.user_data["request_updates"]
        response = api_routes.update_request(body=data)

        if response.status_code == 200:
            await update.message.reply_text("Заявка успешно одобрена !")
            client_id = context.user_data["request_info"]["client_tg_id"]
            request_text = context.user_data["request_info"]["text"]
            message_id = context.user_data["request_info"]["message_id"]
            request_number = context.user_data["request_info"]["number"]
            if update.message.text:
                await context.bot.edit_message_text(
                    text=request_text,
                    chat_id=update.message.chat.id,
                    message_id=message_id,
                    reply_markup=None
                )
            elif update.message.caption:
                await context.bot.edit_message_caption(
                    caption=request_text,
                    chat_id=update.message.chat.id,
                    message_id=message_id,
                    reply_markup=None
                )
            try:
                await context.bot.send_message(
                    chat_id=client_id,
                    text=f"Заявка #{request_number}s одобрена и отложена!\nПричина отложения:  {description}"
                )
            except Exception as e:
                error_sender(error_message=f"FINANCE BOT: \n{e}")

        elif response.status_code == 400:
            await update.message.reply_text(
                text="Заявка не может быть одобрена, недостаточно средств в бюджете ! ❌"
            )

        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return HOME

    keyboard = (await client_keyboards.currency_keyboard())
    await update.message.reply_text(
        text=keyboard['text'],
        reply_markup=keyboard['markup']
    )
    return CURRENCY


async def currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    currency = update.message.text
    if currency == "Назад ⬅️":
        await update.message.reply_text(
            text='Введите комментарии',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return DESCRIPTION

    if currency not in ["Сум", "Доллар", "Евро", "Тенге", "Фунт", "Рубль"]:  # "Другое"
        keyboard = (await client_keyboards.currency_keyboard())
        await update.message.reply_text(
            text=f"{keyboard['text']} только из этих вариантов 👇",
            reply_markup=keyboard['markup']
        )
        return CURRENCY

    ccy = ""
    if currency == "Доллар":
        ccy = "USD"
    elif currency == "Евро":
        ccy = "EUR"
    elif currency == "Тенге":
        ccy = "KZT"
    elif currency == "Фунт":
        ccy = "GBP"
    elif currency == "Рубль":
        ccy = "RUB"

    exchange_rate = None

    if currency != "Сум":
        currency_response = requests.get(f"https://cbu.uz/uz/arkhiv-kursov-valyut/json/")
        if currency_response.status_code == 200:
            cbu_currencies = currency_response.json()
            currency_dict = next((item for item in cbu_currencies if item["Ccy"] == ccy), None)
            exchange_rate = float(currency_dict["Rate"])

        else:
            error_sender(error_message=currency_response.text)
            await update.message.reply_text(
                text="Что-то пошло не так, выберите заново валюту!"
            )
            keyboard = (await client_keyboards.currency_keyboard())
            await update.message.reply_text(
                text=keyboard['text'],
                reply_markup=keyboard['markup']
            )
            return CURRENCY


    context.user_data["new_request"]["currency"] = currency
    context.user_data["new_request"]["exchange_rate"] = exchange_rate
    context.user_data["request_details"]["currency"] = currency
    context.user_data["request_details"]["exchange_rate"] = exchange_rate

    await update.message.reply_text(
        text='Укажите сумму в числах',
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return SUM



async def sum_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sum = update.message.text
    if sum == "Назад ⬅️":
        keyboard = (await client_keyboards.currency_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return CURRENCY

    is_number = sum.isdigit()
    if is_number:
        # over_budget = context.user_data["request_details"]["over_budget"]
        if context.user_data["new_request"]["currency"] != "Сум":
            sum = float(sum) * context.user_data["new_request"]["exchange_rate"]

        context.user_data["new_request"]["sum"] = sum
        context.user_data["request_details"]["sum"] = sum

        await update.message.reply_text(
            text="Введите дату оплаты в формате:  дд.мм.гггг (08.05.2025)",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return PAYMENT_TIME

    else:
        await update.message.reply_text(
            text='Укажите сумму. Используйте только числа',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return SUM



async def payment_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text
    if user_message == "Назад ⬅️":
        await update.message.reply_text(
            text='Укажите сумму в числах',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return SUM

    is_date = is_valid_date(user_message)
    if is_date is False:
        await update.message.reply_text(
            text='Повторно введите дату в правильном формате',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return PAYMENT_TIME

    date_obj = datetime.strptime(user_message, "%d.%m.%Y")

    # Format it as "YYYY-MM-DD"
    formatted_date = date_obj.strftime("%Y-%m-%d")

    if date_obj.date() < date.today():
        await update.message.reply_text(
            text='Вы не можете ввести прошедшую дату !',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return PAYMENT_TIME

    budget_balance = api_routes.get_budget_balance(
        department_id=context.user_data["new_request"]["department_id"],
        expense_type_id=context.user_data["new_request"]["expense_type_id"],
        start_date=formatted_date,
        finish_date=formatted_date
    )
    context.user_data["request_details"]["budget_balance"] = budget_balance['value'] if budget_balance else 0

    await update.message.reply_text(
        text=f"Ваш текущий бюджет по выбранному типу затраты: \n<b>{format(budget_balance['value'], ',').replace(',', ' ') if budget_balance else 0} сум</b>",
        parse_mode='HTML'
    )


    # Format it as "YYYY-MM-DD"
    formatted_date = date_obj.strftime("%Y-%m-%d")

    if context.user_data.get("new_request", None) is not None:
        context.user_data["new_request"]["payment_time"] = formatted_date

    if context.user_data.get("request_details", None) is not None:
        context.user_data["request_details"]["payment_time"] = date_obj

    if context.user_data.get("new_request", None) is None and context.user_data.get("request_details", None) is None:
        context.user_data["request_updates"]["payment_time"] = formatted_date

        await update.message.reply_text(
            text='Введите комментарии'
        )
        return DESCRIPTION


    keyboard = (await client_keyboards.payment_types_keyboard())
    await update.message.reply_text(
        text=keyboard['text'],
        reply_markup=keyboard['markup']
    )
    return PAYMENT_TYPE



async def payment_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    payment_type_name = update.message.text
    if payment_type_name == "Назад ⬅️":
        await update.message.reply_text(
            text="Введите дату оплаты в формате:  дд.мм.гггг (08.05.2025)",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return PAYMENT_TIME

    response = api_routes.get_payment_types(name=payment_type_name)
    payment_type_id = response[0]["id"]
    context.user_data["new_request"]["payment_type_id"] = payment_type_id
    context.user_data["request_details"]["payment_type_name"] = payment_type_name

    text = ''
    reply_markup = None
    if "Перевод" in payment_type_name:
        text = 'Укажите номер карты, куда нужно сделать перевод средств.'
        reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup
        )
        return PAYMENT_CARD

    elif "Наличные" in payment_type_name:
        context.user_data["new_request"]["cash"] = context.user_data["new_request"]["sum"]
        text = 'Отправьте договор в формате: pdf , png , docx.'
        reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"], ["Пропустить ➡️"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup
        )
        context.user_data.pop("media_group", None)
        return CONTRACT

    elif "Перечисление" in payment_type_name:
        # text = 'Отправьте договор в формате: pdf , png , docx.'
        keyboard = (await client_keyboards.payer_companies_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return PAYER_COMPANY



async def payer_company_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    payer_company = update.message.text
    if payer_company == "Назад ⬅️":
        keyboard = (await client_keyboards.payment_types_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return PAYMENT_TYPE

    response = api_routes.get_payer_companies(name=payer_company)
    if response.status_code == 200:
        objs = response.json()
        payer_company_id = objs["items"][0]["id"]

        context.user_data["new_request"]["payer_company_id"] = payer_company_id
        context.user_data["request_details"]["payer_company_name"] = payer_company

        text = 'Отправьте договор в формате: pdf , png , docx.'
        reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True,
                                           one_time_keyboard=True)
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup
        )
        context.user_data.pop("media_group", None)
        return CONTRACT
    else:
        await update.message.reply_text(
            text='Выберите плательщика только из списка',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return PAYER_COMPANY


async def payment_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    payment_card = update.message.text
    if payment_card == "Назад ⬅️":
        keyboard = (await client_keyboards.payment_types_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return PAYMENT_TYPE

    context.user_data["new_request"]["payment_card"] = payment_card
    context.user_data["request_details"]["payment_card"] = payment_card

    await update.message.reply_text(
        text='Укажите код заявки в SAP',
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return SAP_CODE


async def contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    media_group_id = message.media_group_id
    files = []
    messages = [message]

    if message.text:
        text = update.message.text
        if text == "Назад ⬅️":
            keyboard = (await client_keyboards.payment_types_keyboard())
            await update.message.reply_text(
                text=keyboard['text'],
                reply_markup=keyboard['markup']
            )
            return PAYMENT_TYPE
        elif text == "Пропустить ➡️":
            await update.message.reply_text(
                text='Укажите код заявки в SAP',
                reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
            )
            return SAP_CODE
        else:
            await update.message.reply_text("⚠️ 'Отправьте договор в формате: pdf , png , docx.'")
            context.user_data.pop("media_group", None)
            return CONTRACT

    # Prepare user_data store for accumulating media group
    if media_group_id:
        if "media_group" not in context.user_data:
            context.user_data["media_group"] = {}

        if media_group_id not in context.user_data["media_group"]:
            context.user_data["media_group"][media_group_id] = []

        context.user_data["media_group"][media_group_id].append(message)

        messages = context.user_data["media_group"][media_group_id]

        if len(messages) < 2:
            return CONTRACT

    context.user_data["new_request"]["contract"] = True
    for msg in messages:
        document = msg.document
        photo = msg.photo
        if document:  # ✅ If the user sends a document
            file_id = document.file_id
            file_name = document.file_name if document.file_name else document.file_unique_id
            mime_type = document.mime_type
        elif photo and len(photo) > 0:  # ✅ If the user sends a photo
            file_id = photo[-1].file_id  # Get the best quality image
            file_name = photo[-1].file_unique_id + '.jpg'
            # mime_type = "image/png"
            mime_type = "image/jpeg"
        else:
            await update.message.reply_text("⚠️ 'Отправьте договор в формате: pdf , png , docx.'")
            context.user_data.pop("media_group", None)
            return CONTRACT

        file = await context.bot.get_file(file_id)  # Get the file object
        binary_data = await file.download_as_bytearray()  # Download file as binary data

        # Prepare files for upload
        files.append(("files", (file_name, binary_data, mime_type)))

    response = api_routes.upload_files(files=files)
    if response.status_code == 200:
        response = response.json()
        context.user_data["new_request"]["file_paths"] = response["file_paths"]
    else:
        error_sender(error_message=f"FINANCE BOT: \n{response.text}")
        await update.message.reply_text(
            text="Повторите отправить файл заново!",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True,
                                             one_time_keyboard=True)
        )
        context.user_data.pop("media_group", None)
        return CONTRACT

    await update.message.reply_text(
        text='Укажите код заявки в SAP',
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return SAP_CODE

    # print(f"\nmessages: {messages}\n")
    # print(f"media_group: {context.user_data['media_group']}\n\n")
    # print(f"messages after cleaning: {messages}\n")

    # if "media_group" in context.user_data:
    #     # Check if we had buffered a media group earlier
    #     for group_id, msgs in context.user_data["media_group"].items():
    #         if any(m.message_id == message.message_id for m in msgs):
    #             messages = msgs
    #             del context.user_data["media_group"][group_id]
    #             break


async def sap_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sap_code = update.message.text
    if sap_code == "Назад ⬅️":
        if "payment_card" in context.user_data["new_request"]:
            text = 'Укажите номер карты, куда нужно сделать перевод средств.'
            reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True,
                                               one_time_keyboard=True)
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup
            )
            return PAYMENT_CARD

        elif "contract" in context.user_data["new_request"]:
            text = 'Отправьте договор в формате: pdf , png , docx.'
            reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True,
                                               one_time_keyboard=True)
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup
            )
            context.user_data.pop("media_group", None)
            return CONTRACT
        else:
            keyboard = (await client_keyboards.payment_types_keyboard())
            await update.message.reply_text(
                text=keyboard['text'],
                reply_markup=keyboard['markup']
            )
            return PAYMENT_TYPE

    context.user_data["new_request"]["sap_code"] = sap_code
    context.user_data["new_request"]["client_id"] = context.user_data['client']["id"]
    context.user_data["request_details"]["sap_code"] = sap_code

    if "Перечисление" in context.user_data["request_details"]["payment_type_name"]:
        text = 'Укажите номер договора'
        reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True,
                                           one_time_keyboard=True)
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup
        )
        return CONTRACT_NUMBER

    request = context.user_data["request_details"]
    request_sum = format(int(request['sum']), ',').replace(',', ' ')
    if request.get('exchange_rate', None) is not None:
        requested_currency = format((request['sum'] / request['exchange_rate']), ',').replace(',', ' ')
    else:
        requested_currency = request_sum

    request_text = (
        f"📅 Дата заявки: {datetime.now().date().strftime('%d.%m.%Y')}\n"
        f"📍 Отдел: {request['department_name']}\n"
        f"👤 Заявитель: {context.user_data['client']['fullname']}\n"
        f"📞 Номер заявителя: {context.user_data['client']['phone']}\n"
        f"🛒 Заказчик: {request['buyer_name']}\n"
        f"💰 Тип затраты: {request['expense_type_name']}\n"
        f"🏢 Поставщик: {request['supplier_name']}\n\n"
        f"💎 Стоимость: <b>{request_sum} сум</b>\n"
        f"💎 Запрошенная сумма в валюте: <b>{requested_currency}</b>\n"
        f"💵 Валюта: {request['currency']}\n"
        f"📈 Курс валюты: {request['exchange_rate']}\n"
        f"💳 Тип оплаты: {request['payment_type_name']}\n"
        f"💳 Карта перевода: {request.get('payment_card', '')}\n"
        f"📜 № Заявки в SAP: {request['sap_code']}\n"
        f"🕓 Дата оплаты: {request['payment_time'].strftime('%d.%m.%Y')}\n"
        f"💸 Фирма-плательщик: {request.get('payer_company_name', '')}\n\n"
        f"📝 Комментарии: {request['description']}"
    )
    city_name = context.user_data.get("request_details").get("city")
    trip_days = context.user_data.get("request_details").get("trip_days")
    if city_name and trip_days:
        request_text += (f"\n✈️ Коммандировка по направлению: {city_name}"
                         f"\n⏳ Количество дней: {trip_days}")
    budget_balance = context.user_data["request_details"]["budget_balance"]
    context.user_data["request_details"]["send_ceo"] = False

    if float(context.user_data["request_details"]["sum"]) > budget_balance and context.user_data["request_details"][
        "over_budget"] == False:
        await update.message.reply_text(
            text="К сожалению, на балансе бюджета недостаточно средств для покрытия запрошенной суммы."
        )
        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return HOME

    else:
        if float(context.user_data["request_details"]["sum"]) > budget_balance and \
                context.user_data["request_details"]["over_budget"] == True:
            context.user_data["request_details"]["send_ceo"] = True

        await update.message.reply_text(
            text='Проверьте свою заявку ещё раз, если всё правильно, подтвердите её.'
        )
        await update.message.reply_text(
            text=request_text,
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"], ["Подтвердить"]], resize_keyboard=True),
            parse_mode='HTML'
        )
        return CONFIRM



async def contract_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = update.message.text

    if response == "Назад ⬅️":
        await update.message.reply_text(
            text='Укажите код заявки в SAP',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return SAP_CODE

    context.user_data["request_details"]["contract_number"] = response
    context.user_data["new_request"]["contract_number"] = response

    text = ('Отправьте счёт-фактуру в формате: pdf , png , docx.\n'
            'Либо нажмите "Пропустить ➡️", если оплата является авансом !')
    reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"], ["Пропустить ➡️"]], resize_keyboard=True,
                                       one_time_keyboard=True)
    await update.message.reply_text(
        text=text,
        reply_markup=reply_markup
    )
    return RECEIPT



async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    media_group_id = message.media_group_id
    files = []
    messages = [message]

    if message.text:
        text = update.message.text
        if text == "Назад ⬅️":
            text = 'Укажите номер договора'
            reply_markup = ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True,
                                               one_time_keyboard=True)
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup
            )
            return CONTRACT_NUMBER

        elif text == "Пропустить ➡️":
            request = context.user_data["request_details"]
            request_sum = format(int(request['sum']), ',').replace(',', ' ')
            if request.get('exchange_rate', None) is not None:
                requested_currency = format((request['sum'] / request['exchange_rate']), ',').replace(',', ' ')
            else:
                requested_currency = request_sum

            request_text = (
                f"📅 Дата заявки: {datetime.now().date().strftime('%d.%m.%Y')}\n"
                f"📍 Отдел: {request['department_name']}\n"
                f"👤 Заявитель: {context.user_data['client']['fullname']}\n"
                f"📞 Номер заявителя: {context.user_data['client']['phone']}\n"
                f"🛒 Заказчик: {request['buyer_name']}\n"
                f"💰 Тип затраты: {request['expense_type_name']}\n"
                f"🏢 Поставщик: {request['supplier_name']}\n\n"
                f"💎 Стоимость: <b>{request_sum} сум</b>\n"
                f"💎 Запрошенная сумма в валюте: <b>{requested_currency}</b>\n"
                f"💵 Валюта: {request['currency']}\n"
                f"📈 Курс валюты: {request['exchange_rate']}\n"
                f"💳 Тип оплаты: {request['payment_type_name']}\n"
                f"💳 Карта перевода: {request.get('payment_card', '')}\n"
                f"📜 № Заявки в SAP: {request['sap_code']}\n"
                f"🕓 Дата оплаты: {request['payment_time'].strftime('%d.%m.%Y')}\n"
                f"💸 Фирма-плательщик: {request.get('payer_company_name', '')}\n\n"
                f"📝 Комментарии: {request['description']}"
            )
            city_name = context.user_data.get("request_details").get("city")
            trip_days = context.user_data.get("request_details").get("trip_days")
            if city_name and trip_days:
                request_text += (f"\n✈️ Коммандировка по направлению: {city_name}"
                                 f"\n⏳ Количество дней: {trip_days}")
            budget_balance = context.user_data["request_details"]["budget_balance"]
            context.user_data["request_details"]["send_ceo"] = False

            if float(context.user_data["request_details"]["sum"]) > budget_balance and \
                    context.user_data["request_details"][
                        "over_budget"] == False:
                await update.message.reply_text(
                    text="К сожалению, на балансе бюджета недостаточно средств для покрытия запрошенной суммы."
                )
                keyboard = (await client_keyboards.home_keyboard())
                await update.message.reply_text(
                    text=keyboard['text'],
                    reply_markup=keyboard['markup']
                )
                return HOME

            else:
                if float(context.user_data["request_details"]["sum"]) > budget_balance and \
                        context.user_data["request_details"]["over_budget"] == True:
                    context.user_data["request_details"]["send_ceo"] = True

                await update.message.reply_text(
                    text='Проверьте свою заявку ещё раз, если всё правильно, подтвердите её.'
                )
                await update.message.reply_text(
                    text=request_text,
                    reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"], ["Подтвердить"]], resize_keyboard=True),
                    parse_mode='HTML'
                )
                return CONFIRM

        else:
            await update.message.reply_text("⚠️ 'Отправьте счёт-фактуру в формате: pdf , png , docx.'")
            context.user_data.pop("media_group", None)
            return RECEIPT

    # Prepare user_data store for accumulating media group
    if media_group_id:
        if "media_group" not in context.user_data:
            context.user_data["media_group"] = {}

        if media_group_id not in context.user_data["media_group"]:
            context.user_data["media_group"][media_group_id] = []

        context.user_data["media_group"][media_group_id].append(message)

        messages = context.user_data["media_group"][media_group_id]

        if len(messages) < 2:
            return RECEIPT

    for msg in messages:
        document = msg.document
        photo = msg.photo
        if document:  # ✅ If the user sends a document
            file_id = document.file_id
            file_name = document.file_name if document.file_name else document.file_unique_id
            mime_type = document.mime_type
        elif photo and len(photo) > 0:  # ✅ If the user sends a photo
            file_id = photo[-1].file_id  # Get the best quality image
            file_name = photo[-1].file_unique_id + '.jpg'
            # mime_type = "image/png"
            mime_type = "image/jpeg"
        else:
            await update.message.reply_text("⚠️ 'Отправьте договор в формате: pdf , png , docx.'")
            context.user_data.pop("media_group", None)
            return RECEIPT

        file = await context.bot.get_file(file_id)  # Get the file object
        binary_data = await file.download_as_bytearray()  # Download file as binary data

        # Prepare files for upload
        files.append(("files", (file_name, binary_data, mime_type)))

    response = api_routes.upload_files(files=files)
    if response.status_code == 200:
        response = response.json()
        context.user_data["new_request"]["receipt_files"] = response["file_paths"]
    else:
        error_sender(error_message=f"FINANCE BOT: \n{response.text}")
        await update.message.reply_text(
            text="Повторите отправить файл заново!",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True,
                                             one_time_keyboard=True)
        )
        context.user_data.pop("media_group", None)
        return RECEIPT

    request = context.user_data["request_details"]
    request_sum = format(int(request['sum']), ',').replace(',', ' ')
    if request.get('exchange_rate', None) is not None:
        requested_currency = format((request['sum'] / request['exchange_rate']), ',').replace(',', ' ')
    else:
        requested_currency = request_sum

    request_text = (
        f"📅 Дата заявки: {datetime.now().date().strftime('%d.%m.%Y')}\n"
        f"📍 Отдел: {request['department_name']}\n"
        f"👤 Заявитель: {context.user_data['client']['fullname']}\n"
        f"📞 Номер заявителя: {context.user_data['client']['phone']}\n"
        f"🛒 Заказчик: {request['buyer_name']}\n"
        f"💰 Тип затраты: {request['expense_type_name']}\n"
        f"🏢 Поставщик: {request['supplier_name']}\n\n"
        f"💎 Стоимость: <b>{request_sum} сум</b>\n"
        f"💎 Запрошенная сумма в валюте: <b>{requested_currency}</b>\n"
        f"💵 Валюта: {request['currency']}\n"
        f"📈 Курс валюты: {request['exchange_rate']}\n"
        f"💳 Тип оплаты: {request['payment_type_name']}\n"
        f"💳 Карта перевода: {request.get('payment_card', '')}\n"
        f"📜 № Заявки в SAP: {request['sap_code']}\n"
        f"🕓 Дата оплаты: {request['payment_time'].strftime('%d.%m.%Y')}\n"
        f"💸 Фирма-плательщик: {request.get('payer_company_name', '')}\n\n"
        f"📝 Комментарии: {request['description']}"
    )
    city_name = context.user_data.get("request_details").get("city")
    trip_days = context.user_data.get("request_details").get("trip_days")
    if city_name and trip_days:
        request_text += (f"\n✈️ Коммандировка по направлению: {city_name}"
                         f"\n⏳ Количество дней: {trip_days}")
    budget_balance = context.user_data["request_details"]["budget_balance"]
    context.user_data["request_details"]["send_ceo"] = False

    if float(context.user_data["request_details"]["sum"]) > budget_balance and \
            context.user_data["request_details"][
                "over_budget"] == False:
        await update.message.reply_text(
            text="К сожалению, на балансе бюджета недостаточно средств для покрытия запрошенной суммы."
        )
        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return HOME

    else:
        if float(context.user_data["request_details"]["sum"]) > budget_balance and \
                context.user_data["request_details"]["over_budget"] == True:
            context.user_data["request_details"]["send_ceo"] = True

        await update.message.reply_text(
            text='Проверьте свою заявку ещё раз, если всё правильно, подтвердите её.'
        )
        await update.message.reply_text(
            text=request_text,
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"], ["Подтвердить"]], resize_keyboard=True),
            parse_mode='HTML'
        )
        return CONFIRM



async def confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirmation = update.message.text
    if confirmation == "Назад ⬅️":
        await update.message.reply_text(
            text='Укажите код заявки в SAP',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return SAP_CODE

    elif confirmation == "Подтвердить":
        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )

        if context.user_data["request_details"]["department_purchasable"] is True and context.user_data["request_details"]["expense_type_purchasable"] is True:
            context.user_data["new_request"]["purchase_approved"] = False

        if context.user_data["request_details"]["expense_type_checkable"] is True:
            context.user_data["new_request"]["checked_by_financier"] = False

        data = context.user_data["new_request"]
        response = api_routes.create_request(body=data)
        if response.status_code == 200:
            request = response.json()
            request_sum = format(int(request['sum']), ',').replace(',', ' ')
            if request.get('exchange_rate', None) is not None:
                requested_currency = format((float(request['sum']) / float(request['exchange_rate'])), ',').replace(',', ' ')
            else:
                requested_currency = request_sum

            request_text = (
                f"📌 Заявка #{request['number']}s\n\n"
                f"📅 Дата заявки: {datetime.strptime(request['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%d.%m.%Y')}\n"
                f"📍 Отдел: {request['department']['name']}\n"
                f"👤 Заявитель: {request['client']['fullname']}\n"
                f"📞 Номер заявителя: {request['client']['phone']}\n"
                f"🛒 Заказчик: {request['buyer']}\n"
                f"💰 Тип затраты: {request['expense_type']['name']}\n"
                f"🏢 Поставщик: {request['supplier']}\n\n"
                f"💎 Стоимость: <b>{request_sum} сум</b>\n"
                f"💎 Запрошенная сумма в валюте: <b>{requested_currency}</b>\n"
                f"💵 Валюта: {request['currency']}\n"
                f"📈 Курс валюты: {request['exchange_rate']}\n"
                f"💳 Тип оплаты: {request['payment_type']['name']}\n"
                f"💳 Карта перевода: {request['payment_card'] if request['payment_card'] is not None else ''}\n"
                f"📜 № Заявки в SAP: {request['sap_code']}\n"
                f"🕓 Дата оплаты: {datetime.strptime(request['payment_time'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y')}\n"
                f"💸 Фирма-плательщик: {request['payer_company']['name'] if request['payer_company'] is not None else ''}\n\n"
                f"📝 Комментарии: {request['description']}"
            )
            city_name = context.user_data.get("request_details").get("city")
            trip_days = context.user_data.get("request_details").get("trip_days")
            if city_name and trip_days:
                request_text += (f"\n✈️ Коммандировка по направлению: {city_name}"
                                 f"\n⏳ Количество дней: {trip_days}")
            # current_year = str(datetime.now().year)
            # current_month = str(datetime.now().month) if len(str(datetime.now().month)) > 1 else "0"+str(datetime.now().month)
            # current_date = str(datetime.now().date()) if len(str(datetime.now().date())) > 1 else "0"+str(datetime.now().date())
            if context.user_data["request_details"]["send_ceo"] == True:
                await update.message.reply_text(
                    text="Не осталось бюджетных средств, и заявка будет отправлена Гендиректору.\n"
                         "В случае одобрения будут выделены средства сверх бюджета !"
                )
                chat_id = APPROVE_GROUP
                sent_message = await context.bot.send_message(
                    chat_id=chat_id,  # WHERE CEO CAN APPROVE
                    text=request_text,
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text="Одобрить", callback_data="confirm"),
                                InlineKeyboardButton(text="Отказать", callback_data="refuse"),
                            ]
                        ]
                    ),
                    parse_mode='HTML'
                )
                if request["contract"]:
                    files = request["contract"]["file"]
                    for file in files:
                        file_paths = file["file_paths"]
                        for file_path in file_paths:
                            try:
                                await context.bot.send_document(
                                    chat_id=chat_id,
                                    document=f"{PROJECT_PATH}/{file_path}",
                                    reply_to_message_id=sent_message.message_id
                                )
                            except Exception as e:
                                error_message = (
                                    f"FINANCE BOT !!!\n"
                                    f"Couldn't send request № {request['number']} contract files to CEO group:"
                                )
                                error_sender(
                                    error_message=f"{error_message}\n\n{e}"
                                )
            else:
                text = f"Ваша заявка #{request['number']}s принята на обработку, как финансовый отдел примет её, вы получите срок оплаты"
                await update.message.reply_text(text)
                department_head = request["department"]["head"]
                purchasable_department = request["department"]["purchasable"]
                purchasable_expense = request["expense_type"]["purchasable"]
                if department_head:
                    chat_id = department_head["tg_id"]
                    try:
                        sent_message = await context.bot.send_message(
                            chat_id=chat_id,
                            text=request_text,
                            reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(text="Одобрить", callback_data="confirm"),
                                        InlineKeyboardButton(text="Отказать", callback_data="refuse")
                                    ]
                                ]
                            ),
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        error_message = (
                            f"FINANCE BOT !!!\n"
                            f"Couldn't send request № {request['number']} to head of department:"
                        )
                        error_sender(
                            error_message=f"{error_message}\n\n{e}"
                        )

                    if request["contract"]:
                        files = request["contract"]["file"]
                        for file in files:
                            file_paths = file["file_paths"]
                            for file_path in file_paths:
                                try:
                                    await context.bot.send_document(
                                        chat_id=chat_id,
                                        document=f"{PROJECT_PATH}/{file_path}",
                                        reply_to_message_id=sent_message.message_id
                                    )
                                except Exception as e:
                                    error_message = (
                                        f"FINANCE BOT !!!\n"
                                        f"Couldn't send request № {request['number']} contract files to head of department:"
                                    )
                                    error_sender(
                                        error_message=f"{error_message}\n\n{e}"
                                    )
                if purchasable_department is True:
                    if purchasable_expense is True:
                        chat_id = PURCHASE_GROUP
                        try:
                            sent_message = await context.bot.send_message(
                                chat_id=chat_id,
                                text=request_text,
                                parse_mode='HTML'
                            )
                        except Exception as e:
                            error_message = (
                                f"FINANCE BOT !!!\n"
                                f"Couldn't send request № {request['number']} to purchase group:"
                            )
                            error_sender(
                                error_message=f"{error_message}\n\n{e}"
                            )

                        if request["contract"]:
                            files = request["contract"]["file"]
                            for file in files:
                                file_paths = file["file_paths"]
                                for file_path in file_paths:
                                    try:
                                        await context.bot.send_document(
                                            chat_id=chat_id,
                                            document=f"{PROJECT_PATH}/{file_path}",
                                            reply_to_message_id=sent_message.message_id
                                        )
                                    except Exception as e:
                                        error_message = (
                                            f"FINANCE BOT !!!\n"
                                            f"Couldn't send request № {request['number']} contract files to purchase group:"
                                        )
                                        error_sender(
                                            error_message=f"{error_message}\n\n{e}"
                                        )

        else:
            error_sender(error_message=f"FINANCE BOT: \n{response.text}")
            await update.message.reply_text(text="Что-то пошло не так, отправьте заявку заново !")

        context.user_data.pop("new_request", None)
        context.user_data.pop("request_details", None)
        return HOME
