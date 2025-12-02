# import logging
import re
from datetime import datetime

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes

from configs.variables import APPROVE_GROUP, CEO
from handlers.conversation_handlers import HOME, MY_REQUESTS, PAYMENT_TIME
from keyboards import client_keyboards
from utils.api_requests import api_routes
from utils.utils import error_sender


async def inline_handler(update: Update, context: CallbackContext):
    query = update.inline_query.query
    query = query.strip().lower()
    # logging.info('inline: %s', query)

    # api_routes = ApiRoutes()

    # The list with similar elements
    results = []
    response = api_routes.get_departments(name=query)
    branches = response['items']
    for i, branch in enumerate(branches):
        results.append(
            InlineQueryResultArticle(
                id=str(i+1),
                title=branch["name"],
                input_message_content=InputTextMessageContent(
                    message_text=branch["id"]
                )
            )
        )

    # Nothing is found
    if query and not results:
        results.append(
            InlineQueryResultArticle(
                id=str(999),
                title="Ничего не нашлось!",
                input_message_content=InputTextMessageContent(
                    message_text=f"Не нашлось введенного филиала: {query}"
                )
            )
        )

    await update.inline_query.answer(
        results=results,
        cache_time=120
    )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data
    chat_type = str(query.message.chat.type)
    tg_id = query.from_user.id
    message_text = query.message.text or query.message.caption

    if chat_type in ["group", "supergroup"]:
        if tg_id != CEO:
            await query.answer(text="Вы не являетесь CEO !", show_alert=True)
            return None

    # Use regex to find the request number after "📌 Заявка #"
    match = re.search(r"📌 Заявка #(\d+)s", message_text)
    request_number = match.group(1)

    response = api_routes.get_requests(number=request_number)
    request = response.json()['items'][0]
    request_id = str(request['id'])

    if request['status'] == 5:
        await query.answer(text="Данная завка уже закрыта !", show_alert=True)
        return None

    response = api_routes.get_client(tg_id)
    client = response.json()
    client = client['items'][0]

    context.user_data.pop("new_request", None)
    context.user_data.pop("request_details", None)

    if callback_data == "refuse":
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Не подтверждаю", callback_data="not_confirm")],
                    [InlineKeyboardButton(text="Нужно переговорить", callback_data="discuss")],
                    [InlineKeyboardButton(text="Другое", callback_data="other")],
                    [InlineKeyboardButton(text="Назад ⬅️", callback_data="back")]
                ]
            )
        )

    elif callback_data == "back":
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Одобрить", callback_data="confirm"),
                        InlineKeyboardButton(text="Отказать", callback_data="refuse")
                    ]
                ]
            )
        )

    elif callback_data in ["not_confirm", "discuss", "other"]:
        deny_reason = ""
        if callback_data == "not_confirm":
            deny_reason = "Не подтверждаю"
        elif callback_data == "discuss":
            deny_reason = "Нужно переговорить"
        elif callback_data == "other":
            deny_reason = "Другое"

        body = {
            "id": request_id,
            "status": 4,
            "comment": deny_reason,
            "client_id": client["id"]
        }
        response = api_routes.update_request(body=body)
        if response.status_code == 200:
            request = response.json()
            await query.answer(text="Заявка отменена 🚫", show_alert=True)
            request_text = (f"{message_text}\n\n"
                            f"Отказано 🚫")
            if query.message.text:
                await query.edit_message_text(
                    text=request_text,
                    reply_markup=None
                )
            elif query.message.caption:
                await query.edit_message_caption(
                    caption=request_text,
                    reply_markup=None
                )
            try:
                await context.bot.send_message(
                    chat_id=request["client"]["tg_id"],
                    text=f"Заявка #{request['number']}s отклонена 🚫!\n\n"
                         f"Причина отклонения: {deny_reason}"
                )
            except Exception as e:
                print(e)
        else:
            error_sender(error_message=f"FINANCE BOT: \n{response.text}")

        await query.answer()

    elif callback_data == "confirm":
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Отложить", callback_data="delay")],
                    [InlineKeyboardButton(text="Подтвердить ✅", callback_data="pass")],
                    [InlineKeyboardButton(text="Назад ⬅️", callback_data="back")]
                ]
            )
        )

    elif callback_data == "delay":
        await query.answer()
        await query.message.reply_text(
            text="Введите дату оплаты в формате:  дд.мм.гггг (08.05.2025)"
        )
        context.user_data["request_info"] = {}
        context.user_data["request_info"]["text"] = (
            f"{message_text}\n\n"
            f"Подтверждено  ✅\n"
            f"Отложено  ⏳"
        )
        context.user_data["request_info"]["message_id"] = query.message.message_id
        context.user_data["request_info"]["client_tg_id"] = request["client"]["tg_id"]
        context.user_data["request_info"]["number"] = request["number"]

        context.user_data["request_updates"] = {}
        context.user_data["request_updates"]["id"] = request_id
        context.user_data["request_updates"]["approved"] = True
        context.user_data["request_updates"]["status"] = 6
        context.user_data["request_updates"]["client_id"] = client["id"]

        return PAYMENT_TIME

    elif callback_data == "pass":
        body = {
            "id": request_id,
            "approved": True,
            "client_id": client["id"]
        }
        response = api_routes.update_request(body=body)

        if response.status_code == 200:
            request = response.json()
            await query.answer(text="Заявка одобрена ✅", show_alert=True)
            request_text = (f"{message_text}\n\n"
                            f"Подтверждено ✅")
            if query.message.text:
                await query.edit_message_text(
                    text=request_text,
                    reply_markup=None
                )
            elif query.message.caption:
                await query.edit_message_caption(
                    caption=request_text,
                    reply_markup=None
                )

            try:
                # 2025-09-27T00:00:00Z <class 'str'>
                date_obj = datetime.strptime(request['payment_time'], "%Y-%m-%dT%H:%M:%SZ")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                balance_response = api_routes.get_budget_balance(
                    department_id=request['department']['id'],
                    expense_type_id=request['expense_type']['id'],
                    start_date=formatted_date,
                    finish_date=formatted_date
                )
                balance_sum = balance_response["value"] if balance_response else 0
                balance_sum = format(balance_sum, ',').replace(',', ' ')
                await query.message.reply_text(
                    text=f'На счёту "{request["expense_type"]["name"]}" вашего бюджета осталось: {balance_sum} сум'
                )
            except Exception as e:
                error_sender(error_message=f"FINANCE BOT: \n{e}")

            try:
                await context.bot.send_message(
                    chat_id=request["client"]["tg_id"],
                    text=f"Заявка #{request['number']}s одобрена !"
                )
            except Exception as e:
                error_sender(error_message=f"FINANCE BOT: \n{e}")
        elif response.status_code == 400:
            await query.answer(text="Заявка не может быть одобрена, недостаточно средств в бюджете ! ❌", show_alert=True)
        else:
            json_response = response.json()
            await query.answer(text=json_response["detail"], show_alert=True)
            error_sender(error_message=f'FINANCE BOT: \n{json_response["detail"]}')



