from telegram.ext import Application, CommandHandler, InlineQueryHandler, ConversationHandler, MessageHandler, \
    filters, PicklePersistence, CallbackQueryHandler
from configs.variables import BOT_TOKEN
from handlers.command_handlers import help_command, custom_command, start_command
from handlers.conversation_handlers import *
from handlers.inline_handlers import handle_callback_query


# from handlers.inline_handlers import inline_handler


def main() -> None:
    """Run the bot."""
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    # application.add_handler(InlineQueryHandler(inline_handler))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth)],
            USER_REG: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_reg)],
            HOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, home_selection)],
            MY_REQUESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, my_requests_handler)],
            DEPARTMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, department_handler)],
            EXPENSE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, expense_type_handler)],
            BUYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, buyer_handler)],
            SUPPLIER: [MessageHandler(filters.TEXT & ~filters.COMMAND, supplier_handler)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_handler)],
            SUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, sum_handler)],
            PAYMENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_type_handler)],
            PAYMENT_DETAIL: [
                MessageHandler(filters.Document.FileExtension("pdf") | filters.Document.FileExtension("png") | filters.Document.FileExtension("docx"), payment_detail_handler),
                # MessageHandler(filters.Document.PDF | filters.Document.IMAGE | filters.Document.DOCX, payment_detail_handler),
                MessageHandler(filters.PHOTO, payment_detail_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_detail_handler),
            ],
            # PAYMENT_DETAIL: [MessageHandler(filters.Document.ALL & ~filters.TEXT & ~filters.COMMAND, payment_detail_handler)],
            SAP_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sap_code_handler)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation_handler)]
        },
        fallbacks=[CommandHandler('start', start_command)],
        allow_reentry=True,
        name="my_conversation",
        persistent=True,
        per_chat=True
    )

    application.add_handler(conv_handler)

    # Handle commands, but when user is not in a conversation
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('custom', custom_command))

    # Log all errors
    # application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()
