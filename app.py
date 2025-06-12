from flask import Flask, render_template, request, jsonify
import json
import os
from game_logic import GameLogic
from ai_player import AIPlayer
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Глобальное состояние игры
game_state = {
    'game': None,
    'ai': None,
    'user_symbol': 'X',
    'ai_symbol': 'O'
}

def init_game():
    """Инициализация новой игры"""
    global game_state
    game_state['game'] = GameLogic()
    game_state['ai'] = AIPlayer(game_state['ai_symbol'])
    logger.info("🎮 Новая игра инициализирована")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    try:
        data = request.get_json()
        user_choice = data.get('symbol', 'X')
        
        game_state['user_symbol'] = user_choice
        game_state['ai_symbol'] = 'O' if user_choice == 'X' else 'X'
        
        init_game()
        
        response = {
            'success': True,
            'board': game_state['game'].board,
            'current_player': game_state['game'].current_player,
            'user_symbol': game_state['user_symbol'],
            'ai_symbol': game_state['ai_symbol'],
            'move_count': game_state['game'].move_count
        }
        
        logger.info(f"✅ Новая игра: пользователь={user_choice}, ИИ={game_state['ai_symbol']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания игры: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/make_move', methods=['POST'])
def make_move():
    try:
        if not game_state['game']:
            return jsonify({'success': False, 'error': 'Игра не инициализирована'})
        
        data = request.get_json()
        row = data.get('row')
        col = data.get('col')
        
        if row is None or col is None:
            return jsonify({'success': False, 'error': 'Неверные координаты'})
        
        # Проверяем, что ход игрока
        if game_state['game'].current_player != game_state['user_symbol']:
            return jsonify({'success': False, 'error': 'Сейчас не ваш ход'})
        
        # Делаем ход игрока
        success = game_state['game'].make_move(row, col, game_state['user_symbol'])
        if not success:
            return jsonify({'success': False, 'error': 'Неверный ход'})
        
        # Проверяем победу игрока
        if game_state['game'].check_winner():
            return jsonify({
                'success': True,
                'board': game_state['game'].board,
                'winner': game_state['user_symbol'],
                'game_over': True,
                'move_count': game_state['game'].move_count
            })
        
        # Проверяем ничью
        if game_state['game'].is_board_full():
            return jsonify({
                'success': True,
                'board': game_state['game'].board,
                'winner': None,
                'game_over': True,
                'move_count': game_state['game'].move_count
            })
        
        # Ход ИИ
        ai_move = game_state['ai'].get_move(game_state['game'])
        if ai_move:
            ai_row, ai_col = ai_move
            game_state['game'].make_move(ai_row, ai_col, game_state['ai_symbol'])
            
            # Проверяем победу ИИ
            if game_state['game'].check_winner():
                return jsonify({
                    'success': True,
                    'board': game_state['game'].board,
                    'winner': game_state['ai_symbol'],
                    'game_over': True,
                    'ai_move': [ai_row, ai_col],
                    'move_count': game_state['game'].move_count
                })
        
        return jsonify({
            'success': True,
            'board': game_state['game'].board,
            'current_player': game_state['game'].current_player,
            'ai_move': ai_move,
            'move_count': game_state['game'].move_count
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка хода: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    """Запросить ход ИИ"""
    try:
        if not game_state['game'] or not game_state['ai']:
            return jsonify({'success': False, 'error': 'Игра не инициализирована'})
        
        if game_state['game'].game_over:
            return jsonify({'success': False, 'error': 'Игра уже окончена'})
        
        # Проверяем, что сейчас ход ИИ
        if game_state['game'].current_player != game_state['ai_symbol']:
            return jsonify({'success': False, 'error': 'Сейчас не ход ИИ'})
        
        # Получаем ход ИИ
        ai_move = game_state['ai'].get_move(game_state['game'])
        
        if not ai_move:
            return jsonify({'success': False, 'error': 'ИИ не может сделать ход'})
        
        # Делаем ход
        row, col = ai_move
        success = game_state['game'].make_move(row, col, game_state['ai_symbol'])
        
        if not success:
            return jsonify({'success': False, 'error': 'Невозможно сделать ход ИИ'})
        
        logger.info(f"✅ Ход {game_state['ai_symbol']} на ({row}, {col}), счетчик: {game_state['game'].move_count}")
        
        # Проверяем победу
        if game_state['game'].check_winner():
            logger.info(f"🏆 Победа игрока {game_state['ai_symbol']}!")
            return jsonify({
                'success': True,
                'board': game_state['game'].board,
                'current_player': game_state['game'].current_player,
                'move_count': game_state['game'].move_count,
                'ai_move': [row, col],
                'game_over': True,
                'winner': game_state['ai_symbol']
            })
        
        # Проверяем ничью
        if game_state['game'].is_board_full():
            return jsonify({
                'success': True,
                'board': game_state['game'].board,
                'current_player': game_state['game'].current_player,
                'move_count': game_state['game'].move_count,
                'ai_move': [row, col],
                'game_over': True,
                'winner': None
            })
        
        return jsonify({
            'success': True,
            'board': game_state['game'].board,
            'current_player': game_state['game'].current_player,
            'move_count': game_state['game'].move_count,
            'ai_move': [row, col],
            'game_over': False,
            'winner': None
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка хода ИИ: {e}")
        return jsonify({'success': False, 'error': f'Ошибка ИИ: {str(e)}'})

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    try:
        if not game_state['game']:
            return jsonify({'success': False, 'error': 'Игра не инициализирована'})
        
        return jsonify({
            'success': True,
            'board': game_state['game'].board,
            'current_player': game_state['game'].current_player,
            'user_symbol': game_state['user_symbol'],
            'ai_symbol': game_state['ai_symbol'],
            'move_count': game_state['game'].move_count
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    init_game()
    # Запуск БЕЗ debug режима для избежания проблем с watchdog
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True) 