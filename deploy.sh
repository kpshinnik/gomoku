#!/bin/bash

# Скрипт деплоя игры Гомоку на сервер
SERVER="root@165.232.157.203"
APP_DIR="/var/www/gomoku"

echo "🚀 Начинаем деплой игры Гомоку..."

# 1. Создаем архив с проектом
echo "📦 Создаем архив проекта..."
tar -czf gomoku.tar.gz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' .

# 2. Копируем архив на сервер
echo "📤 Копируем файлы на сервер..."
scp gomoku.tar.gz $SERVER:/tmp/

# 3. Подключаемся к серверу и разворачиваем приложение
echo "🔧 Обновляем приложение на сервере..."
ssh $SERVER << 'EOF'
    # Останавливаем сервис если он запущен
    systemctl stop gomoku 2>/dev/null || true
    
    # Переходим в директорию приложения
    cd /var/www/gomoku
    
    # Создаем бэкап текущей версии
    if [ -f "app.py" ]; then
        echo "📦 Создаем бэкап текущей версии..."
        cp -r . ../gomoku_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    fi
    
    # Распаковываем новую версию
    echo "📦 Распаковываем новую версию..."
    tar -xzf /tmp/gomoku.tar.gz
    rm /tmp/gomoku.tar.gz
    
    # Активируем виртуальное окружение и обновляем зависимости
    echo "📚 Обновляем зависимости..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Настраиваем права доступа
    chown -R www-data:www-data /var/www/gomoku
    
    # Перезапускаем сервисы
    echo "🔄 Перезапускаем сервисы..."
    systemctl daemon-reload
    systemctl start gomoku
    systemctl restart nginx
    
    # Проверяем статус
    echo "🔍 Проверяем статус сервисов..."
    if systemctl is-active --quiet gomoku; then
        echo "✅ Сервис gomoku запущен"
    else
        echo "❌ Ошибка запуска сервиса gomoku"
        journalctl -u gomoku --no-pager -n 10
    fi
    
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx запущен"
    else
        echo "❌ Ошибка Nginx"
    fi
    
    echo "✅ Деплой завершен!"
    echo "🌐 Игра доступна по адресу: http://165.232.157.203"
EOF

# Удаляем временный архив
rm gomoku.tar.gz

echo "🎉 Деплой успешно завершен!"
echo "🌐 Ваша игра доступна по адресу: http://165.232.157.203" 