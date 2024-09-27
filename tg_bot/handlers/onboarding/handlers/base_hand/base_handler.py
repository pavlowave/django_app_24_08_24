import logging
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ContextTypes

from tg_bot.handlers.onboarding.keyboards.base_key.bas_key import make_keyboard_for_start_command
from tg_bot.handlers.onboarding.manage_data import MY_PROFILE_BUTTON, DIRECTORY_BUTTON, CALCULATION_CALORIES, \
    HELP_BUTTON, BACK_BUTTON
from tg_bot.handlers.onboarding.utils.info import extract_user_data_from_update

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
User = get_user_model()


async def start(update: Update, context: CallbackContext) -> None:
    user_data = extract_user_data_from_update(update)
    # Используем sync_to_async для вызова синхронного метода класса
    user, created = await sync_to_async(User.get_or_create_user)(user_data)
    text = "Привет! Я фитнес бот. Твой помощник."
    await context.bot.send_message(
        chat_id=user_data['user_id'],
        text=text,
        reply_markup=make_keyboard_for_start_command(),
    )


async def open_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = extract_user_data_from_update(update)['user_id']
    text = "kek"
    await context.bot.edit_message_text(
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        text=text,
        reply_markup=make_keyboard_for_start_command()
    )


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = extract_user_data_from_update(update)['user_id']
    await context.bot.send_message(
        chat_id=user_id,
        text="Возвращаемся в главное меню.",
        reply_markup=make_keyboard_for_start_command()
    )


async def button_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user_id = extract_user_data_from_update(update)['user_id']

    if data == DIRECTORY_BUTTON:
        pass
        # text = 'Справочник:'
        # await context.bot.edit_message_text(
        #     chat_id=user_id,
        #     message_id=query.message.message_id,
        #     text=text,
        #     parse_mode=ParseMode.HTML,
        #     reply_markup=make_keyboard_for_directory()
        # )
    elif data == MY_PROFILE_BUTTON:
        # Обернем вызов filter и exists в sync_to_async
        user = await sync_to_async(User.objects.filter)(email__icontains=f'{user_id}@telegram.com')
        user_exists = await sync_to_async(user.exists)()

        if user_exists:
            # Если email имеет формат @telegram.com, это означает, что email не привязан
            buttons = [
                [InlineKeyboardButton('Привязать email', callback_data='bind_email')],
                [InlineKeyboardButton('Назад', callback_data=BACK_BUTTON)]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            text = "У вас еще нет привязанного email. Пожалуйста, привяжите ваш email."
        else:
            # Если email отличается, предложите изменить
            user_instance = await sync_to_async(user.first)()  # Получаем первого пользователя
            email = user_instance.email if user_instance else "Email не найден"
            buttons = [
                [InlineKeyboardButton('Изменить email', callback_data='change_email')],
                [InlineKeyboardButton('Назад', callback_data=BACK_BUTTON)]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            text = f'Ваш email: {email}'

        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    elif data == CALCULATION_CALORIES:
        pass

    elif data == HELP_BUTTON:
        pass

    await query.answer()