import asyncio
import re
import logging
import secrets
import string

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from tg_bot.handlers.onboarding.manage_data import EMAIL_BUTTON
from tg_bot.handlers.onboarding.utils.info import extract_user_data_from_update

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
User = get_user_model()
# Определение состояний
ASK_EMAIL, ASK_CODE = range(2)


async def handle_email_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    current_state = context.user_data.get('current_state')
    if query:
        data = query.data
        logger.info(f"Received callback_data: {data}")
        await query.answer()  # Закрывает callback query
        if data == EMAIL_BUTTON:
            await asyncio.sleep(0.4)
            await query.message.delete()
            await asyncio.sleep(0.4)
            # Ответ на callback_query, чтобы Telegram закрыл кнопку загрузки
            new_message = await context.bot.send_message(
                chat_id=user_id,
                text='Введите ваш email:',
                parse_mode=ParseMode.HTML
            )
            context.user_data['current_state'] = ASK_EMAIL
            context.user_data['current_message_id'] = new_message.message_id
            logger.info(f"Current state: {context.user_data.get('current_state')}")
            return
        print('assdasda')
    if update.message:
        print('kek')
        user_text = update.message.text.lower()
        old_message_id = context.user_data.get('current_message_id')
        context.user_data['current_state'] = ASK_EMAIL
        if old_message_id:
            await asyncio.sleep(0.4)
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=old_message_id)
            except Exception as e:
                logging.error(f"Failed to delete message: {e}")
        logger.info(f"Current state is: {current_state}")
        logger.info("Checking if state is ASK_EMAIL")

        if current_state == ASK_EMAIL:
            user_email = user_text
            logger.info(f"Processing email input: {user_email}")

            # Валидация email с помощью Django
            try:
                validate_email(user_email)
                logger.info(f"Email {user_email} is valid.")
            except ValidationError:
                logger.info(f"Invalid email entered: {user_email}")
                await update.message.reply_text("Некорректный email. Пожалуйста, введите корректный адрес.")
                return ASK_EMAIL

            # Получаем или создаем пользователя
            user, created = User.objects.get_or_create(email=user_email)
            new_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

            # Сохраняем код в пароле пользователя
            user.set_password(new_code)
            user.is_active = False
            user.save(update_fields=["password", "is_active"])

            # Асинхронная отправка email с кодом
            try:
                await context.application.loop.run_in_executor(
                    None,
                    send_mail,
                    "Ваш код подтверждения",
                    f"Ваш код подтверждения: {new_code}",
                    "noreply@yourproject.com",
                    [user_email]
                )
            except Exception as e:
                await update.message.reply_text("Ошибка при отправке письма. Попробуйте снова позже.")
                return ASK_EMAIL

            # Отправляем код в Telegram через бота
            try:
                await send_verification_code_to_telegram(user, new_code)
            except Exception as e:
                await update.message.reply_text("Ошибка при отправке сообщения в Telegram. Попробуйте снова позже.")
                return ASK_EMAIL

            # Сохраняем email в контексте для дальнейшей проверки
            context.user_data['email'] = user_email

            await update.message.reply_text(
                "Код подтверждения был отправлен на ваш email. Пожалуйста, введите его:"
            )
            return ASK_CODE

        elif current_state == ASK_CODE:
            user_code = update.message.text
            user_email = context.user_data.get('email')

            if not user_email:
                await update.message.reply_text("Ошибка: Email не найден. Пожалуйста, начните регистрацию заново.")
                return ASK_EMAIL

            # Получаем пользователя по email
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                await update.message.reply_text("Ошибка: Пользователь не найден. Пожалуйста, начните регистрацию заново.")
                return ASK_EMAIL

            # Проверяем код
            if user.check_password(user_code):
                user.is_active = True  # Активируем пользователя
                user.save(update_fields=["is_active"])

                await update.message.reply_text("Регистрация успешно завершена! Ваш аккаунт активирован.")
                context.user_data.clear()  # Очищаем состояние для следующего использования
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    "Неверный код. Пожалуйста, введите правильный код или начните регистрацию заново.")
                return ASK_CODE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # query = update.callback_query
    """
    Обработчик для отмены текущей операции.
    """
    # await query.answer()
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END
