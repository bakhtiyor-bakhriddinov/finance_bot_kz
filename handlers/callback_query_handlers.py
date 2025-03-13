from telegram import Update
from telegram.ext import ContextTypes
from keyboards import freezer_keyboards
# from utils.api_requests import ApiRoutes


# api_routes = ApiRoutes()


# async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # tg_id = update.message.chat.id
#     query = update.callback_query
#     await query.delete_message()
#     user_orders = api_routes.get_orders(branch_id=context.user_data["branch_id"])
#     keyboard = (await freezer_keyboards.my_orders(user_orders, context.user_data["username"]))
#     await update.message.reply_text(
#         text=keyboard['text'],
#         reply_markup=keyboard['markup']
#     )