# import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
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
    request_id = str(query.data)
    body = {
        "id": request_id,
        "approved": True
    }
    response = api_routes.update_request(body=body)
    if response.status_code == 200:
        request = response.json()
        await query.edit_message_reply_markup(reply_markup=None)
        await query.answer(text="Заявка одобрена ✅", show_alert=True)
        await context.bot.send_message(
            chat_id=request["client"]["tg_id"],
            text=f"Заявка #{request['number']}s одобрена !"
        )