async def my_requests_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tg_id = update.message.chat.id
    response = api_routes.get_client(tg_id)
    client = response.json()
    client = client.get('items', None)
    if client:
        client = client[0]["id"]
    else:
        client = None
        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return HOME

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
        status = "0,1,2,3,6"
        text = "Ваши активные заявки"

    await update.message.reply_text(text)
    response = api_routes.get_requests(client_id=client, status=status)
    requests = response.json()["items"]
    request_messages = [
        f"📌 Заявка #{request['number']}s\n\n"
        f"📅 Дата заявки: {datetime.strptime(request['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%d.%m.%Y')}\n"
        f"📍 Отдел: {request['department']['name']}\n"
        f"👤 Заявитель: {request['client']['fullname']}\n"
        f"📞 Номер заявителя: {request['client']['phone']}\n"
        f"🛒 Заказчик: {request['buyer']}\n"
        f"💰 Тип затраты: {request['expense_type']['name']}\n"
        f"🏢 Поставщик: {request['supplier']}\n\n"
        f"💎 Стоимость: <b>{format(int(request['sum']), ',').replace(',', ' ')} сум</b>\n"
        f"💎 Запрошенная сумма в валюте: <b>{format((float(request['sum']) / float(request['exchange_rate'])), ',').replace(',', ' ') if request.get('exchange_rate', None) is not None else format(int(request['sum']), ',').replace(',', ' ')}</b>\n"
        f"💵 Валюта: {request.get('currency', '')}\n"
        f"📈 Курс валюты: {request.get('exchange_rate', '')}\n"
        f"💳 Тип оплаты: {request['payment_type']['name']}\n"
        f"💳 Карта перевода: {request['payment_card'] if request['payment_card'] is not None else ''}\n"
        f"📜 № Заявки в SAP: {request['sap_code']}\n"
        f"🕓 Дата оплаты: {datetime.strptime(request['payment_time'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y') if request['payment_time'] is not None else ''}\n"
        f"💸 Фирма-плательщик: {request['payer_company']['name'] if request['payer_company'] is not None else ''}\n\n"
        f"📝 Комментарии: {request['description']}"
        for request in requests
    ]
    for message in request_messages:
        await update.message.reply_text(
            text=message,
            reply_markup=ReplyKeyboardMarkup(keyboard=[["Назад ⬅️"]], resize_keyboard=True),
            parse_mode='HTML'
        )

    return MY_REQUESTS
