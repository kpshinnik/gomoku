from flask import Flask, render_template, request, jsonify, session
import json
import os
from game_logic import GameLogic
from ai_player import AIPlayer
import logging
import secrets
import datetime
import glob

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Генерируем случайный секретный ключ для продакшена
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Создаем директорию для логов если её нет
LOGS_DIR = 'game_logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

def get_next_game_index(winner_type):
    """Получить следующий индекс для файла лога"""
    pattern = os.path.join(LOGS_DIR, f"{winner_type}-*.json")
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    # Извлекаем номера из существующих файлов
    indices = []
    for file_path in existing_files:
        filename = os.path.basename(file_path)
        try:
            # Извлекаем номер между префиксом и .json
            index_str = filename.split('-')[1].split('.')[0]
            indices.append(int(index_str))
        except (IndexError, ValueError):
            continue
    
    return max(indices) + 1 if indices else 1

def save_game_log(game, winner, user_symbol, ai_symbol):
    """Сохранить лог игры в файл"""
    try:
        # Определяем тип победителя
        if winner == user_symbol:
            winner_type = "human"
        elif winner == ai_symbol:
            winner_type = "AI"
        else:
            winner_type = "draw"
        
        # Получаем следующий индекс
        game_index = get_next_game_index(winner_type)
        
        # Создаем данные лога
        game_log = {
            'game_id': f"{winner_type}-{game_index}",
            'timestamp': datetime.datetime.now().isoformat(),
            'winner': winner,
            'winner_type': winner_type,
            'user_symbol': user_symbol,
            'ai_symbol': ai_symbol,
            'total_moves': game.move_count,
            'final_board': game.board,
            'game_duration_moves': game.move_count,
            'result': {
                'human_won': winner == user_symbol,
                'ai_won': winner == ai_symbol,
                'draw': winner is None
            }
        }
        
        # Сохраняем в файл
        filename = f"{winner_type}-{game_index}.json"
        filepath = os.path.join(LOGS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(game_log, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📝 Лог игры сохранен: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения лога игры: {e}")
        return None

def init_game():
    """Инициализация новой игры"""
    session['game_board'] = [['.'] * 15 for _ in range(15)]
    session['current_player'] = 'X'
    session['move_count'] = 0
    session['game_over'] = False
    session['winner'] = None
    logger.info("🎮 Новая игра инициализирована")

def get_game_logic():
    """Получить объект GameLogic из сессии"""
    if 'game_board' not in session:
        init_game()
    
    game = GameLogic()
    game.board = session['game_board']
    game.current_player = session['current_player']
    game.move_count = session['move_count']
    game.game_over = session['game_over']
    game.winner = session['winner']
    return game

def save_game_state(game):
    """Сохранить состояние игры в сессию"""
    session['game_board'] = game.board
    session['current_player'] = game.current_player
    session['move_count'] = game.move_count
    session['game_over'] = game.game_over
    session['winner'] = game.winner

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    try:
        data = request.get_json()
        user_choice = data.get('symbol', 'X')
        
        session['user_symbol'] = user_choice
        session['ai_symbol'] = 'O' if user_choice == 'X' else 'X'
        
        init_game()
        game = get_game_logic()
        ai = AIPlayer(session['ai_symbol'])
        
        # Если ИИ играет за X (пользователь выбрал O), ИИ ходит первым
        ai_move = None
        if session['ai_symbol'] == 'X':
            logger.info("🤖 ИИ играет за X, делает первый ход")
            ai_move_result = ai.get_move(game)
            if ai_move_result:
                ai_row, ai_col = ai_move_result
                logger.info(f"🤖 ИИ делает первый ход на ({ai_row}, {ai_col})")
                success = game.make_move(ai_row, ai_col, session['ai_symbol'])
                if success:
                    ai_move = [ai_row, ai_col]
                    save_game_state(game)
                    logger.info(f"✅ Первый ход ИИ {session['ai_symbol']} на ({ai_row}, {ai_col}), счетчик: {game.move_count}")
                else:
                    logger.error(f"❌ ИИ не смог сделать первый ход на ({ai_row}, {ai_col})")
        
        response = {
            'success': True,
            'board': game.board,
            'current_player': game.current_player,
            'user_symbol': session['user_symbol'],
            'ai_symbol': session['ai_symbol'],
            'move_count': game.move_count,
            'ai_move': ai_move
        }
        
        logger.info(f"✅ Новая игра: пользователь={user_choice}, ИИ={session['ai_symbol']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания игры: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/make_move', methods=['POST'])
def make_move():
    try:
        if 'user_symbol' not in session:
            return jsonify({'success': False, 'error': 'Игра не инициализирована'})
        
        data = request.get_json()
        row = data.get('row')
        col = data.get('col')
        
        if row is None or col is None:
            return jsonify({'success': False, 'error': 'Неверные координаты'})
        
        game = get_game_logic()
        
        # Проверяем, что ход игрока
        if game.current_player != session['user_symbol']:
            return jsonify({'success': False, 'error': 'Сейчас не ваш ход'})
        
        # Делаем ход игрока
        success = game.make_move(row, col, session['user_symbol'])
        if not success:
            return jsonify({'success': False, 'error': 'Неверный ход'})
        
        save_game_state(game)
        logger.info(f"✅ Ход игрока {session['user_symbol']} на ({row}, {col}), счетчик: {game.move_count}")
        
        # Проверяем победу игрока
        if game.check_winner():
            # Сохраняем лог игры
            save_game_log(game, session['user_symbol'], session['user_symbol'], session['ai_symbol'])
            return jsonify({
                'success': True,
                'board': game.board,
                'winner': session['user_symbol'],
                'game_over': True,
                'move_count': game.move_count
            })
        
        # Проверяем ничью
        if game.is_board_full():
            # Сохраняем лог игры (ничья)
            save_game_log(game, None, session['user_symbol'], session['ai_symbol'])
            return jsonify({
                'success': True,
                'board': game.board,
                'winner': None,
                'game_over': True,
                'move_count': game.move_count
            })
        
        # Ход ИИ
        ai = AIPlayer(session['ai_symbol'])
        ai_move = ai.get_move(game)
        if ai_move:
            ai_row, ai_col = ai_move
            logger.info(f"🤖 ИИ пытается сделать ход на ({ai_row}, {ai_col})")
            logger.info(f"📊 Состояние клетки [{ai_row}][{ai_col}]: '{game.board[ai_row][ai_col]}'")
            ai_success = game.make_move(ai_row, ai_col, session['ai_symbol'])
            
            if not ai_success:
                logger.error(f"❌ ИИ не смог сделать ход на ({ai_row}, {ai_col})")
                return jsonify({
                    'success': True,
                    'board': game.board,
                    'current_player': game.current_player,
                    'ai_move': None,
                    'move_count': game.move_count,
                    'error': f'ИИ не смог сделать ход на ({ai_row}, {ai_col})'
                })
            
            save_game_state(game)
            
            # Проверяем победу ИИ
            if game.check_winner():
                # Сохраняем лог игры
                save_game_log(game, session['ai_symbol'], session['user_symbol'], session['ai_symbol'])
                return jsonify({
                    'success': True,
                    'board': game.board,
                    'winner': session['ai_symbol'],
                    'game_over': True,
                    'ai_move': [ai_row, ai_col],
                    'move_count': game.move_count
                })
        
        return jsonify({
            'success': True,
            'board': game.board,
            'current_player': game.current_player,
            'ai_move': ai_move,
            'move_count': game.move_count
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка хода: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    """Запросить ход ИИ"""
    try:
        if 'ai_symbol' not in session:
            return jsonify({'success': False, 'error': 'Игра не инициализирована'})
        
        game = get_game_logic()
        
        if game.game_over:
            return jsonify({'success': False, 'error': 'Игра уже окончена'})
        
        # Проверяем, что сейчас ход ИИ
        if game.current_player != session['ai_symbol']:
            return jsonify({'success': False, 'error': 'Сейчас не ход ИИ'})
        
        # Получаем ход ИИ
        ai = AIPlayer(session['ai_symbol'])
        ai_move = ai.get_move(game)
        
        if not ai_move:
            return jsonify({'success': False, 'error': 'ИИ не может сделать ход'})
        
        # Делаем ход
        row, col = ai_move
        success = game.make_move(row, col, session['ai_symbol'])
        
        if not success:
            return jsonify({'success': False, 'error': 'Невозможно сделать ход ИИ'})
        
        save_game_state(game)
        logger.info(f"✅ Ход {session['ai_symbol']} на ({row}, {col}), счетчик: {game.move_count}")
        
        # Проверяем победу
        if game.check_winner():
            logger.info(f"🏆 Победа игрока {session['ai_symbol']}!")
            # Сохраняем лог игры
            save_game_log(game, session['ai_symbol'], session['user_symbol'], session['ai_symbol'])
            return jsonify({
                'success': True,
                'board': game.board,
                'current_player': game.current_player,
                'move_count': game.move_count,
                'winner': session['ai_symbol'],
                'game_over': True
            })
        
        return jsonify({
            'success': True,
            'board': game.board,
            'current_player': game.current_player,
            'move_count': game.move_count
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка хода ИИ: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    """Получить текущее состояние игры"""
    try:
        if 'user_symbol' not in session:
            return jsonify({'success': False, 'error': 'Игра не инициализирована'})
        
        game = get_game_logic()
        
        return jsonify({
            'success': True,
            'board': game.board,
            'current_player': game.current_player,
            'user_symbol': session.get('user_symbol'),
            'ai_symbol': session.get('ai_symbol'),
            'move_count': game.move_count,
            'game_over': game.game_over,
            'winner': game.winner
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/game_stats', methods=['GET'])
def get_game_stats():
    """Получить статистику игр"""
    try:
        # Подсчитываем файлы логов
        ai_wins = len(glob.glob(os.path.join(LOGS_DIR, "AI-*.json")))
        human_wins = len(glob.glob(os.path.join(LOGS_DIR, "human-*.json")))
        draws = len(glob.glob(os.path.join(LOGS_DIR, "draw-*.json")))
        total_games = ai_wins + human_wins + draws
        
        # Вычисляем процентные соотношения
        ai_win_rate = (ai_wins / total_games * 100) if total_games > 0 else 0
        human_win_rate = (human_wins / total_games * 100) if total_games > 0 else 0
        draw_rate = (draws / total_games * 100) if total_games > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_games': total_games,
                'ai_wins': ai_wins,
                'human_wins': human_wins,
                'draws': draws,
                'ai_win_rate': round(ai_win_rate, 1),
                'human_win_rate': round(human_win_rate, 1),
                'draw_rate': round(draw_rate, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 