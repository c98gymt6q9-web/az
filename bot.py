#!/usr/bin/env python3
"""
🤖 Telegram Sales Bot - Готовый код для продажи файлов
Интеграция: Google Drive, SQLite DB, ручные платежи
"""

import os
import re
import json
import sqlite3
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ========== ЗАГРУЗКА КОНФИГА ==========
load_dotenv()

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== КОНФИГУРАЦИЯ ==========
from config import Config

TOKEN = Config.TELEGRAM_TOKEN
class Config:
    # Telegram
    TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    if not TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN не найден в .env файле!")

    # Google
    GOOGLE_FOLDER_ID = os.getenv("GOOGLE_FOLDER_ID", "")
    GOOGLE_SERVICE_ACCOUNT = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")

    if not GOOGLE_FOLDER_ID:
        raise ValueError("❌ GOOGLE_FOLDER_ID не найден в .env файле!")

    # Продукт
    PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Мой продукт")
    PRODUCT_PRICE = int(os.getenv("PRODUCT_PRICE", "499"))

    # Платежи
    PAYMENT_METHOD = os.getenv("PAYMENT_METHOD", "Яндекс.Касса")
    PAYMENT_ACCOUNT = os.getenv("PAYMENT_ACCOUNT", "410013XXXXXXXX")
    PAYMENT_NAME = os.getenv("PAYMENT_NAME", "Твое имя")
    PAYMENT_PHONE = os.getenv("PAYMENT_PHONE", "+79XXXXXXXXXX")

    # БД
    DB_NAME = "sales_bot.db"

