# 🔧 Примеры конфигураций для разных сценариев

## Сценарий 1: Продажа PDF-файла курса

```python
class Config:
    TELEGRAM_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    GOOGLE_FOLDER_ID = "1A2B3C4D5E6F7G8H9I0J"
    
    PRODUCT_NAME = "📚 Полный курс по Python"
    PRODUCT_PRICE = 1990  # 1990 рублей
    PRODUCT_FILE_PATH = "/files/python_course.pdf"
    
    PAYMENT_DETAILS = {
        "method": "Яндекс.Касса",
        "account": "410013123456789",
        "name": "Иван Петров",
        "phone": "+7 999 123-45-67",
        "description": "Платеж за курс Python"
    }
```

## Сценарий 2: Продажа онлайн-доступа

```python
class Config:
    TELEGRAM_TOKEN = "YOUR_TOKEN"
    GOOGLE_FOLDER_ID = "YOUR_FOLDER_ID"
    
    PRODUCT_NAME = "🎓 Доступ на 30 дней к материалам"
    PRODUCT_PRICE = 3990
    
    PAYMENT_DETAILS = {
        "method": "Яндекс.Касса",
        "account": "410013XXXXXXXX",
        "name": "Имя Фамилия",
        "phone": "+79XXXXXXXXXX",
        "description": "Подписка на 30 дней"
    }
```

## Сценарий 3: Продажа через Bitcoin (крипто)

```python
class Config:
    TELEGRAM_TOKEN = "YOUR_TOKEN"
    GOOGLE_FOLDER_ID = "YOUR_FOLDER_ID"
    
    PRODUCT_NAME = "💎 Премиум пакет"
    PRODUCT_PRICE = 5000
    
    # Цена в USDT (примерно)
    PRODUCT_PRICE_CRYPTO = 0.05  # примерно
    
    PAYMENT_DETAILS = {
        "method": "Bitcoin",
        "address": "1A1z7agoat2EV6sPZKSarqmBtQavJfR",
        "network": "Bitcoin Mainnet",
        "description": "Отправь ровно 0.0005 BTC на этот адрес"
    }
```

## Сценарий 4: Продажа через Ethereum

```python
class Config:
    TELEGRAM_TOKEN = "YOUR_TOKEN"
    GOOGLE_FOLDER_ID = "YOUR_FOLDER_ID"
    
    PRODUCT_NAME = "💎 VIP Доступ"
    PRODUCT_PRICE = 2500
    
    PAYMENT_DETAILS = {
        "method": "Ethereum",
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f2e",
        "network": "Ethereum Mainnet",
        "token": "ETH",
        "amount": "0.001",
        "description": "Отправь 0.001 ETH на этот адрес"
    }
```

## Сценарий 5: Несколько вариантов платежа

```python
PAYMENT_METHODS = {
    "yandex": {
        "method": "Яндекс.Касса",
        "account": "410013XXXXXXXX",
        "name": "Твое Имя",
        "phone": "+79XXXXXXXXXX",
    },
    "bitcoin": {
        "method": "Bitcoin",
        "address": "1A1z7agoat2EV6sPZKSarqmBtQavJfR",
    },
    "paypal": {
        "method": "PayPal",
        "email": "your-paypal@email.com",
    }
}

class Config:
    PAYMENT_DETAILS = PAYMENT_METHODS["yandex"]  # Выбрать один по умолчанию
```

## Сценарий 6: Разные цены и продукты

```python
PRODUCTS = {
    "basic": {
        "name": "📦 Базовый пакет",
        "price": 499,
        "folder_id": "FOLDER_ID_BASIC"
    },
    "pro": {
        "name": "⭐ Профессиональный",
        "price": 1990,
        "folder_id": "FOLDER_ID_PRO"
    },
    "premium": {
        "name": "💎 Премиум",
        "price": 4990,
        "folder_id": "FOLDER_ID_PREMIUM"
    }
}

class Config:
    DEFAULT_PRODUCT = "pro"
```

## Сценарий 7: Использование .env файла (безопасно)

