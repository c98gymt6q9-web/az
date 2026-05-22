# 🤖 Telegram Sales Bot - Инструкция по установке

## 📋 Требования
- Python 3.9+
- Telegram Bot Token
- Google Service Account (для Google Drive)
- Google Folder ID

## 🚀 Установка

### 1. Установи зависимости
```bash
pip install -r requirements.txt
```

### 2. Создай Telegram бота

1. Напиши боту [@BotFather](https://t.me/botfather) в Telegram
2. Команда: `/newbot`
3. Выбери имя бота (например, "My Sales Bot")
4. Выбери юзернейм (например, "my_sales_bot")
5. Получи **TELEGRAM_TOKEN** - скопируй его

### 3. Подготовь Google Drive

#### 3.1 Создай папку в Google Drive
- Создай новую папку в Google Drive
- Скопируй ID папки из URL:
  ```
  https://drive.google.com/drive/folders/[ID_ПАПКИ]
  ```
- Это будет твой **GOOGLE_FOLDER_ID**

#### 3.2 Создай Service Account
1. Перейди в [Google Cloud Console](https://console.cloud.google.com/)
2. Создай новый проект или выбери существующий
3. Перейди в "APIs & Services" → "Service Accounts"
4. Нажми "Create Service Account"
5. Заполни детали, нажми "Create"
6. На странице сервис-аккаунта:
   - Перейди на вкладку "Keys"
   - "Add Key" → "Create new key"
   - Выбери "JSON"
   - Загрузишься файл `service_account.json`
7. Сохрани этот файл в папку проекта

#### 3.3 Активируй Google Drive API
1. В Google Cloud Console перейди в "APIs & Services" → "Library"
2. Поищи "Google Drive API"
3. Нажми "Enable"

#### 3.4 Дай доступ папке Service Account
1. Открой папку в Google Drive
2. Нажми "Share"
3. В "Share with people and groups" введи email сервис-аккаунта:
   - Найди email в файле `service_account.json`, поле `client_email`
   - Выглядит так: `bot@project-id.iam.gserviceaccount.com`
4. Дай права "Editor"
5. Нажми "Share"

### 4. Настрой конфиг

Открой `main.py` и заполни:

```python
class Config:
    TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"  # Токен от @BotFather
    GOOGLE_FOLDER_ID = "YOUR_FOLDER_ID"  # ID папки Google Drive
    
    # Твой продукт
    PRODUCT_PRICE = 499
    PRODUCT_NAME = "Название твоего продукта"
    
    # Реквизиты для платежа (вариант 1 - Яндекс.Касса)
    PAYMENT_DETAILS = {
        "method": "Яндекс.Касса",
        "account": "410013XXXXXXXX",
        "name": "Твое имя",
        "phone": "+79XXXXXXXXXX",
    }
    
    # Или вариант 2 - Bitcoin/Крипто
    # PAYMENT_DETAILS = {
    #     "method": "Bitcoin",
    #     "address": "1A1z7agoat...",
    # }
```

## ▶️ Запуск

```bash
python main.py
```

Если все правильно - увидишь:
```
🤖 Бот запущен!
```

## 🎯 Как это работает

### Поток покупки:
1. Пользователь нажимает "💳 Купить продукт"
2. Вводит свой **Gmail** адрес
3. Видит **реквизиты платежа** (твой счет, номер и т.д.)
4. Нажимает "✅ Я оплатил(а)"
5. Бот **проверяет email** (должен быть @gmail.com)
6. Бот **добавляет юзера в Google папку** автоматически
7. Юзер получает доступ к файлам в папке

### База данных:
- Создается `sales_bot.db` (SQLite)
- Хранит:
  - ✅ Все покупки
  - ✅ Email клиентов
  - ✅ Статусы платежей
  - ✅ Даты транзакций

## 🔒 Безопасность

⚠️ **ВАЖНО:**
- Никогда не коммитьте в GitHub:
  - `service_account.json`
  - TELEGRAM_TOKEN
  - Реквизиты платежей
- Используй `.env` файл для чувствительных данных (опционально)

### Рекомендуемо:
```python
# Использовать переменные окружения
from os import getenv

TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
GOOGLE_SERVICE_ACCOUNT_JSON = getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
```

## 🐛 Дебаг

Если что-то не работает:

1. **Бот не запускается:**
   - Проверь `TELEGRAM_TOKEN`
   - Убедись, что интернет включен

2. **Не добавляет в Google папку:**
   - Проверь, что сервис-аккаунт имеет доступ к папке
   - Проверь `GOOGLE_FOLDER_ID`
   - Убедись что Google Drive API активирован

3. **Требует другую почту:**
   - Проверь регулярное выражение в `get_email()`
   - Убедись, что это именно @gmail.com

## 📊 Примеры использования

### Разные способы платежа:

**Яндекс.Касса:**
```python
PAYMENT_DETAILS = {
    "method": "Яндекс.Касса",
    "account": "410013123456789",
    "name": "Иван Иванов",
    "phone": "+79991234567",
}
```

**Bitcoin:**
```python
PAYMENT_DETAILS = {
    "method": "Bitcoin",
    "address": "1A1z7agoat2EV6sPZKSarqmBtQavJfR",
}
```

**Криптовалюта (Ethereum):**
```python
PAYMENT_DETAILS = {
    "method": "Ethereum",
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f2e",
}
```

## 🆘 Поддержка

Если возникают проблемы:
1. Проверь логи (выводятся в консоль)
2. Убедись что все конфиги заполнены
3. Проверь доступы в Google Cloud
4. Перепроверь типы данных (email, folder_id и т.д.)

## 📝 Дальнейшее развитие

Можно добавить:
- [ ] Разные продукты с разными ценами
- [ ] Функция промокодов/скидок
- [ ] Отправка файла прямо в Telegram
- [ ] Интеграция с платежными системами (Stripe, PayPal)
- [ ] Админ-панель для управления продуктами
- [ ] Уведомления о новых платежах
- [ ] Система рефералов

---

**Удачи с продажами!** 🚀💰
