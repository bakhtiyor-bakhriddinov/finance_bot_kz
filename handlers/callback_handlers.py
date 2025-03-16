# import logging
import re

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import CallbackContext, ContextTypes
from utils.api_requests import api_routes


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

    # Use regex to find the request number
    match = re.search(r"Номер заявки:\s+(\d+)", query.message.text)
    request_number = match.group(1)

    response = api_routes.get_requests(number=request_number)
    request = response.json()['items'][0]
    request_id = str(request['id'])

    if callback_data == "refuse":
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Не подтверждаю", callback_data="not_confirm")],
                    [InlineKeyboardButton(text="Нужно переговорить", callback_data="discuss")],
                    [InlineKeyboardButton(text="Другое", callback_data="other")]
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
            "comment": deny_reason
        }
        response = api_routes.update_request(body=body)
        if response.status_code == 200:
            request = response.json()
            await query.answer(text="Заявка отменена 🚫", show_alert=True)
            request_text = query.message.text
            await query.edit_message_text(
                text=f"{request_text}\n\n"
                     f"Отказано 🚫",
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

        await query.answer()
    elif callback_data == "confirm":
        body = {
            "id": request_id,
            "approved": True
        }
        response = api_routes.update_request(body=body)
        if response.status_code == 200:
            request = response.json()
            await query.answer(text="Заявка одобрена ✅", show_alert=True)
            # await query.edit_message_reply_markup(reply_markup=None)
            request_text = query.message.text
            await query.edit_message_text(
                text=f"{request_text}\n\n"
                     f"Подтверждено ✅",
                reply_markup=None
            )
            try:
                await context.bot.send_message(
                    chat_id=request["client"]["tg_id"],
                    text=f"Заявка #{request['number']}s одобрена !"
                )
            except Exception as e:
                print(e)
