# 🚀 БЫСТРЫЙ СТАРТ (за 10 минут)

## Шаг 1: Получи токен Telegram бота (2 мин)

1. Открой Telegram → напиши боту [@BotFather](https://t.me/botfather)
2. Команда: `/newbot`
3. Выбери имя: например `My Sales Bot`
4. Выбери юзернейм: например `my_sales_bot` (должен заканчиваться на _bot)
5. **Скопируй токен!** Выглядит так: `123456:ABC-DEF1234ghIkl...`

## Шаг 2: Подготовь Google Drive (5 мин)

### 2.1 Создай папку
- Открой [Google Drive](https://drive.google.com)
- Создай новую папку
- Посмотри URL: `https://drive.google.com/drive/folders/[ID_ПАПКИ]`
- **Скопируй ID_ПАПКИ**

### 2.2 Создай Service Account
1. Открой [Google Cloud Console](https://console.cloud.google.com)
2. Создай новый проект (если нужно)
3. В меню слева: APIs & Services → Service Accounts
4. Нажми "Create Service Account"
5. Заполни данные, нажми Create
6. На странице аккаунта → вкладка "Keys" → "Add Key" → "Create new key"
7. Выбери JSON → **загрузишься файл**
8. Сохрани как `service_account.json` в папку бота

### 2.3 Дай доступ папке
1. Открой папку в Google Drive
2. Нажми "Share"
3. Напиши email из `service_account.json` (поле `client_email`)
   - Выглядит: `bot@project-name.iam.gserviceaccount.com`
4. Дай права "Editor"
5. Нажми Share

### 2.4 Активируй Google Drive API
1. [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services → Library
3. Ищи "Google Drive API" → нажми "Enable"

## Шаг 3: Установи зависимости (1 мин)

```bash
pip install -r requirements.txt
```

Или вручную:
```bash
pip install python-telegram-bot==20.5 google-auth-oauthlib google-api-python-client
```

## Шаг 4: Заполни конфиг (1 мин)

Открой `main.py` и найди класс `Config`:

```python
class Config:
    # Сюда вставь свои данные
    TELEGRAM_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"  # Из @BotFather
    GOOGLE_FOLDER_ID = "1A2B3C4D5E6F7G8H9I0J"  # Из Google Drive URL
    GOOGLE_SERVICE_ACCOUNT_JSON = "service_account.json"  # Файл который ты сохранил
    
    # Твой продукт
    PRODUCT_PRICE = 499  # Цена в рублях
    PRODUCT_NAME = "Мой Курс"
    
    # Твои реквизиты для платежа
    PAYMENT_DETAILS = {
        "method": "Яндекс.Касса",  # Или другой способ
        "account": "410013XXXXXXXX",  # Твой номер счета
        "name": "Иван Петров",  # Твое имя
        "phone": "+79991234567",  # Твой номер
        "description": "Платеж за курс"
    }
```

## Шаг 5: Запусти бота! (1 мин)

```bash
python main.py
```

Если видишь:
```
🤖 Бот запущен!
```

✅ **Готово!**

## Тестирование

1. Открой Telegram
2. Найди своего бота по юзернейму (который ты выбрал на шаге 1)
3. Команда: `/start`
4. Нажми "💳 Купить продукт"
5. Введи свой Gmail (должен быть @gmail.com)
6. Посмотри реквизиты
7. Нажми "✅ Я оплатил(а)"
8. Проверь что ты добавлен в Google папку!

## Что будет работать:

✅ Показ реквизитов для платежа  
✅ Проверка Gmail  
✅ Добавление в Google папку  
✅ Логирование покупок в БД  
✅ Admin панель для просмотра статистики  

## Дополнительно (опционально)

### Посмотри статистику:
```bash
python admin_panel.py
```

### Экспортируй данные в Excel:
В админ-панели → опция 4

### Использовать .env для безопасности:
1. Скопируй `.env.example` → `.env`
2. Заполни свои данные
3. В `main.py` используй `getenv()`

## 🆘 Если не работает

### Бот не запускается
- Проверь токен правильный ли?
- Установлены ли зависимости? (`pip list | grep telegram`)
- Интернет подключен?

### Не добавляет в папку
- Проверь что email это @gmail.com
- Сервис-аккаунт имеет доступ к папке? (Share с вкладкой)
- Google Drive API активирована? (Console → APIs)

### Другие ошибки
Читай [FAQ.md](./FAQ.md) - там ответы на 90% проблем

---

**Уже готово! 🎉 Можешь начинать зарабатывать!**

## Следующие шаги

- 📖 Прочитай SETUP.md для более подробной информации
- 🔧 Посмотри CONFIG_EXAMPLES.md для разных вариантов конфига
- ❓ Если вопросы - смотри FAQ.md
- 📊 Используй admin_panel.py для аналитики

---

**Успехов в продажах! 💰**
