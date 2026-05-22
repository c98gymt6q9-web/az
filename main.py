import os
import re
import json
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== КОНФИГУРАЦИЯ ====================
class Config:
    # Telegram
    TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"

    # Продукт
    PRODUCT_PRICE = 499  # Цена в рублях (или другой валюте)
    PRODUCT_NAME = "Мой продукт"
    PRODUCT_FILE_PATH = "path/to/your/file.pdf"  # Путь к файлу

    # Реквизиты (то, что видит пользователь)
    PAYMENT_DETAILS = {
        "method": "Яндекс.Касса",  # Можешь изменить на свой способ
        "account": "410013XXXXXXXX",
        "name": "Твое имя",
        "phone": "+79XXXXXXXXXX",
        "description": "Платеж за курс"
        # Или если используешь крипто:
        # "method": "Bitcoin",
        # "address": "1A1z7agoat..."
    }

    # Google Drive
    GOOGLE_SERVICE_ACCOUNT_JSON = "service_account.json"  # Файл сервис-аккаунта
    GOOGLE_FOLDER_ID = "YOUR_GOOGLE_FOLDER_ID"  # ID папки в Google Drive

    # База данных
    DB_NAME = "sales_bot.db"

# ==================== БД ====================
class Database:
    def __init__(self, db_name=Config.DB_NAME):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                telegram_name TEXT,
                email TEXT,
                purchase_date TEXT,
                payment_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица покупок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_name TEXT,
                price REAL,
                payment_method TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, user_id, telegram_name, email):
        """Добавить пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, telegram_name, email, purchase_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, telegram_name, email, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def add_purchase(self, user_id, product_name, price, payment_method):
        """Добавить покупку"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO purchases (user_id, product_name, price, payment_method, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (user_id, product_name, price, payment_method))

        conn.commit()
        conn.close()

    def update_payment_status(self, user_id, status):
        """Обновить статус платежа"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users SET payment_status = ? WHERE user_id = ?
        ''', (status, user_id))

        cursor.execute('''
            UPDATE purchases SET status = ?
            WHERE user_id = ? AND status = 'pending'
        ''', (status, user_id))

        conn.commit()
        conn.close()

    def get_user(self, user_id):
        """Получить информацию пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()

        return result

