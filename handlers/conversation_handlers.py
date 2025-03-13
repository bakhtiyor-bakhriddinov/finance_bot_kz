# import logging
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import ContextTypes

from keyboards import client_keyboards
from utils.api_requests import api_routes

# Define states
(
    AUTH,
    USER_REG,
    HOME,
    MY_REQUESTS,
    DEPARTMENTS,
    EXPENSE_TYPE,
    BUYER,
    SUPPLIER,
    DESCRIPTION,
    SUM,
    PAYMENT_TYPE,
    PAYMENT_DETAIL,
    SAP_CODE,
    CONFIRM
) = range(14)




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
            text='Укажите свой номер'
        )
        context.user_data["client"]["phone"] = None
        return USER_REG

    elif context.user_data["client"]["phone"] is None:
        context.user_data["client"]["phone"] = user_input

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


async def my_requests_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    part_name = update.message.text
    if part_name == "Назад ⬅️":
        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return HOME

    status = 5
    text = ''
    if part_name == "Архив":
        status = "4,5"
        text = "Ваши заявки в архиве"
    elif part_name == "Актив":
        status = "0,1,2,3"
        text = "Ваши активные заявки"

    await update.message.reply_text(text)
    response = api_routes.get_requests(client_id=context.user_data["client"]["id"], status=status)
    requests = response.json()["items"]
    request_messages = [
        f"Номер заявки: {request['number']}\n"
        f"Отдел: {request['department']['name']}\n"
        f"Заказчик: {request['client']['fullname']}\n"
        f"Номер заказчика: {request['client']['phone']}\n"
        f"Закупщик: {request['buyer']['name']}\n"
        f"Тип затраты: {request['expense_type']['name']}\n"
        f"Поставщик:  {request['supplier']['name']}\n\n"
        f"Стоимость: {request['sum']} сум\n"
        f"Тип оплаты: {request['payment_type']['name']}\n"
        f"Карта перевода: {request['payment_card']}\n"
        f"Дата заявки: {datetime.strptime(request['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d.%m.%Y')}\n"
        f"№ Заявки в SAP: {request['sap_code']}\n\n"
        f"Комментарии: {request['description']}"
        for request in requests
    ]
    for message in request_messages:
        await update.message.reply_text(
            text=message,
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True)
        )

    return MY_REQUESTS


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
    department_id = response["items"][0]["id"]
    context.user_data["new_request"]["status"] = 0
    context.user_data["new_request"]["department_id"] = department_id
    context.user_data["request_details"]["department_name"] = department_name

    keyboard = (await client_keyboards.expense_types_keyboard())
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
    expense_type_id = response[0]["id"]
    context.user_data["new_request"]["expense_type_id"] = expense_type_id
    context.user_data["request_details"]["expense_type_name"] = expense_type_name

    keyboard = (await client_keyboards.buyers_keyboard())
    await update.message.reply_text(
        text=keyboard['text'],
        reply_markup=keyboard['markup']
    )
    return BUYER



