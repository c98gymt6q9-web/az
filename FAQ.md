# ❓ FAQ - Часто задаваемые вопросы

## 🤖 Telegram Bot

### Q: Где взять TELEGRAM_TOKEN?
**A:** 
1. Напиши боту [@BotFather](https://t.me/botfather)
2. Команда `/newbot`
3. Следуй инструкциям
4. Получишь токен вида: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### Q: Бот не отвечает
**A:** Проверь:
- Правильный ли токен в конфиге?
- Интернет подключен?
- Консоль показывает ошибки?
- Попробуй `python main.py` в консоли

### Q: Можно ли использовать бот на разных серверах одновременно?
**A:** **Нет!** Один токен = один процесс. Если запустишь на 2 серверах - будут конфликты.

### Q: Как сделать так, чтобы бот работал 24/7?
**A:** Используй:
- **Heroku** (бесплатно, но с ограничениями)
- **AWS/Google Cloud** (платно, но надежно)
- **Dedicated Server** (VPS)
- **Домашний компьютер** (всегда включен)

Рекомендуемо: **VPS на Hetzner** (~3$/месяц)

---

## 📧 Google Drive & Email

### Q: Бот не добавляет в папку
**A:** 
1. Проверь, что email это именно @gmail.com
2. Убедись что сервис-аккаунт имеет доступ к папке
3. Проверь GOOGLE_FOLDER_ID (правильный ли?)
4. Активирована ли Google Drive API? (в Console → APIs)

### Q: Где взять GOOGLE_FOLDER_ID?
**A:**
1. Открой папку в Google Drive
2. Посмотри на URL: `https://drive.google.com/drive/folders/[ID_ПАПКИ]`
3. Скопируй ID_ПАПКИ
4. Вставь в конфиг

### Q: Как создать Service Account?
**A:**
1. [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → Service Accounts
3. Create Service Account
4. На странице аккаунта → Keys → Add Key → JSON
5. Загрузится файл - сохрани как `service_account.json`

### Q: Работает ли с @yandex.ru или @mail.ru?
**A:** **Нет!** Только @gmail.com. Если нужно другое - измени regex в коде:

```python
# Было:
if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):

# Стало (для любого email):
if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):

# Или для Google/Яндекс:
if not email.endswith(('@gmail.com', '@yandex.ru')):
```

### Q: Папка конфиденциальная - как защитить доступ?
**A:** Не давай боту права "editor", используй "reader":
```python
permission = {
    'type': 'user',
    'role': 'reader',  # Только чтение
    'emailAddress': user_email
}
```

---

## 💳 Платежи

### Q: Как интегрировать Stripe/PayPal?
**A:** Это большая тема. Основная идея:
1. Создай аккаунт на Stripe/PayPal
2. Интегрируй их API
3. Вместо показа реквизитов - покажи ссылку на оплату
4. Используй вебхуки для автоматического подтверждения

Пример с Stripe:
```python
import stripe

stripe.api_key = "sk_live_..."

# При покупке:
intent = stripe.PaymentIntent.create(
    amount=Config.PRODUCT_PRICE * 100,  # в копейках
    currency="rub",
    payment_method_types=["card"],
)

# Отправить ссылку для оплаты пользователю
```

### Q: Как добавить скидку/промокод?
**A:**
```python
PROMO_CODES = {
    "NEWUSER": 0.1,  # 10% скидка
    "FRIEND": 0.2,   # 20% скидка
}

# В боте:
if promo_code in PROMO_CODES:
    discount = Config.PRODUCT_PRICE * PROMO_CODES[promo_code]
    final_price = Config.PRODUCT_PRICE - discount
```

### Q: Что если клиент скажет что оплатил, но денег нет?
**A:** 
1. Проверь реквизиты (Яндекс.Касса, банк)
2. Посмотри логи в БД
3. Можешь добавить проверку платежей вручную:
```python
@admin_only
async def verify_payment(user_id):
    # Проверить платеж
    db.update_payment_status(user_id, 'completed')
```

---

## 🗄️ База данных

### Q: Как посмотреть, кто покупал?
**A:** Используй admin_panel.py:
```bash
python admin_panel.py
```
Выбери опцию "2" (Все покупки)

### Q: Как экспортировать данные?
**A:** В admin_panel.py → опция "4" (Экспорт CSV)

### Q: Я удалил БД, можно ли восстановить?
**A:** **Нет!** Но бот создаст новую. Рекомендуемо делать резервные копии:
```bash
# Каждый день копировать
cp sales_bot.db sales_bot_backup_$(date +%Y%m%d).db
```

### Q: Как перенести БД на другой сервер?
**A:** Просто скопируй файл sales_bot.db:
```bash
scp sales_bot.db user@server:/path/to/bot/
```

---

## 🔒 Безопасность

### Q: Безопасно ли хранить токены в main.py?
**A:** **Нет!** Всегда используй .env файл:
```python
from os import getenv
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
```

### Q: Кто-то украл мой токен, что делать?
**A:**
1. Сразу напиши @BotFather
2. Команда `/mybots`
3. Выбери бота → Edit → Replace API token
4. Получишь новый токен
5. Обнови в конфиге

### Q: Нужна ли двухфакторная аутентификация?
**A:** Для админ-панели - да. Пример:
```python
ADMIN_PASSWORD = "super_secret_password"

def verify_admin(password):
    return password == ADMIN_PASSWORD
```

### Q: Как защитить файлы в Google папке?
**A:**
1. Не делайся папку публичной
2. Добавляй доступ только через Service Account
3. Используй "reader" вместо "editor"
4. Периодически проверяй доступ

---

## 🐛 Ошибки и решения

### Q: `ModuleNotFoundError: No module named 'telegram'`
**A:**
```bash
pip install python-telegram-bot==20.5
```

### Q: `google.auth.exceptions.DefaultCredentialsError`
**A:**
1. Проверь путь к `service_account.json`
2. Убедись файл существует
3. Проверь расширение (должен быть .json)

### Q: `Invalid Sharing Request`
**A:**
- Email уже имеет доступ
- Email не существует
- Папка настроена неправильно

### Q: Бот работает, но не добавляет в папку
**A:**
- Проверь логи: `INFO` или `ERROR`?
- Тестовый email: попробуй свой
- Проверь Google Drive API (активирована?)

### Q: `rate_limit_exceeded`
**A:** Бот отправляет слишком много запросов. Добавь задержку:
```python
import time
time.sleep(0.5)  # Жди 0.5 сек между запросами
```

---

## 💰 Доход и аналитика

### Q: Как считать доход?
**A:** Используй admin_panel.py → опция "1":
```
💰 Общий доход: 14 950 руб.
```

Или вручную в Python:
```python
cursor.execute("SELECT SUM(price) FROM purchases WHERE status = 'completed'")
total = cursor.fetchone()[0]
```

### Q: Как отследить, отку идут покупки?
**A:** Добавь в БД информацию о источнике:
```python
cursor.execute('''
    ALTER TABLE purchases ADD COLUMN source TEXT
''')

# При покупке:
db.add_purchase(user_id, product, price, method, source="telegram")
```

### Q: Можно ли продавать несколько продуктов?
**A:** Да! См. сценарий 6 в CONFIG_EXAMPLES.md

---

## 🚀 Развитие

### Q: Как добавить рефералов?
**A:**
```python
REFERRAL_BONUS = 0.1  # 10% от цены

# Структура:
# Юзер A пригласил Юзера B
# Юзер B покупает → Юзер A получает бонус
```

### Q: Как добавить подписку вместо одноразовой покупки?
**A:**
```python
# Добавить в БД:
subscription_end_date

# Проверить ежедневно:
if subscription_end_date < today:
    # Закрыть доступ
    pass
```

### Q: Как интегрировать с WhatsApp?
**A:** Используй Twilio или aiowhatsapp, но это уже другой уровень сложности.

---

## 📞 Получить помощь

Если все еще не работает:

1. **Проверь логи** - они часто содержат подсказку
2. **Прочитай документацию:**
   - [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
   - [Google Drive API docs](https://developers.google.com/drive)
3. **Попробуй поиск в Google** с текстом ошибки
4. **Сделай минимальный пример** и проверь его отдельно
5. **Создай issue** на GitHub (если это чей-то проект)

---

**Удачи! 🚀**
