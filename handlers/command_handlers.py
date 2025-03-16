from telegram import Update
from telegram.ext import ContextTypes
from .conversation_handlers import AUTH, HOME
from utils.api_requests import api_routes
from keyboards import client_keyboards


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tg_id = update.message.chat.id
    response = api_routes.get_client(tg_id)
    print("CLIENT RESPONSE: \n", response.text)
    client = response.json()
    print("CLIENT: \n", client)
    client = client['items']
    context.user_data["client"] = {}
    context.user_data["client"]["tg_id"] = tg_id
    context.user_data["client"]["language"] = "ru"
    if client:
        client = client[0]
        context.user_data["client"]["id"] = client["id"]
        context.user_data["client"]["fullname"] = client["fullname"]
        context.user_data["client"]["phone"] = client["phone"]
        keyboard = (await client_keyboards.home_keyboard())
        await update.message.reply_text(
            text=keyboard['text'],
            reply_markup=keyboard['markup']
        )
        return HOME
    else:
        await update.message.reply_text(
            'Здравствуйте.\n'
            'Это корпоративный бот компании Safia.\n'
            'Пожалуйста введите пароль:'
        )
        await update.message.reply_text(
            'Если у вас её нет, обратитесь к системному администратору вашей компании.'
        )
        return AUTH


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Здравствуйте.\n'
        'Это корпоративный бот компании Safia.\n'
        'Пожалуйста введите пароль:'
    )


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Здравствуйте.\n'
        'Это корпоративный бот компании Safia.\n'
        'Пожалуйста введите пароль:'
    )