async def buyer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buyer_name = update.message.text
    if buyer_name == "Назад ⬅️":
        keyboard = (await client_keyboards.expense_types_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return EXPENSE_TYPE

    response = api_routes.get_buyers(name=buyer_name)
    buyer_id = response[0]["id"]
    context.user_data["new_request"]["buyer_id"] = buyer_id
    context.user_data["request_details"]["buyer_name"] = buyer_name

    keyboard = (await client_keyboards.suppliers_keyboard())
    await update.message.reply_text(
        text=keyboard['text'],
        reply_markup=keyboard['markup']
    )
    return SUPPLIER


async def supplier_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    supplier_name = update.message.text
    if supplier_name == "Назад ⬅️":
        keyboard = (await client_keyboards.buyers_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return BUYER

    response = api_routes.get_suppliers(name=supplier_name)
    supplier_id = response[0]["id"]
    context.user_data["new_request"]["supplier_id"] = supplier_id
    context.user_data["request_details"]["supplier_name"] = supplier_name

    await update.message.reply_text(
        text='Введите комментарии',
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return DESCRIPTION


async def description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    description = update.message.text
    if description == "Назад ⬅️":
        keyboard = (await client_keyboards.suppliers_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return SUPPLIER

    context.user_data["new_request"]["description"] = description
    context.user_data["request_details"]["description"] = description

    await update.message.reply_text(
        text='Укажите сумму, в сумм',
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return SUM


async def sum_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sum = update.message.text
    if sum == "Назад ⬅️":
        await update.message.reply_text(
            text='Введите комментарии',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return DESCRIPTION

    sum_number = sum.isdigit()
    if sum_number:
        context.user_data["new_request"]["sum"] = sum
        context.user_data["request_details"]["sum"] = sum

        keyboard = (await client_keyboards.payment_types_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return PAYMENT_TYPE

    else:
        await update.message.reply_text(
            text='Укажите сумму, в сумм. Используйте только числа'
        )
        return SUM


async def payment_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    payment_type_name = update.message.text
    if payment_type_name == "Назад ⬅️":
        await update.message.reply_text(
            text='Укажите сумму, в сумм',
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return SUM

    response = api_routes.get_payment_types(name=payment_type_name)
    payment_type_id = response[0]["id"]
    context.user_data["new_request"]["payment_type_id"] = payment_type_id
    context.user_data["request_details"]["payment_type_name"] = payment_type_name

    text = ''
    if "Наличные" in payment_type_name:
        context.user_data["new_request"]["cash"] = context.user_data["new_request"]["sum"]
        text = 'Укажите код заявки в SAP'
        await update.message.reply_text(
            text=text,
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return SAP_CODE

    elif "Перечисление" in payment_type_name:
        text = 'Отправьте договор в формате: pdf , png , docx.'

    elif "Перевод" in payment_type_name:
        text = 'Укажите номер карты, куда нужно сделать перевод средств'

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return PAYMENT_DETAIL


async def payment_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    payment_card = update.message.text
    if payment_card == "Назад ⬅️":
        keyboard = (await client_keyboards.payment_types_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return PAYMENT_TYPE

    document = update.message.document
    photo = update.message.photo
    # print("document: ", document)
    # print("photo: ", photo)
    # print("payment_card: ", payment_card)
    if payment_card:
        context.user_data["new_request"]["payment_card"] = payment_card
        context.user_data["request_details"]["payment_card"] = payment_card

    elif document or photo:
        context.user_data["new_request"]["contract"] = True
        if document:  # ✅ If the user sends a document
            file_id = document.file_id
            file_name = document.file_name
            mime_type = document.mime_type
        elif photo:  # ✅ If the user sends a photo
            file_id = photo[-1].file_id  # Get the best quality image
            file_name = photo[-1].file_unique_id
            mime_type = "image/png"
        else:
            await update.message.reply_text("⚠️ 'Отправьте договор в формате: pdf , png , docx.'")
            return PAYMENT_DETAIL

        file = await context.bot.get_file(file_id)  # Get the file object
        binary_data = await file.download_as_bytearray()  # Download file as binary data
        # Prepare file for upload
        files = [
            (
                "files", (file_name, binary_data, mime_type)
            )
        ]
        response = api_routes.upload_files(files=files)
        # print("uploaded file: ", response.text)
        response = response.json()
        context.user_data["new_request"]["file_paths"] = response["file_paths"]

    text = 'Укажите код заявки в SAP'
    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return SAP_CODE



async def sap_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sap_code = update.message.text
    if sap_code == "Назад ⬅️":
        if "payment_card" in context.user_data["new_request"] or "contract" in context.user_data["new_request"]:
            text = ''
            if "payment_card" in context.user_data["new_request"]:
                text='Укажите номер карты, куда нужно сделать перевод средств'
            elif "contract" in context.user_data["new_request"]:
                text='Отправьте договор в формате: pdf , png , docx.'

            await update.message.reply_text(text)
            return PAYMENT_DETAIL
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

    await update.message.reply_text(
        text='Проверьте свою заявку ещё раз, если всё правильно, подтвердите её.'
    )
    request = context.user_data["request_details"]
    request_text = (
        f"Отдел: {request['department_name']}\n"
        f"Заказчик: {context.user_data['client']['fullname']}\n"
        f"Номер заказчика: {context.user_data['client']['phone']}\n"
        f"Закупщик: {request['buyer_name']}\n"
        f"Тип затраты: {request['expense_type_name']}\n"
        f"Поставщик:  {request['supplier_name']}\n\n"
        f"Стоимость: {request['sum']} сум\n"
        f"Тип оплаты: {request['payment_type_name']}\n"
        f"Карта перевода: {request.get('payment_card', '')}\n"
        f"Дата заявки: {datetime.now().date().strftime('DD.MM.YYYY')}\n"
        f"№ Заявки в SAP:   {request['sap_code']}\n\n"
        f"Комментарии:  {request['description']}"
    )
    await update.message.reply_text(
        text=request_text,
        reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"], ["Подтвердить"]], resize_keyboard=True)
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
        data = context.user_data["new_request"]
        response = api_routes.create_request(body=data)
        if response.status_code == 200:
            request = response.json()
            text = f"Ваша заявка #{request['number']}s принята на обработку, как финансовый отдел примет её, вы получите срок оплаты"
            await update.message.reply_text(text)

            request_text = (
                f"Отдел: {request['department']['name']}\n"
                f"Заказчик: {request['client']['fullname']}\n"
                f"Номер заказчика: {request['client']['phone']}\n"
                f"Закупщик: {request['buyer']['name']}\n"
                f"Тип затраты: {request['expense_type']['name']}\n"
                f"Поставщик:  {request['supplier']['name']}\n\n"
                f"Стоимость: {request['sum']} сум\n"
                f"Тип оплаты: {request['payment_type']['name']}\n"
                f"Карта перевода: {request['payment_card']}\n"
                f"Дата заявки: {request['created_at']}\n"
                f"№ Заявки в SAP:   {request['sap_code']}\n\n"
                f"Комментарии:  {request['description']}"
            )
            await context.bot.send_message(
                chat_id=request["department"]["head"]["tg_id"],
                text=request_text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="Да", callback_data=f"{request['id']}")
                        ]
                    ]
                )
            )
            keyboard = (await client_keyboards.home_keyboard())
            await update.message.reply_text(
                text=keyboard['text'],
                reply_markup=keyboard['markup']
            )
            return HOME
        else:
            await update.message.reply_text(text="Что-то пошло не так, отправьте заново заявку, после отправки команды /start")

