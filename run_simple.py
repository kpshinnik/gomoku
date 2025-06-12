#!/usr/bin/env python3
"""
Простой запуск игры Гомоку без debug режима
"""

import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        print("🎮 Запуск игры Гомоку...")
        print("📱 Веб-интерфейс будет доступен по адресу: http://127.0.0.1:5001")
        print("🔧 Для остановки нажмите Ctrl+C")
        print("="*50)
        
        # Импортируем и запускаем приложение
        from app import app, init_game
        
        # Инициализация игры
        init_game()
        
        # Запуск без debug режима
        app.run(
            host='127.0.0.1',
            port=5001,
            debug=False,
            threaded=True,
            use_reloader=False  # Отключаем reloader который вызывает проблемы с watchdog
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Игра остановлена пользователем")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь что установлены все зависимости: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 