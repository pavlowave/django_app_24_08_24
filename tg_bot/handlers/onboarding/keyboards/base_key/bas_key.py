from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.handlers.onboarding.manage_data import DIRECTORY_BUTTON, MY_PROFILE_BUTTON, HELP_BUTTON, \
    CALCULATION_CALORIES


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Справочник', callback_data=f'{DIRECTORY_BUTTON}')],
        [InlineKeyboardButton('Мой профиль', callback_data=f'{MY_PROFILE_BUTTON}')],
        [InlineKeyboardButton('Норма калорий', callback_data=f'{CALCULATION_CALORIES}')],
        [InlineKeyboardButton('Помощь', callback_data=f'{HELP_BUTTON}')]
    ]

    return InlineKeyboardMarkup(buttons)