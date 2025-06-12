import random
import time
import logging
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger(__name__)

class AIPlayer:
    def __init__(self, symbol, max_depth=4):
        self.symbol = symbol
        self.opponent_symbol = 'X' if symbol == 'O' else 'O'
        self.max_depth = max_depth
        self.max_time = 5.0  # Максимальное время на ход
        
        # Паттерны для оценки позиций (в порядке убывания важности)
        self.patterns = {
            # Выигрышные комбинации
            'FIVE': ([self.symbol] * 5, 100000),
            'OPEN_FOUR': ([None, self.symbol, self.symbol, self.symbol, self.symbol, None], 50000),
            'FOUR': ([self.symbol] * 4, 10000),
            
            # Угрозы соперника (высокий приоритет защиты)
            'OPP_FIVE': ([self.opponent_symbol] * 5, -100000),
            'OPP_OPEN_FOUR': ([None, self.opponent_symbol, self.opponent_symbol, self.opponent_symbol, self.opponent_symbol, None], -50000),
            'OPP_FOUR': ([self.opponent_symbol] * 4, -10000),
            
            # Тройки
            'OPEN_THREE': ([None, self.symbol, self.symbol, self.symbol, None], 1000),
            'THREE': ([self.symbol] * 3, 500),
            'OPP_OPEN_THREE': ([None, self.opponent_symbol, self.opponent_symbol, self.opponent_symbol, None], -1000),
            'OPP_THREE': ([self.opponent_symbol] * 3, -500),
            
            # Двойки
            'OPEN_TWO': ([None, self.symbol, self.symbol, None], 100),
            'TWO': ([self.symbol] * 2, 50),
            'OPP_OPEN_TWO': ([None, self.opponent_symbol, self.opponent_symbol, None], -100),
            'OPP_TWO': ([self.opponent_symbol] * 2, -50),
            
            # Одиночки
            'ONE': ([self.symbol], 10),
            'OPP_ONE': ([self.opponent_symbol], -10)
        }
        
    def get_move(self, game) -> Optional[Tuple[int, int]]:
        """Получить лучший ход для ИИ"""
        start_time = time.time()
        
        try:
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                logger.warning("⚠️ Нет доступных ходов для ИИ")
                return None
                
            logger.info(f"🤖 ИИ выбирает из {len(valid_moves)} возможных ходов")
            
            # Для первого хода - ставим в центр
            if game.move_count == 0:
                center = game.board_size // 2
                return (center, center)
            
            # Проверяем критические ходы (победа/защита)
            critical_move = self._find_critical_move(game, valid_moves)
            if critical_move:
                logger.info(f"🎯 Найден критический ход: {critical_move}")
                return critical_move
            
            # Ищем лучший ход с помощью minimax
            best_move = self._find_best_move(game, valid_moves, start_time)
            
            elapsed_time = time.time() - start_time
            logger.info(f"🤖 ИИ выбрал ход {best_move} за {elapsed_time:.2f}с")
            
            return best_move
            
        except Exception as e:
            logger.error(f"❌ Ошибка ИИ: {e}")
            # Возвращаем случайный ход в случае ошибки
            return random.choice(valid_moves) if valid_moves else None
    
    def _find_critical_move(self, game, valid_moves) -> Optional[Tuple[int, int]]:
        """Поиск критических ходов (победа или защита от поражения)"""
        board = game.board
        
        for row, col in valid_moves:
            # Проверяем, может ли ИИ выиграть этим ходом
            if self._check_winning_move(board, row, col, self.symbol):
                return (row, col)
        
        for row, col in valid_moves:
            # Проверяем, нужно ли защищаться от поражения
            if self._check_winning_move(board, row, col, self.opponent_symbol):
                return (row, col)
        
        # Проверяем угрозы открытых четверок
        for row, col in valid_moves:
            if self._creates_open_four(board, row, col, self.symbol):
                return (row, col)
        
        # Защищаемся от открытых четверок соперника
        for row, col in valid_moves:
            if self._creates_open_four(board, row, col, self.opponent_symbol):
                return (row, col)
        
        return None
    
    def _check_winning_move(self, board, row, col, symbol) -> bool:
        """Проверяет, создает ли данный ход выигрышную комбинацию"""
        # Временно ставим фигуру
        board[row][col] = symbol
        
        # Проверяем все направления
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1  # Считаем текущую фигуру
            
            # Проверяем в одну сторону
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r, c = r + dr, c + dc
            
            # Проверяем в другую сторону
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r, c = r - dr, c - dc
            
            if count >= 5:
                board[row][col] = ''  # Убираем временную фигуру
                return True
        
        board[row][col] = ''  # Убираем временную фигуру
        return False
    
    def _creates_open_four(self, board, row, col, symbol) -> bool:
        """Проверяет, создает ли ход открытую четверку"""
        board[row][col] = symbol
        
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            # Проверяем последовательность длиной 6 (для открытой четверки)
            for start_offset in range(-5, 1):
                sequence = []
                for i in range(6):
                    r = row + (start_offset + i) * dr
                    c = col + (start_offset + i) * dc
                    
                    if 0 <= r < len(board) and 0 <= c < len(board[0]):
                        sequence.append(board[r][c])
                    else:
                        sequence.append('#')  # Граница доски
                
                # Проверяем паттерн открытой четверки: .XXXX.
                if (len(sequence) == 6 and 
                    sequence[0] == '' and 
                    sequence[5] == '' and
                    all(sequence[i] == symbol for i in range(1, 5))):
                    board[row][col] = ''
                    return True
        
        board[row][col] = ''
        return False
    
    def _find_best_move(self, game, valid_moves, start_time) -> Tuple[int, int]:
        """Поиск лучшего хода с помощью оценки позиций"""
        best_score = float('-inf')
        best_moves = []
        
        for row, col in valid_moves:
            # Проверяем лимит времени
            if time.time() - start_time > self.max_time:
                break
                
            score = self._evaluate_move(game.board, row, col)
            
            if score > best_score:
                best_score = score
                best_moves = [(row, col)]
            elif score == best_score:
                best_moves.append((row, col))
        
        # Если несколько ходов с одинаковой оценкой, выбираем случайный
        return random.choice(best_moves) if best_moves else random.choice(valid_moves)
    
    def _evaluate_move(self, board, row, col) -> float:
        """Оценка конкретного хода"""
        # Временно ставим фигуру
        board[row][col] = self.symbol
        
        # Оценка позиции для ИИ
        ai_score = self._evaluate_position(board, self.symbol)
        
        # Убираем фигуру и ставим фигуру соперника для оценки защиты
        board[row][col] = self.opponent_symbol
        opponent_score = self._evaluate_position(board, self.opponent_symbol)
        
        # Убираем временную фигуру
        board[row][col] = ''
        
        # Комбинируем оценки (атака + защита)
        total_score = ai_score - opponent_score * 0.9  # Защита чуть менее важна
        
        # Бонус за позицию ближе к центру
        center = len(board) // 2
        distance_to_center = abs(row - center) + abs(col - center)
        center_bonus = max(0, 14 - distance_to_center) * 5
        
        return total_score + center_bonus
    
    def _evaluate_position(self, board, symbol) -> float:
        """Оценка позиции для данного символа"""
        score = 0
        board_size = len(board)
        
        # Проверяем все возможные линии
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(board_size):
            for col in range(board_size):
                for dr, dc in directions:
                    # Проверяем линию длиной 5
                    line = []
                    for i in range(5):
                        r, c = row + i * dr, col + i * dc
                        if 0 <= r < board_size and 0 <= c < board_size:
                            cell = board[r][c]
                            line.append(cell if cell != '' else None)
                        else:
                            line.append('#')  # Граница доски
                    
                    # Оценка линии
                    score += self._evaluate_line(line, symbol)
        
        return score
    
    def _evaluate_line(self, line, symbol) -> float:
        """Оценка конкретной линии из 5 клеток"""
        if len(line) != 5:
            return 0
            
        # Подсчитываем фигуры
        my_count = line.count(symbol)
        opp_count = line.count('X' if symbol == 'O' else 'O')
        empty_count = line.count(None)
        
        # Если есть фигуры соперника, линия бесполезна
        if opp_count > 0:
            return 0
        
        # Оценка в зависимости от количества фигур
        if my_count == 5:
            return 100000  # Победа
        elif my_count == 4 and empty_count == 1:
            return 10000   # Четверка
        elif my_count == 3 and empty_count == 2:
            # Проверяем, открытая ли тройка
            if line[0] is None and line[4] is None:
                return 1000  # Открытая тройка
            else:
                return 500   # Обычная тройка
        elif my_count == 2 and empty_count == 3:
            return 100     # Двойка
        elif my_count == 1 and empty_count == 4:
            return 10      # Одиночка
        
        return 0
    
    def _has_adjacent_stones(self, board, row, col) -> bool:
        """Проверяет, есть ли соседние камни"""
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if (0 <= nr < len(board) and 0 <= nc < len(board[0]) and 
                board[nr][nc] != ''):
                return True
        
        return False 