# ========== БД ==========
class DB:
    def __init__(self):
        self.init()

    def init(self):
        """Инициализировать БД"""
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            status TEXT,
            created_at TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product TEXT,
            price REAL,
            status TEXT,
            created_at TEXT
        )''')

        conn.commit()
        conn.close()

    def add_user(self, user_id, username, email):
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO users
                    (user_id, username, email, status, created_at)
                    VALUES (?, ?, ?, ?, ?)''',
                 (user_id, username, email, 'pending', datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def add_purchase(self, user_id):
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO purchases (user_id, product, price, status, created_at)
                    VALUES (?, ?, ?, ?, ?)''',
                 (user_id, Config.PRODUCT_NAME, Config.PRODUCT_PRICE, 'pending', datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def update_status(self, user_id, status):
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute('UPDATE users SET status = ? WHERE user_id = ?', (status, user_id))
        c.execute('UPDATE purchases SET status = ? WHERE user_id = ? AND status = "pending"',
                 (status, user_id))
        conn.commit()
        conn.close()

    def get_user(self, user_id):
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result

    def count_purchases(self):
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM purchases WHERE status = "completed"')
        result = c.fetchone()[0]
        conn.close()
        return result

    def count_revenue(self):
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute('SELECT SUM(price) FROM purchases WHERE status = "completed"')
        result = c.fetchone()[0] or 0
        conn.close()
        return result

# ========== GOOGLE DRIVE ==========
class GDrive:
    def __init__(self):
        try:
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_SERVICE_ACCOUNT,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("✅ Google Drive подключен")
        except Exception as e:
            logger.error(f"❌ Ошибка Google Drive: {e}")
            self.service = None

    def share(self, email):
        """Добавить доступ к папке"""
        if not self.service:
            return False, "Google Drive недоступен"

        # Проверка Gmail
        if not email.endswith('@gmail.com'):
            return False, "❌ Используй только Gmail адрес (@gmail.com)"

        try:
            permission = {
                'type': 'user',
                'role': 'reader',
                'emailAddress': email
            }
            self.service.permissions().create(
                fileId=Config.GOOGLE_FOLDER_ID,
                body=permission,
                fields='id'
            ).execute()
            logger.info(f"✅ {email} добавлен в папку")
            return True, "✅ Доступ к папке выдан!"

        except HttpError as e:
            if "Invalid Sharing Request" in str(e):
                return False, "⚠️ Этот аккаунт уже имеет доступ"
            return False, f"❌ Ошибка: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            return False, "❌ Ошибка доступа"

# ========== БОТ ==========
WAITING_EMAIL, WAITING_CONFIRM, WAITING_PAYMENT = range(3)

db = DB()
gdrive = GDrive()

class SalesBot:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user

        keyboard = [
            [InlineKeyboardButton("💳 Купить", callback_data="buy")],
            [InlineKeyboardButton("📖 О продукте", callback_data="about")],
            [InlineKeyboardButton("📞 Контакты", callback_data="contact")]
        ]
        reply = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"Добро пожаловать в магазин 🏪\n\n"
            f"Что тебе нужно?",
            reply_markup=reply
        )

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопок"""
        query = update.callback_query
        await query.answer()

        if query.data == "buy":
            await query.edit_message_text(
                f"🛍️ **{Config.PRODUCT_NAME}**\n\n"
                f"💰 Цена: **{Config.PRODUCT_PRICE} руб.**\n\n"
                f"Введи свой **Gmail** адрес:"
            )
            return WAITING_EMAIL

        elif query.data == "about":
            await query.edit_message_text(
                f"📖 **О продукте**\n\n"
                f"🏷️ {Config.PRODUCT_NAME}\n"
                f"💵 {Config.PRODUCT_PRICE} руб.\n\n"
                f"Это отличный продукт для тебя! 🎁"
            )

        elif query.data == "contact":
            await query.edit_message_text(
                f"📞 **Контакты**\n\n"
                f"📱 Telegram: @your_username\n"
                f"✉️ Email: your-email@gmail.com\n"
                f"☎️ WhatsApp: {Config.PAYMENT_PHONE}"
            )

    async def get_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получить email"""
        email = update.message.text.strip().lower()

        # Валидация
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            await update.message.reply_text(
                "❌ Это не Gmail адрес\n\n"
                "Используй @gmail.com:"
            )
            return WAITING_EMAIL

        context.user_data['email'] = email

        # Подтверждение
        keyboard = [
            [InlineKeyboardButton("✅ Да", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ Нет", callback_data="confirm_no")]
        ]
        reply = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Email: **{email}**\n\nВерно?",
            reply_markup=reply
        )

        return WAITING_CONFIRM

    async def confirm_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтвердить email"""
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_no":
            await query.edit_message_text("Введи email еще раз:")
            return WAITING_EMAIL

        email = context.user_data['email']
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        # Сохраняем в БД
        db.add_user(user_id, username, email)
        db.add_purchase(user_id)

        # Показываем реквизиты
        payment_text = f"""💳 **РЕКВИЗИТЫ ПЛАТЕЖА**

📦 Товар: {Config.PRODUCT_NAME}
💰 Сумма: **{Config.PRODUCT_PRICE} руб.**
📧 Email: {email}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
**{Config.PAYMENT_METHOD}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 Счет: `{Config.PAYMENT_ACCOUNT}`
👤 Получатель: {Config.PAYMENT_NAME}
📱 Номер: {Config.PAYMENT_PHONE}

⏱️ **ИНСТРУКЦИЯ:**
1️⃣ Переведи деньги на реквизиты выше
2️⃣ Напиши мне доказательство платежа
3️⃣ Я добавлю тебя в папку с файлом
4️⃣ Готово! 🎉

❓ Вопросы? Напиши: {Config.PAYMENT_PHONE}
"""

        keyboard = [
            [InlineKeyboardButton("✅ Я оплатил(а)", callback_data="paid_yes")],
            [InlineKeyboardButton("❌ Отменить", callback_data="paid_no")]
        ]
        reply = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(payment_text, reply_markup=reply)

        return WAITING_PAYMENT

    async def confirm_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтвердить платеж"""
        query = update.callback_query
        await query.answer()

        if query.data == "paid_no":
            await query.edit_message_text("Отменено ❌")
            return ConversationHandler.END

        user_id = update.effective_user.id
        email = context.user_data['email']

        # Добавляем в Google папку
        success, msg = gdrive.share(email)

        if success:
            db.update_status(user_id, 'completed')
            purchases = db.count_purchases()
            revenue = db.count_revenue()

            await query.edit_message_text(
                f"""✅ **УСПЕШНО!**

{msg}

📂 Ссылка на папку:
https://drive.google.com/drive/folders/{Config.GOOGLE_FOLDER_ID}

Спасибо за покупку! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Всего продаж: {purchases}
💰 Доход: {revenue} руб.
"""
            )
        else:
            db.update_status(user_id, 'error')
            await query.edit_message_text(
                f"{msg}\n\n"
                f"❓ Напиши в поддержку: {Config.PAYMENT_PHONE}"
            )

        return ConversationHandler.END

# ========== MAIN ==========
def main():
    """Запуск бота"""
    logger.info("🤖 Запуск бота...")

    app = Application.builder().token(Config.TOKEN).build()
    bot = SalesBot()

    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(bot.button, pattern="^buy$")],
        states={
            WAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_email)],
            WAITING_CONFIRM: [CallbackQueryHandler(bot.confirm_email)],
            WAITING_PAYMENT: [CallbackQueryHandler(bot.confirm_payment)],
        },
        fallbacks=[CommandHandler("start", bot.start)],
    )

    # Обработчики
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(bot.button))

    logger.info("✅ Бот готов! Слушаю сообщения...")
    logger.info(f"📦 Продукт: {Config.PRODUCT_NAME} ({Config.PRODUCT_PRICE} руб.)")
    logger.info(f"💳 Метод: {Config.PAYMENT_METHOD}")

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
