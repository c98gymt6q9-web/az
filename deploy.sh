#!/bin/bash

# 🚀 Быстрое развертывание бота на BotHost в одну команду

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        🚀 БЫСТРОЕ РАЗВЕРТЫВАНИЕ НА BOTHHOST        ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "Этот скрипт автоматически:"
echo "✅ Обновит систему"
echo "✅ Установит Python и зависимости"
echo "✅ Создаст папку проекта"
echo "✅ Запустит бота через systemd"
echo ""

# Проверка прав
if [[ $EUID -ne 0 ]]; then
   echo "❌ Требуются права администратора!"
   echo "Запусти: sudo bash deploy.sh"
   exit 1
fi

# ========== ПЕРЕМЕННЫЕ ==========
BOT_DIR="/root/telegram-sales-bot"
GIT_REPO="${1:-}"

# ========== УСТАНОВКА ==========
echo "📦 Установка зависимостей системы..."
apt update && apt upgrade -y
apt install -y python3 python3-pip git screen nano

echo "📦 Установка Python пакетов..."
pip3 install --upgrade pip
pip3 install python-telegram-bot==20.5 google-auth-oauthlib google-api-python-client python-dotenv

echo ""
echo "📂 Подготовка папки: $BOT_DIR"
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

# ========== ЗАГРУЗКА КОДА ==========
if [ -n "$GIT_REPO" ]; then
    echo "📥 Клонирование репозитория..."
    git clone "$GIT_REPO" . 2>/dev/null || echo "⚠️  Не удалось клонировать"
else
    echo "⚠️  Git URL не указан"
    echo "   Используй: bash deploy.sh https://github.com/user/repo.git"
fi

# ========== СОЗДАНИЕ СЕРВИСА ==========
echo ""
echo "⚙️  Создание systemd сервиса..."

cat > /etc/systemd/system/telegram-bot.service << 'EOF'
[Unit]
Description=Telegram Sales Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram-sales-bot
ExecStart=/usr/bin/python3 /root/telegram-sales-bot/bot.py
Restart=always
RestartSec=10
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable telegram-bot

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ ГОТОВО К ЗАПУСКУ                       ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "🔧 ЗАПОЛНИ .env:"
echo "   nano $BOT_DIR/.env"
echo ""
echo "   Требуется заполнить:"
echo "   • TELEGRAM_TOKEN (от @BotFather)"
echo "   • GOOGLE_FOLDER_ID (из Google Drive)"
echo "   • PAYMENT_ACCOUNT (твои реквизиты)"
echo ""
echo "📄 ЗАГРУЗИ service_account.json:"
echo "   С ПК: scp service_account.json root@YOUR_IP:$BOT_DIR/"
echo ""
echo "🚀 ЗАПУСТИ БОТ:"
echo "   systemctl start telegram-bot"
echo ""
echo "📊 ПРОВЕРЬ СТАТУС:"
echo "   systemctl status telegram-bot"
echo ""
echo "📜 СМОТРИ ЛОГИ:"
echo "   journalctl -u telegram-bot -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Готово! 🎉 Теперь заполни .env и запусти бота"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
