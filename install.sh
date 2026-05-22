#!/bin/bash

# 🚀 Скрипт установки Telegram Sales Bot на VPS

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🤖 Telegram Sales Bot - Установка на VPS     ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Проверка прав
if [[ $EUID -ne 0 ]]; then
   echo "❌ Этот скрипт требует прав администратора"
   echo "Запусти: sudo bash install.sh"
   exit 1
fi

# ========== СИСТЕМА ==========
echo ""
echo "📦 Обновление системы..."
apt update && apt upgrade -y

echo "📦 Установка Python и зависимостей..."
apt install -y python3 python3-pip git wget curl

echo "📦 Установка screen для фонового запуска..."
apt install -y screen

# ========== ПРОВЕРКА ВЕРСИИ ==========
echo ""
echo "✅ Проверка версий:"
python3 --version
pip3 --version

# ========== УСТАНОВКА PYTHON ЗАВИСИМОСТЕЙ ==========
echo ""
echo "📦 Установка Python пакетов..."
pip3 install --upgrade pip
pip3 install python-telegram-bot==20.5
pip3 install google-auth-oauthlib
pip3 install google-api-python-client
pip3 install python-dotenv

# ========== ПОДГОТОВКА ПАПКИ ==========
echo ""
echo "📂 Подготовка папки проекта..."
BOT_DIR="/root/telegram-sales-bot"

if [ ! -d "$BOT_DIR" ]; then
    mkdir -p "$BOT_DIR"
    echo "✅ Папка создана: $BOT_DIR"
else
    echo "✅ Папка уже существует: $BOT_DIR"
fi

cd "$BOT_DIR"

# ========== ПРОВЕРКА ФАЙЛОВ ==========
echo ""
echo "📋 Проверка файлов:"

files=("bot.py" ".env" "requirements.txt")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file найден"
    else
        echo "❌ $file не найден - скопируй его вручную"
    fi
done

if [ ! -f "service_account.json" ]; then
    echo "⚠️  service_account.json не найден"
    echo "   👉 Скопируй файл вручную:"
    echo "   scp service_account.json root@YOUR_IP:/root/telegram-sales-bot/"
fi

# ========== КОНФИГУРАЦИЯ ==========
echo ""
echo "🔧 Конфигурация:"
echo ""
echo "Открой .env файл и заполни:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TELEGRAM_TOKEN=...  (от @BotFather)"
echo "GOOGLE_FOLDER_ID=...(из Google Drive)"
echo "PAYMENT_ACCOUNT=... (твои реквизиты)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ========== SYSTEMD СЕРВИС ==========
echo ""
echo "⚙️  Создание systemd сервиса..."

sudo tee /etc/systemd/system/telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram Sales Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BOT_DIR
ExecStart=/usr/bin/python3 $BOT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Сервис создан"

# Активация
systemctl daemon-reload
systemctl enable telegram-bot
echo "✅ Сервис добавлен в автозагрузку"

# ========== ИТОГИ ==========
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ УСТАНОВКА ЗАВЕРШЕНА                   ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1️⃣  Скопируй service_account.json:"
echo "   На локальном ПК:"
echo "   scp service_account.json root@YOUR_IP:$BOT_DIR/"
echo ""
echo "2️⃣  Отредактируй .env файл:"
echo "   nano $BOT_DIR/.env"
echo ""
echo "   Заполни:"
echo "   - TELEGRAM_TOKEN"
echo "   - GOOGLE_FOLDER_ID"
echo "   - PAYMENT_ACCOUNT и др."
echo ""
echo "3️⃣  Запусти бота:"
echo "   systemctl start telegram-bot"
echo ""
echo "4️⃣  Проверь статус:"
echo "   systemctl status telegram-bot"
echo ""
echo "5️⃣  Смотри логи:"
echo "   journalctl -u telegram-bot -f"
echo ""
echo "📞 Тестирование:"
echo "   Напиши боту: /start"
echo ""
echo "📊 Admin панель:"
echo "   Создай admin_panel.py для просмотра статистики"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "❓ Проблемы? Читай FAQ.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
