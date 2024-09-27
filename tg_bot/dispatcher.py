import re
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from tg_bot.handlers.onboarding.handlers.base_hand.base_handler import open_buttons, start, button_menu_click
from tg_bot.handlers.onboarding.handlers.email_hand.email_handler import ASK_EMAIL, ASK_CODE, handle_email_button
from tg_bot.handlers.onboarding.manage_data import BACK_BUTTON, EMAIL_BUTTON


def get_handlers():
    conv_handler_email = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_email_button, pattern='^' + re.escape(EMAIL_BUTTON) + '$')],
        states={
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email_button)],
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email_button)],
        },
        fallbacks=[],
    )
    return [
        CommandHandler('start', start),
        CallbackQueryHandler(open_buttons, pattern=f'^{BACK_BUTTON}'),
        conv_handler_email,
        CallbackQueryHandler(button_menu_click),

        ]