# ==================== GOOGLE DRIVE ====================
class GoogleDriveManager:
    def __init__(self, service_account_json, folder_id):
        self.service_account_json = service_account_json
        self.folder_id = folder_id
        self.service = self._get_service()

    def _get_service(self):
        """Получить сервис Google Drive"""
        try:
            credentials = Credentials.from_service_account_file(
                self.service_account_json,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Drive: {e}")
            return None

    def share_folder_with_user(self, user_email):
        """Поделиться папкой с пользователем"""
        if not self.service:
            return False, "Нет подключения к Google Drive"

        try:
            # Проверяем что это именно гугл аккаунт
            if not user_email.endswith('@gmail.com'):
                return False, "Используйте Google/Gmail аккаунт"

            # Даем доступ к папке
            permission = {
                'type': 'user',
                'role': 'reader',  # reader - только чтение, можно изменить на editor
                'emailAddress': user_email
            }

            self.service.permissions().create(
                fileId=self.folder_id,
                body=permission,
                fields='id'
            ).execute()

            logger.info(f"Папка поделена с {user_email}")
            return True, "✅ Доступ к папке выдан!"

        except HttpError as e:
            logger.error(f"Ошибка Google Drive: {e}")
            if "Invalid Sharing Request" in str(e):
                return False, "❌ Ошибка: Возможно, этот аккаунт уже имеет доступ"
            return False, f"❌ Ошибка при доступе: {str(e)}"
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")
            return False, f"❌ Ошибка: {str(e)}"

# ==================== СОСТОЯНИЯ РАЗГОВОРА ====================
CHOOSING, EMAIL, CONFIRM_PAYMENT, WAIT_PAYMENT, CONFIRM_EMAIL = range(5)

# ==================== ОБРАБОТЧИКИ ====================
class SalesBot:
    def __init__(self):
        self.db = Database()
        self.drive_manager = GoogleDriveManager(
            Config.GOOGLE_SERVICE_ACCOUNT_JSON,
            Config.GOOGLE_FOLDER_ID
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        keyboard = [
            [InlineKeyboardButton("💳 Купить продукт", callback_data="buy")],
            [InlineKeyboardButton("❓ О продукте", callback_data="about")],
            [InlineKeyboardButton("📞 Контакты", callback_data="contacts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            f"Добро пожаловать в магазин!\n\n"
            f"Что тебе нужно?",
            reply_markup=reply_markup
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопок"""
        query = update.callback_query
        await query.answer()

        if query.data == "buy":
            await query.edit_message_text(
                f"🛍️ **{Config.PRODUCT_NAME}**\n\n"
                f"Цена: **{Config.PRODUCT_PRICE} руб.**\n\n"
                f"Для покупки нужна твоя Google почта.\n\n"
                f"Введи свой email (gmail.com):"
            )
            return CHOOSING

        elif query.data == "about":
            await query.edit_message_text(
                f"📖 **О продукте**\n\n"
                f"Название: {Config.PRODUCT_NAME}\n"
                f"Цена: {Config.PRODUCT_PRICE} руб.\n\n"
                f"[Добавь подробное описание]"
            )

        elif query.data == "contacts":
            await query.edit_message_text(
                f"📞 **Наши контакты**\n\n"
                f"Email: your-email@gmail.com\n"
                f"Telegram: @your_username\n"
                f"WhatsApp: +79XXXXXXXXXX"
            )

    async def get_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получить email от пользователя"""
        email = update.message.text.strip().lower()
        user = update.effective_user

        # Валидация Gmail
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            await update.message.reply_text(
                "❌ Это не Google/Gmail email.\n\n"
                "Пожалуйста, используй именно @gmail.com адрес:"
            )
            return EMAIL

        # Сохраняем email в контекст
        context.user_data['email'] = email
        context.user_data['user_id'] = user.id
        context.user_data['telegram_name'] = user.username or user.first_name

        # Подтверждение
        keyboard = [
            [InlineKeyboardButton("✅ Да, верно", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ Нет, другой email", callback_data="confirm_no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Твой email: **{email}**\n\n"
            f"Это верно?",
            reply_markup=reply_markup
        )

        return CONFIRM_EMAIL

    async def confirm_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтвердить email"""
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_no":
            await query.edit_message_text("Введи свой Gmail email:")
            return EMAIL

        elif query.data == "confirm_yes":
            email = context.user_data['email']

            # Показываем реквизиты
            payment_text = self._format_payment_details(email)

            keyboard = [
                [InlineKeyboardButton("✅ Я оплатил(а)", callback_data="paid_yes")],
                [InlineKeyboardButton("❌ Отменить", callback_data="paid_no")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                payment_text,
                reply_markup=reply_markup
            )

            return WAIT_PAYMENT

    def _format_payment_details(self, email):
        """Форматировать реквизиты платежа"""
        details = Config.PAYMENT_DETAILS

        text = f"""💳 **РЕКВИЗИТЫ ДЛЯ ПЛАТЕЖА**

📦 Товар: {Config.PRODUCT_NAME}
💰 Сумма: {Config.PRODUCT_PRICE} руб.
📧 Email: {email}

**Способ оплаты: {details['method']}**

"""

        if details['method'] == "Яндекс.Касса":
            text += f"""💳 Номер счета: `{details['account']}`
👤 Получатель: {details['name']}
📞 Номер телефона: {details['phone']}

Описание платежа: {details['description']}
"""
        elif details['method'] == "Bitcoin":
            text += f"""₿ Адрес: `{details['address']}`

⚠️ ВНИМАНИЕ: Скопируй адрес точно, проверь еще раз!
"""

        text += f"""
⏱️ **После оплаты:**
1. Подтверди платеж в боте
2. Я добавлю тебя в Google папку с файлом
3. Готово! Получи доступ к продукту

❓ Возникли проблемы? Напиши: {Config.PAYMENT_DETAILS.get('phone', 'нет контакта')}
"""

        return text

    async def wait_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ожидание подтверждения платежа"""
        query = update.callback_query
        await query.answer()

        if query.data == "paid_no":
            await query.edit_message_text("Покупка отменена. Жаль 😢\n\nМожешь начать заново: /start")
            return ConversationHandler.END

        elif query.data == "paid_yes":
            user_id = context.user_data['user_id']
            email = context.user_data['email']
            telegram_name = context.user_data['telegram_name']

            # Сохраняем в БД
            self.db.add_user(user_id, telegram_name, email)
            self.db.add_purchase(user_id, Config.PRODUCT_NAME, Config.PRODUCT_PRICE, Config.PAYMENT_DETAILS['method'])

            # Добавляем в Google папку
            success, message = self.drive_manager.share_folder_with_user(email)

            if success:
                self.db.update_payment_status(user_id, 'completed')

                await query.edit_message_text(
                    f"""✅ **ПЛАТЕЖ ПОДТВЕРЖДЕН!**

{message}

📂 Ссылка на папку: https://drive.google.com/drive/folders/{Config.GOOGLE_FOLDER_ID}

Спасибо за покупку! 🎉
"""
                )
            else:
                await query.edit_message_text(
                    f"""⚠️ **ОШИБКА**

{message}

Пожалуйста, напиши в поддержку: {Config.PAYMENT_DETAILS.get('phone')}
Передай этот текст: Платеж {user_id}
"""
                )

            return ConversationHandler.END

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================
def main():
    """Запуск бота"""
    bot = SalesBot()

    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(bot.button_callback, pattern="^buy$")],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_email)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_email)],
            CONFIRM_EMAIL: [CallbackQueryHandler(bot.confirm_email)],
            WAIT_PAYMENT: [CallbackQueryHandler(bot.wait_payment)],
        },
        fallbacks=[CommandHandler("start", bot.start)],
    )

    # Обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(bot.button_callback))

    # Запуск
    logger.info("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
