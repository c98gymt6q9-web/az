# 🚀 Развертывание на BotHost за 5 минут

## 📋 Перед началом

Убедись что у тебя есть:
- ✅ Аккаунт на BotHost
- ✅ Куплен VPS (Linux/Ubuntu)
- ✅ IP адрес и пароль доступа
- ✅ Visual Studio Code на ПК
- ✅ Файлы бота (bot.py, .env и т.д.)
- ✅ service_account.json для Google

## 📱 Шаг 1: Подключись к серверу (1 мин)

### Вариант A: Через SSH в терминале

```bash
# На твоем ПК в терминале (Windows PowerShell или Mac/Linux Terminal):
ssh root@YOUR_IP_ADDRESS

# Введи пароль когда попросит
```

### Вариант B: Через VSCode (удобнее)

1. Открой VSCode
2. Установи расширение **Remote - SSH** (найди в Extensions)
3. Нажми иконку "><" внизу слева
4. Выбери "Connect to Host"
5. Введи: `root@YOUR_IP_ADDRESS`
6. Выбери платформу: Linux
7. Вводишь пароль
8. **Готово!** Теперь видишь файлы сервера слева

## 📥 Шаг 2: Загрузи файлы (1 мин)

### Вариант A: Через SCP (если не используешь VSCode Remote)

На ПК в терминале:
```bash
# Перейди в папку с ботом
cd /path/to/telegram-sales-bot

# Скопируй все файлы
scp -r ./* root@YOUR_IP:/root/telegram-sales-bot/

# Скопируй service_account.json
scp service_account.json root@YOUR_IP:/root/telegram-sales-bot/
```

### Вариант B: Через VSCode Remote (проще)

1. В VSCode подключен к серверу (см. выше)
2. Слева в File Explorer нажми на папку
3. Перетащи файлы из ПК в VSCode
4. Файлы загружаются автоматически!

## ⚙️ Шаг 3: Быстрая установка (2 мин)

В терминале сервера (SSH или VSCode Terminal):

```bash
# Перейди в папку проекта
cd /root/telegram-sales-bot

# Сделай скрипты исполняемыми
chmod +x install.sh deploy.sh

# ВАРИАНТ 1: Быстрая установка (рекомендуемо)
sudo bash deploy.sh

# ВАРИАНТ 2: Подробная установка
sudo bash install.sh
```

Скрипт автоматически:
- ✅ Обновит систему
- ✅ Установит Python и зависимости
- ✅ Создаст systemd сервис
- ✅ Запустит бота

## 🔧 Шаг 4: Заполни конфиг (1 мин)

В терминале сервера:

```bash
nano /root/telegram-sales-bot/.env
```

Заполни значения:
```
TELEGRAM_TOKEN=123456:ABC-DEF1234...
GOOGLE_FOLDER_ID=1A2B3C4D5E6F...
GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
PRODUCT_NAME=Мой продукт
PRODUCT_PRICE=499
PAYMENT_METHOD=Яндекс.Касса
PAYMENT_ACCOUNT=410013XXXXXXXX
PAYMENT_NAME=Твое имя
PAYMENT_PHONE=+79991234567
```

Сохрани: **CTRL+X** → **Y** → **Enter**

## 🚀 Шаг 5: Запусти бота! (0 мин)

```bash
# Стартуй сервис
sudo systemctl start telegram-bot

# Проверь что работает
sudo systemctl status telegram-bot

# Должно быть: "active (running)" ✅
```

## 📊 Проверка работает ли

1. Открой Telegram
2. Найди своего бота по юзернейму
3. Команда: `/start`
4. Нажми "💳 Купить"
5. Введи Gmail
6. Посмотри реквизиты платежа
7. Всё работает! ✅

## 📜 Полезные команды

```bash
# Посмотреть логи (последние 50 строк)
journalctl -u telegram-bot -n 50

# Смотреть логи в реальном времени
journalctl -u telegram-bot -f

# Остановить бота
sudo systemctl stop telegram-bot

# Перезагрузить бота
sudo systemctl restart telegram-bot

# Проверить статус
sudo systemctl status telegram-bot

# Убить процесс (если зависает)
pkill -f "python3 /root/telegram-sales-bot/bot.py"
```

## 🔍 Отладка проблем

### Бот не запускается

```bash
# Проверь логи
journalctl -u telegram-bot -n 100

# Проверь конфиг
cat /root/telegram-sales-bot/.env

# Проверь Python
python3 --version

# Запусти бота вручную для отладки
python3 /root/telegram-sales-bot/bot.py
```

### TELEGRAM_TOKEN неверный

- Пересоздай токен у @BotFather
- Скопируй новый
- Обнови .env
- Перезагрузи: `systemctl restart telegram-bot`

### Google папка недоступна

```bash
# Проверь что service_account.json на месте
ls -la /root/telegram-sales-bot/service_account.json

# Проверь что ты поделился папкой с сервис-аккаунтом
# (в Google Drive Share выбери email из service_account.json)
```

### Бот работает но медленный

```bash
# Проверь интернет на сервере
ping google.com

# Проверь что сервер не перегружен
top

# Нажми 'q' для выхода
```

## 📈 Мониторинг

### Просмотр статистики

```bash
python3 /root/telegram-sales-bot/admin_panel.py
```

Выбери опции:
- 1️⃣ Дашборд - основная статистика
- 2️⃣ Все покупки
- 3️⃣ Ожидающие оплату
- 4️⃣ Экспорт CSV

### Резервная копия БД

```bash
# Скопируй БД на ПК
scp root@YOUR_IP:/root/telegram-sales-bot/sales_bot.db ./backup_$(date +%Y%m%d).db

# Или делай автоматически каждый день (cron)
```

## 🔒 Безопасность

⚠️ **ВАЖНО!**

```bash
# Убедись что .env защищен
chmod 600 /root/telegram-sales-bot/.env

# Убедись что service_account.json защищен
chmod 600 /root/telegram-sales-bot/service_account.json

# Проверь что никто не видит секреты
cat /root/telegram-sales-bot/.env  # ПРИВАТНО!
```

Никогда не загружай в Git:
- `.env` файл
- `service_account.json`
- `sales_bot.db` (база данных)

## 🎯 Итоговый чек-лист

- [ ] VPS куплен и доступен
- [ ] Подключился через SSH/VSCode
- [ ] Загрузил все файлы бота
- [ ] Загрузил service_account.json
- [ ] Заполнил .env (TELEGRAM_TOKEN, GOOGLE_FOLDER_ID и т.д.)
- [ ] Запустил скрипт установки (deploy.sh или install.sh)
- [ ] Запустил бота: `systemctl start telegram-bot`
- [ ] Проверил статус: `systemctl status telegram-bot`
- [ ] Бот отвечает в Telegram на `/start`
- [ ] Покупка срабатывает и добавляет в папку

## ✅ Поздравляем!

У тебя есть работающий 24/7 Telegram-бот! 🎉

**Теперь:**
- 💰 Начинай продавать
- 📊 Смотри статистику в admin_panel
- 🔄 Обновляй конфиг по мере надобности
- 🆘 При проблемах читай логи (journalctl)

---

**Готово! Бот работает на BotHost! 🚀**

Вопросы? Читай FAQ.md