**main.py:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Загружает из .env файла

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    GOOGLE_FOLDER_ID = os.getenv("GOOGLE_FOLDER_ID")
    PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Мой продукт")
    PRODUCT_PRICE = int(os.getenv("PRODUCT_PRICE", "499"))
    
    PAYMENT_DETAILS = {
        "method": os.getenv("PAYMENT_METHOD", "Яндекс.Касса"),
        "account": os.getenv("PAYMENT_ACCOUNT"),
        "name": os.getenv("PAYMENT_NAME"),
        "phone": os.getenv("PAYMENT_PHONE"),
    }
```

**.env:**
```
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
GOOGLE_FOLDER_ID=1A2B3C4D5E6F
PRODUCT_NAME=Мой Продукт
PRODUCT_PRICE=499
PAYMENT_METHOD=Яндекс.Касса
PAYMENT_ACCOUNT=410013XXXXXXXX
PAYMENT_NAME=Иван Петров
PAYMENT_PHONE=+79991234567
```

## Сценарий 8: Интеграция с Stripe (платежная система)

```python
import stripe

class Config:
    STRIPE_API_KEY = "sk_live_XXXXXXXXXXXXXXXX"
    STRIPE_PUBLISHABLE_KEY = "pk_live_XXXXXXXXXXXXXXXX"
    PRODUCT_PRICE = 499  # в копейках (4.99$)
    
    # Настройка Stripe
    stripe.api_key = STRIPE_API_KEY
```

## Сценарий 9: Использование переменных окружения с валидацией

```python
import os
from typing import Dict, Any

class Config:
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Загрузить и валидировать конфиг"""
        token = os.getenv("TELEGRAM_TOKEN")
        folder_id = os.getenv("GOOGLE_FOLDER_ID")
        
        if not token:
            raise ValueError("❌ TELEGRAM_TOKEN не установлен")
        if not folder_id:
            raise ValueError("❌ GOOGLE_FOLDER_ID не установлен")
        
        return {
            "token": token,
            "folder_id": folder_id,
            "price": int(os.getenv("PRODUCT_PRICE", "499")),
            "name": os.getenv("PRODUCT_NAME", "Продукт"),
        }

# Использование:
# config = Config.load_config()
```

## Сценарий 10: Локализация (разные языки)

```python
LOCALES = {
    "ru": {
        "start_message": "Привет! Добро пожаловать в магазин!",
        "buy_button": "💳 Купить продукт",
        "price": "Цена: {price} руб.",
        "enter_email": "Введи свой Gmail:",
        "confirm_email": "Твой email: {email}. Это верно?",
        "payment_received": "✅ Платеж получен!",
    },
    "en": {
        "start_message": "Hello! Welcome to the store!",
        "buy_button": "💳 Buy Product",
        "price": "Price: ${price}",
        "enter_email": "Enter your Gmail:",
        "confirm_email": "Your email: {email}. Is this correct?",
        "payment_received": "✅ Payment received!",
    }
}

class Config:
    LANGUAGE = "ru"
    TRANSLATION = LOCALES[LANGUAGE]
```

## Быстрый старт для разных случаев

### Для начинающих (простая конфиг):
```python
class Config:
    TELEGRAM_TOKEN = "твой_токен"
    GOOGLE_FOLDER_ID = "твой_folder_id"
    PRODUCT_PRICE = 499
    PRODUCT_NAME = "Мой продукт"
    
    PAYMENT_DETAILS = {
        "method": "Яндекс.Касса",
        "account": "410013XXXXXXXX",
        "name": "Твое имя",
        "phone": "+79XXXXXXXXXX",
    }
```

### Для опытных (с безопасностью):
Используй вариант со сценария 7 (.env файл)

### Для команд (с разными продуктами):
Используй вариант со сценария 6 (PRODUCTS dict)

---

## 💡 Советы

- ✅ **Секреты хранить в .env**, не в коде
- ✅ **Тестировать с минимальной ценой** перед запуском
- ✅ **Проверить все реквизиты** перед отправкой ботов клиентам
- ✅ **Делать резервные копии БД** (sales_bot.db)
- ✅ **Мониторить логи** для отладки проблем
