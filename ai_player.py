import random
import time
import logging
from typing import List, Tuple, Dict, Optional, Set

logger = logging.getLogger(__name__)

class AIPlayer:
    def __init__(self, symbol, max_depth=6):
        self.symbol = symbol
        self.opponent_symbol = 'X' if symbol == 'O' else 'O'
        self.max_depth = max_depth
        self.max_time = 3.0  # Максимальное время на ход
        
        # Стратегические паттерны для выигрышной игры
        self.winning_patterns = {
            # Критические паттерны (немедленная победа/защита)
            'FIVE': 1000000,
            'OPEN_FOUR': 100000,
            'FOUR_THREE': 50000,  # Комбинация 4+3
            'DOUBLE_THREE': 25000,  # Двойная тройка
            
            # Сильные атакующие паттерны
            'FOUR': 10000,
            'BROKEN_FOUR': 8000,  # Разорванная четверка
            'OPEN_THREE': 5000,
            'THREE': 1000,
            
            # Защитные паттерны
            'BLOCK_FOUR': 15000,
            'BLOCK_THREE': 3000,
            
            # Позиционные преимущества
            'CENTER_CONTROL': 500,
            'ADJACENCY': 100,
            'CORNER_TRAP': 2000,
            'SPACE_CONTROL': 800,  # Новый: контроль пространства
            'DEVELOPMENT_POTENTIAL': 600,  # Новый: потенциал развития
        }
        
        # Направления для анализа линий
        self.directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        # Стратегические позиции для первых ходов
        self.opening_book = {
            # Центральные дебюты
            (7, 7): [(6, 6), (6, 7), (6, 8), (7, 6), (7, 8), (8, 6), (8, 7), (8, 8)],
            # Диагональные дебюты
            (6, 6): [(7, 7), (5, 5), (8, 8), (7, 6), (6, 7)],
            (8, 8): [(7, 7), (9, 9), (6, 6), (7, 8), (8, 7)],
        }
        
    def get_move(self, game) -> Optional[Tuple[int, int]]:
        """Получить лучший ход для ИИ используя выигрышную стратегию"""
        start_time = time.time()
        
        try:
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                logger.warning("⚠️ Нет доступных ходов для ИИ")
                return None
                
            logger.info(f"🤖 ИИ выбирает из {len(valid_moves)} возможных ходов")
            
            # Дебютная книга для первых ходов
            opening_move = self._get_opening_move(game, valid_moves)
            if opening_move:
                logger.info(f"📚 Дебютный ход: {opening_move}")
                return opening_move
            
            # ПРИОРИТЕТ 1: Критические ходы (победа/защита)
            critical_move = self._find_critical_move(game, valid_moves)
            if critical_move:
                logger.info(f"🎯 Найден критический ход: {critical_move}")
                return critical_move
            
            # ПРИОРИТЕТ 2: Агрессивные выигрышные комбинации
            aggressive_move = self._find_aggressive_move(game, valid_moves)
            if aggressive_move:
                logger.info(f"⚔️ Агрессивный ход: {aggressive_move}")
                return aggressive_move
            
            # ПРИОРИТЕТ 3: Поиск форсированных выигрышных комбинаций
            winning_move = self._find_winning_sequence(game, valid_moves)
            if winning_move:
                logger.info(f"🏆 Найдена выигрышная комбинация: {winning_move}")
                return winning_move
            
            # ПРИОРИТЕТ 4: Защита от медленных угроз (понижен приоритет)
            slow_threat_defense = self._find_slow_threat_defense(game, valid_moves)
            if slow_threat_defense:
                logger.info(f"🛡️ Защита от медленной угрозы: {slow_threat_defense}")
                return slow_threat_defense
            
            # Стратегический анализ позиции
            best_move = self._find_strategic_move(game, valid_moves, start_time)
            
            elapsed_time = time.time() - start_time
            logger.info(f"🤖 ИИ выбрал ход {best_move} за {elapsed_time:.2f}с")
            
            return best_move
            
        except Exception as e:
            logger.error(f"❌ Ошибка ИИ: {e}")
            return random.choice(valid_moves) if valid_moves else None
    
    def _get_opening_move(self, game, valid_moves) -> Optional[Tuple[int, int]]:
        """Дебютные ходы из книги"""
        if game.move_count == 0:
            # Первый ход - всегда центр
            center = game.board_size // 2
            return (center, center)
        
        if game.move_count <= 4:
            # Ищем последний ход соперника
            last_opponent_move = self._find_last_opponent_move(game.board)
            if last_opponent_move and last_opponent_move in self.opening_book:
                candidates = [move for move in self.opening_book[last_opponent_move] 
                            if move in valid_moves]
                if candidates:
                    return random.choice(candidates)
        
        return None
    
    def _find_last_opponent_move(self, board) -> Optional[Tuple[int, int]]:
        """Находит последний ход соперника"""
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == self.opponent_symbol:
                    return (row, col)
        return None
    
    def _find_winning_sequence(self, game, valid_moves) -> Optional[Tuple[int, int]]:
        """Поиск форсированных выигрышных последовательностей"""
        board = game.board
        
        # Ищем ходы, создающие множественные угрозы
        for row, col in valid_moves:
            threats_count = self._count_threats_after_move(board, row, col, self.symbol)
            
            # Если создаем 2+ угрозы одновременно - это выигрышная комбинация
            if threats_count >= 2:
                return (row, col)
            
            # Проверяем комбинацию 4+3 (четверка + тройка)
            if self._creates_four_three_combo(board, row, col, self.symbol):
                return (row, col)
        
        return None
    
    def _count_threats_after_move(self, board, row, col, symbol) -> int:
        """Подсчитывает количество угроз после хода"""
        board[row][col] = symbol
        threats = 0
        
        # Проверяем все направления от данной позиции
        for dr, dc in self.directions:
            # Анализируем линию в обе стороны
            line_threats = self._analyze_line_threats(board, row, col, dr, dc, symbol)
            threats += line_threats
        
        board[row][col] = '.'
        return threats
    
    def _analyze_line_threats(self, board, row, col, dr, dc, symbol) -> int:
        """Анализирует угрозы в конкретном направлении"""
        threats = 0
        
        # Собираем линию длиной 9 (4 в каждую сторону + центр)
        line = []
        for i in range(-4, 5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                line.append(board[r][c])
            else:
                line.append('#')  # Граница доски
        
        # Ищем паттерны угроз
        line_str = ''.join(line)
        
        # Открытая четверка: .XXXX.
        if f'.{symbol * 4}.' in line_str:
            threats += 2  # Открытая четверка = 2 угрозы
        
        # Четверка с одной стороны: XXXX.
        elif f'{symbol * 4}.' in line_str or f'.{symbol * 4}' in line_str:
            threats += 1
        
        # Открытая тройка: .XXX.
        elif f'.{symbol * 3}.' in line_str:
            threats += 1
        
        return threats
    
    def _creates_four_three_combo(self, board, row, col, symbol) -> bool:
        """Проверяет создание комбинации 4+3"""
        board[row][col] = symbol
        
        has_four = False
        has_three = False
        
        for dr, dc in self.directions:
            pattern = self._get_line_pattern(board, row, col, dr, dc, symbol)
            
            if 'FOUR' in pattern:
                has_four = True
            elif 'THREE' in pattern:
                has_three = True
        
        board[row][col] = '.'
        return has_four and has_three
    
    def _get_line_pattern(self, board, row, col, dr, dc, symbol) -> str:
        """Определяет паттерн в линии"""
        # Подсчитываем последовательные символы
        count = 1
        
        # В одну сторону
        r, c = row + dr, col + dc
        while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
            count += 1
            r, c = r + dr, c + dc
        
        # В другую сторону
        r, c = row - dr, col - dc
        while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
            count += 1
            r, c = r - dr, c - dc
        
        if count >= 5:
            return 'FIVE'
        elif count == 4:
            return 'FOUR'
        elif count == 3:
            return 'THREE'
        else:
            return 'TWO'
    
    def _find_critical_move(self, game, valid_moves) -> Optional[Tuple[int, int]]:
        """Поиск критических ходов (победа или защита от поражения)"""
        board = game.board
        
        # 1. Проверяем возможность выиграть немедленно
        for row, col in valid_moves:
            if self._check_winning_move(board, row, col, self.symbol):
                return (row, col)
        
        # 2. КРИТИЧНО: Защищаемся от немедленного поражения
        for row, col in valid_moves:
            if self._check_winning_move(board, row, col, self.opponent_symbol):
                return (row, col)
        
        # 3. Блокируем открытую четверку соперника (высший приоритет защиты)
        for row, col in valid_moves:
            if self._creates_open_four(board, row, col, self.opponent_symbol):
                return (row, col)
        
        # 4. Создаем открытую четверку (ПОВЫШЕН ПРИОРИТЕТ)
        for row, col in valid_moves:
            if self._creates_open_four(board, row, col, self.symbol):
                return (row, col)
        
        # 5. Блокируем четверку соперника (любую)
        for row, col in valid_moves:
            if self._creates_four_threat(board, row, col, self.opponent_symbol):
                return (row, col)
        
        # 6. Создаем четверку
        for row, col in valid_moves:
            if self._creates_four_threat(board, row, col, self.symbol):
                return (row, col)
        
        # 7. Блокируем двойную тройку соперника
        for row, col in valid_moves:
            if self._creates_double_three(board, row, col, self.opponent_symbol):
                return (row, col)
        
        # 8. Создаем двойную тройку
        for row, col in valid_moves:
            if self._creates_double_three(board, row, col, self.symbol):
                return (row, col)
        
        # 9. УЛУЧШЕННАЯ защита от критических угроз
        critical_defense = self._find_critical_defense(board, valid_moves)
        if critical_defense:
            return critical_defense
        
        # 10. Блокируем открытую тройку соперника (только если критично)
        dangerous_three = self._find_dangerous_open_three(board, valid_moves)
        if dangerous_three:
            return dangerous_three
        
        return None
    
    def _creates_double_three(self, board, row, col, symbol) -> bool:
        """Проверяет создание двойной тройки"""
        board[row][col] = symbol
        
        three_count = 0
        for dr, dc in self.directions:
            if self._has_open_three_in_direction(board, row, col, dr, dc, symbol):
                three_count += 1
        
        board[row][col] = '.'
        return three_count >= 2
    
    def _has_open_three_in_direction(self, board, row, col, dr, dc, symbol) -> bool:
        """Проверяет наличие открытой тройки в направлении"""
        # Собираем линию 7 клеток
        line = []
        for i in range(-3, 4):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                line.append(board[r][c])
            else:
                line.append('#')
        
        line_str = ''.join(line)
        return f'.{symbol * 3}.' in line_str
    
    def _creates_four_threat(self, board, row, col, symbol) -> bool:
        """Проверяет, создает ли ход угрозу четверки"""
        board[row][col] = symbol
        
        for dr, dc in self.directions:
            count = 1
            
            # В одну сторону
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r, c = r + dr, c + dc
            
            # В другую сторону
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r, c = r - dr, c - dc
            
            if count >= 4:
                board[row][col] = '.'
                return True
        
        board[row][col] = '.'
        return False
    
    def _blocks_open_three(self, board, row, col, symbol) -> bool:
        """Проверяет, блокирует ли ход открытую тройку"""
        # Временно ставим фигуру соперника
        board[row][col] = self.opponent_symbol if symbol == self.symbol else self.symbol
        
        # Проверяем, была ли открытая тройка до этого хода
        for dr, dc in self.directions:
            if self._check_open_three_pattern(board, row, col, dr, dc, symbol):
                board[row][col] = '.'
                return True
        
        board[row][col] = '.'
        return False
    
    def _check_open_three_pattern(self, board, row, col, dr, dc, symbol) -> bool:
        """Проверяет паттерн открытой тройки в направлении"""
        # Проверяем несколько позиций для паттерна .XXX.
        for start_offset in range(-4, 2):
            pattern = []
            for i in range(5):
                r = row + (start_offset + i) * dr
                c = col + (start_offset + i) * dc
                
                if 0 <= r < len(board) and 0 <= c < len(board[0]):
                    pattern.append(board[r][c])
                else:
                    pattern.append('#')
            
            # Проверяем паттерн .XXX.
            if (len(pattern) == 5 and 
                pattern[0] == '.' and 
                pattern[4] == '.' and
                all(pattern[i] == symbol for i in range(1, 4))):
                return True
        
        return False
    
    def _find_strategic_move(self, game, valid_moves, start_time) -> Tuple[int, int]:
        """Стратегический анализ позиции"""
        best_score = float('-inf')
        best_moves = []
        
        for row, col in valid_moves:
            if time.time() - start_time > self.max_time:
                break
                
            score = self._evaluate_strategic_move(game.board, row, col)
            
            if score > best_score:
                best_score = score
                best_moves = [(row, col)]
            elif score == best_score:
                best_moves.append((row, col))
        
        return random.choice(best_moves) if best_moves else random.choice(valid_moves)
    
    def _evaluate_strategic_move(self, board, row, col) -> float:
        """Стратегическая оценка хода"""
        score = 0
        
        # Оценка для ИИ
        board[row][col] = self.symbol
        ai_score = self._evaluate_position_advanced(board, row, col, self.symbol)
        
        # Оценка защиты
        board[row][col] = self.opponent_symbol
        defense_score = self._evaluate_position_advanced(board, row, col, self.opponent_symbol)
        
        board[row][col] = '.'
        
        # Комбинированная оценка (атака + защита)
        # Защита важнее атаки для предотвращения поражений
        score = ai_score + defense_score * 1.2
        
        # НОВЫЕ КРИТЕРИИ ОЦЕНКИ:
        
        # 1. Контроль пространства
        space_control = self._evaluate_space_control(board, row, col)
        score += space_control
        
        # 2. Потенциал развития
        development_potential = self._evaluate_development_potential(board, row, col)
        score += development_potential
        
        # 3. Избегание "мертвых" позиций
        dead_position_penalty = self._evaluate_dead_position(board, row, col)
        score -= dead_position_penalty
        
        # 4. Бонус за центральные позиции (уменьшен)
        center = len(board) // 2
        distance_from_center = abs(row - center) + abs(col - center)
        score += max(0, 30 - distance_from_center * 3)  # Уменьшен бонус
        
        # 5. Связность с существующими фигурами
        connectivity_bonus = self._evaluate_connectivity(board, row, col)
        score += connectivity_bonus
        
        return score
    
    def _evaluate_position_advanced(self, board, row, col, symbol) -> float:
        """Продвинутая оценка позиции"""
        score = 0
        
        for dr, dc in self.directions:
            line_score = self._evaluate_line_advanced(board, row, col, dr, dc, symbol)
            score += line_score
        
        return score
    
    def _evaluate_line_advanced(self, board, row, col, dr, dc, symbol) -> float:
        """Продвинутая оценка линии"""
        # Собираем расширенную линию
        line = []
        for i in range(-6, 7):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                line.append(board[r][c])
            else:
                line.append('#')
        
        score = 0
        line_str = ''.join(line)
        
        # Паттерны для оценки
        patterns = {
            f'{symbol * 5}': 100000,  # Пятерка
            f'.{symbol * 4}.': 50000,  # Открытая четверка
            f'{symbol * 4}.': 10000,   # Четверка
            f'.{symbol * 4}': 10000,   # Четверка
            f'.{symbol * 3}.': 5000,   # Открытая тройка
            f'{symbol * 3}.': 1000,    # Тройка
            f'.{symbol * 3}': 1000,    # Тройка
            f'.{symbol * 2}.': 200,    # Открытая двойка
            f'{symbol * 2}': 50,       # Двойка
        }
        
        for pattern, value in patterns.items():
            score += line_str.count(pattern) * value
        
        return score
    
    def _check_winning_move(self, board, row, col, symbol) -> bool:
        """Проверяет, создает ли данный ход выигрышную комбинацию"""
        board[row][col] = symbol
        
        for dr, dc in self.directions:
            count = 1
            
            # В одну сторону
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r, c = r + dr, c + dc
            
            # В другую сторону
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                count += 1
                r, c = r - dr, c - dc
            
            if count >= 5:
                board[row][col] = '.'
                return True
        
        board[row][col] = '.'
        return False
    
    def _creates_open_four(self, board, row, col, symbol) -> bool:
        """Проверяет, создает ли ход открытую четверку"""
        board[row][col] = symbol
        
        for dr, dc in self.directions:
            for start_offset in range(-5, 1):
                sequence = []
                for i in range(6):
                    r = row + (start_offset + i) * dr
                    c = col + (start_offset + i) * dc
                    
                    if 0 <= r < len(board) and 0 <= c < len(board[0]):
                        sequence.append(board[r][c])
                    else:
                        sequence.append('#')
                
                if (len(sequence) == 6 and 
                    sequence[0] == '.' and 
                    sequence[5] == '.' and
                    all(sequence[i] == symbol for i in range(1, 5))):
                    board[row][col] = '.'
                    return True
        
        board[row][col] = '.'
        return False
    
    def _find_slow_threat_defense(self, game, valid_moves) -> Optional[Tuple[int, int]]:
        """Поиск защиты от медленно развивающихся угроз"""
        board = game.board
        
        # Ищем позиции соперника, которые могут стать опасными
        dangerous_positions = []
        
        for row, col in valid_moves:
            # Проверяем, создает ли соперник потенциальную угрозу на этой позиции
            threat_level = self._evaluate_potential_threat(board, row, col, self.opponent_symbol)
            
            if threat_level > 2000:  # Высокий уровень потенциальной угрозы
                dangerous_positions.append((row, col, threat_level))
        
        # Сортируем по уровню угрозы
        dangerous_positions.sort(key=lambda x: x[2], reverse=True)
        
        # Возвращаем защиту от самой опасной позиции
        if dangerous_positions:
            return (dangerous_positions[0][0], dangerous_positions[0][1])
        
        return None
    
    def _evaluate_potential_threat(self, board, row, col, symbol) -> float:
        """Оценивает потенциальную угрозу позиции"""
        board[row][col] = symbol
        
        threat_score = 0
        
        # Анализируем все направления
        for dr, dc in self.directions:
            # Проверяем развитие в каждом направлении
            line_potential = self._analyze_line_potential(board, row, col, dr, dc, symbol)
            threat_score += line_potential
        
        # Бонус за создание множественных линий развития
        development_lines = self._count_development_lines(board, row, col, symbol)
        if development_lines >= 2:
            threat_score += 1500  # Бонус за множественное развитие
        
        board[row][col] = '.'
        return threat_score
    
    def _analyze_line_potential(self, board, row, col, dr, dc, symbol) -> float:
        """Анализирует потенциал развития линии"""
        potential = 0
        
        # Собираем расширенную линию (7 клеток в каждую сторону)
        line = []
        positions = []
        
        for i in range(-7, 8):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                line.append(board[r][c])
                positions.append((r, c))
            else:
                line.append('#')
                positions.append(None)
        
        line_str = ''.join(line)
        
        # Ищем паттерны потенциального развития
        patterns = {
            f'.{symbol}..{symbol}.': 800,    # Разорванная тройка с потенциалом
            f'.{symbol}.{symbol}.': 600,     # Двойка с пространством
            f'..{symbol}{symbol}..': 700,    # Центральная двойка
            f'.{symbol}{symbol}.': 400,      # Простая двойка
            f'...{symbol}...': 200,          # Одиночка с пространством
        }
        
        for pattern, value in patterns.items():
            potential += line_str.count(pattern) * value
        
        # Дополнительный анализ пространства
        empty_space = line_str.count('.')
        if empty_space >= 5:  # Достаточно места для развития
            potential += empty_space * 50
        
        return potential
    
    def _count_development_lines(self, board, row, col, symbol) -> int:
        """Подсчитывает количество линий развития"""
        development_count = 0
        
        for dr, dc in self.directions:
            if self._has_development_potential(board, row, col, dr, dc, symbol):
                development_count += 1
        
        return development_count
    
    def _has_development_potential(self, board, row, col, dr, dc, symbol) -> bool:
        """Проверяет наличие потенциала развития в направлении"""
        # Проверяем 5 клеток в каждую сторону
        empty_count = 0
        symbol_count = 0
        
        for i in range(-5, 6):
            if i == 0:
                continue
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                if board[r][c] == '.':
                    empty_count += 1
                elif board[r][c] == symbol:
                    symbol_count += 1
        
        # Потенциал есть, если достаточно места и есть свои фигуры
        return empty_count >= 3 and symbol_count >= 1
    
    def _evaluate_space_control(self, board, row, col) -> float:
        """Оценивает контроль пространства"""
        control_score = 0
        
        # Проверяем область 5x5 вокруг позиции
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = row + dr, col + dc
                if 0 <= r < len(board) and 0 <= c < len(board[0]):
                    if board[r][c] == '.':
                        # Пустые клетки дают контроль
                        distance = abs(dr) + abs(dc)
                        control_score += max(0, 50 - distance * 10)
                    elif board[r][c] == self.symbol:
                        # Свои фигуры усиливают контроль
                        control_score += 30
        
        return control_score
    
    def _evaluate_development_potential(self, board, row, col) -> float:
        """Оценивает потенциал развития позиции"""
        potential_score = 0
        
        # Проверяем каждое направление
        for dr, dc in self.directions:
            line_potential = 0
            
            # Анализируем линию 9 клеток
            for i in range(-4, 5):
                r, c = row + i * dr, col + i * dc
                if 0 <= r < len(board) and 0 <= c < len(board[0]):
                    if board[r][c] == '.':
                        line_potential += 10
                    elif board[r][c] == self.symbol:
                        line_potential += 20
                    elif board[r][c] == self.opponent_symbol:
                        line_potential -= 15  # Блокировка развития
            
            potential_score += max(0, line_potential)
        
        return potential_score
    
    def _evaluate_dead_position(self, board, row, col) -> float:
        """Оценивает "мертвость" позиции (закрытые линии)"""
        dead_penalty = 0
        
        for dr, dc in self.directions:
            # Проверяем, заблокирована ли линия с обеих сторон
            blocked_count = 0
            
            # Проверяем блокировку в положительном направлении
            for i in range(1, 5):
                r, c = row + i * dr, col + i * dc
                if (r < 0 or r >= len(board) or c < 0 or c >= len(board[0]) or 
                    board[r][c] == self.opponent_symbol):
                    blocked_count += 1
                    break
                elif board[r][c] == self.symbol:
                    break
            
            # Проверяем блокировку в отрицательном направлении
            for i in range(1, 5):
                r, c = row - i * dr, col - i * dc
                if (r < 0 or r >= len(board) or c < 0 or c >= len(board[0]) or 
                    board[r][c] == self.opponent_symbol):
                    blocked_count += 1
                    break
                elif board[r][c] == self.symbol:
                    break
            
            # Если заблокировано с обеих сторон - штраф
            if blocked_count >= 2:
                dead_penalty += 200
        
        return dead_penalty
    
    def _evaluate_connectivity(self, board, row, col) -> float:
        """Оценивает связность с существующими фигурами"""
        connectivity_score = 0
        
        # Проверяем соседние клетки
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                r, c = row + dr, col + dc
                if 0 <= r < len(board) and 0 <= c < len(board[0]):
                    if board[r][c] == self.symbol:
                        connectivity_score += 100
                    elif board[r][c] == self.opponent_symbol:
                        connectivity_score += 50  # Даже соперник дает связность
        
        return connectivity_score
    
    def _find_forced_sequence_defense(self, board, valid_moves) -> Optional[Tuple[int, int]]:
        """Поиск защиты от форсированных последовательностей"""
        # Ищем ходы соперника, которые создают неостановимые угрозы
        critical_defenses = []
        
        for row, col in valid_moves:
            # Проверяем, что произойдет, если соперник сходит сюда
            board[row][col] = self.opponent_symbol
            
            # Анализируем создаваемые угрозы
            threat_level = self._analyze_forced_threats(board, row, col, self.opponent_symbol)
            
            board[row][col] = '.'
            
            if threat_level > 3000:  # Критический уровень угрозы
                critical_defenses.append((row, col, threat_level))
        
        # Возвращаем защиту от самой критичной угрозы
        if critical_defenses:
            critical_defenses.sort(key=lambda x: x[2], reverse=True)
            return (critical_defenses[0][0], critical_defenses[0][1])
        
        return None
    
    def _analyze_forced_threats(self, board, row, col, symbol) -> float:
        """Анализирует форсированные угрозы от позиции"""
        threat_score = 0
        
        # Подсчитываем количество направлений с угрозами
        threat_directions = 0
        
        for dr, dc in self.directions:
            direction_threat = self._evaluate_direction_threat(board, row, col, dr, dc, symbol)
            threat_score += direction_threat
            
            if direction_threat > 1000:  # Серьезная угроза в этом направлении
                threat_directions += 1
        
        # Бонус за множественные угрозы (форсированная игра)
        if threat_directions >= 2:
            threat_score += 2000  # Множественные угрозы = форсированная последовательность
        
        return threat_score
    
    def _evaluate_direction_threat(self, board, row, col, dr, dc, symbol) -> float:
        """Оценивает угрозу в конкретном направлении"""
        threat = 0
        
        # Собираем линию 9 клеток
        line = []
        for i in range(-4, 5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                line.append(board[r][c])
            else:
                line.append('#')
        
        line_str = ''.join(line)
        
        # Анализируем угрозы
        if f'{symbol * 4}' in line_str:
            threat += 5000  # Четверка - критическая угроза
        elif f'.{symbol * 3}.' in line_str:
            threat += 3000  # Открытая тройка - серьезная угроза
        elif f'{symbol * 3}.' in line_str or f'.{symbol * 3}' in line_str:
            threat += 1500  # Тройка - умеренная угроза
        elif f'.{symbol * 2}.' in line_str:
            threat += 800   # Открытая двойка - потенциальная угроза
        
        return threat
    
    def _find_aggressive_move(self, game, valid_moves) -> Optional[Tuple[int, int]]:
        """Поиск агрессивных ходов для создания угроз"""
        board = game.board
        
        # Ищем ходы, которые создают максимальные угрозы
        aggressive_moves = []
        
        for row, col in valid_moves:
            # Оценка агрессивности хода
            aggression_score = self._evaluate_aggression(board, row, col, self.symbol)
            
            if aggression_score > 1500:  # Высокий уровень агрессии
                aggressive_moves.append((row, col, aggression_score))
        
        # Сортируем по агрессивности
        if aggressive_moves:
            aggressive_moves.sort(key=lambda x: x[2], reverse=True)
            return (aggressive_moves[0][0], aggressive_moves[0][1])
        
        return None
    
    def _evaluate_aggression(self, board, row, col, symbol) -> float:
        """Оценивает агрессивность хода"""
        board[row][col] = symbol
        
        aggression_score = 0
        
        # 1. Создание множественных угроз
        threat_count = 0
        for dr, dc in self.directions:
            if self._creates_threat_in_direction(board, row, col, dr, dc, symbol):
                threat_count += 1
        
        if threat_count >= 2:
            aggression_score += 2000  # Множественные угрозы
        elif threat_count == 1:
            aggression_score += 800   # Одна угроза
        
        # 2. Создание открытых троек
        open_threes = self._count_open_threes(board, row, col, symbol)
        aggression_score += open_threes * 1200
        
        # 3. Создание четверок
        fours = self._count_fours(board, row, col, symbol)
        aggression_score += fours * 3000
        
        # 4. Контроль центральных линий
        center_control = self._evaluate_center_control(board, row, col, symbol)
        aggression_score += center_control
        
        # 5. Создание "вилок" (двойных угроз)
        fork_potential = self._evaluate_fork_potential(board, row, col, symbol)
        aggression_score += fork_potential
        
        board[row][col] = '.'
        return aggression_score
    
    def _creates_threat_in_direction(self, board, row, col, dr, dc, symbol) -> bool:
        """Проверяет создание угрозы в направлении"""
        # Собираем линию 7 клеток
        line = []
        for i in range(-3, 4):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                line.append(board[r][c])
            else:
                line.append('#')
        
        line_str = ''.join(line)
        
        # Проверяем различные угрозы
        threats = [
            f'.{symbol * 3}.',  # Открытая тройка
            f'{symbol * 3}.',   # Тройка с одной стороны
            f'.{symbol * 3}',   # Тройка с другой стороны
            f'.{symbol * 2}.{symbol}.', # Разорванная тройка
            f'.{symbol}.{symbol * 2}.', # Разорванная тройка
        ]
        
        return any(threat in line_str for threat in threats)
    
    def _count_open_threes(self, board, row, col, symbol) -> int:
        """Подсчитывает открытые тройки"""
        count = 0
        for dr, dc in self.directions:
            if self._has_open_three_in_direction(board, row, col, dr, dc, symbol):
                count += 1
        return count
    
    def _count_fours(self, board, row, col, symbol) -> int:
        """Подсчитывает четверки"""
        count = 0
        for dr, dc in self.directions:
            line_count = 1
            
            # В одну сторону
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                line_count += 1
                r, c = r + dr, c + dc
            
            # В другую сторону
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == symbol:
                line_count += 1
                r, c = r - dr, c - dc
            
            if line_count >= 4:
                count += 1
        
        return count
    
    def _evaluate_center_control(self, board, row, col, symbol) -> float:
        """Оценивает контроль центральных линий"""
        center = len(board) // 2
        distance_from_center = abs(row - center) + abs(col - center)
        
        # Бонус за близость к центру
        center_bonus = max(0, 100 - distance_from_center * 10)
        
        # Дополнительный бонус за контроль центральных линий
        if row == center or col == center:
            center_bonus += 200
        
        # Бонус за диагональные линии через центр
        if abs(row - center) == abs(col - center):
            center_bonus += 150
        
        return center_bonus
    
    def _evaluate_fork_potential(self, board, row, col, symbol) -> float:
        """Оценивает потенциал создания вилок (двойных угроз)"""
        fork_score = 0
        
        # Проверяем, создает ли ход потенциал для будущих вилок
        potential_lines = 0
        
        for dr, dc in self.directions:
            # Анализируем потенциал линии
            line_potential = self._analyze_line_fork_potential(board, row, col, dr, dc, symbol)
            if line_potential > 0:
                potential_lines += 1
                fork_score += line_potential
        
        # Бонус за множественные потенциальные линии
        if potential_lines >= 3:
            fork_score += 500  # Высокий потенциал вилки
        elif potential_lines >= 2:
            fork_score += 200  # Средний потенциал
        
        return fork_score
    
    def _analyze_line_fork_potential(self, board, row, col, dr, dc, symbol) -> float:
        """Анализирует потенциал вилки в линии"""
        potential = 0
        
        # Собираем линию 9 клеток
        line = []
        for i in range(-4, 5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                line.append(board[r][c])
            else:
                line.append('#')
        
        line_str = ''.join(line)
        
        # Паттерны потенциала вилки
        patterns = {
            f'..{symbol}..': 100,    # Одиночка с пространством
            f'.{symbol}.{symbol}.': 200,  # Разорванная двойка
            f'..{symbol}{symbol}.': 150,  # Двойка с пространством
            f'.{symbol}{symbol}..': 150,  # Двойка с пространством
        }
        
        for pattern, value in patterns.items():
            potential += line_str.count(pattern) * value
        
        return potential
    
    def _find_critical_defense(self, board, valid_moves) -> Optional[Tuple[int, int]]:
        """Улучшенная защита от критических угроз"""
        critical_threats = []
        
        for row, col in valid_moves:
            # Анализируем, что произойдет, если соперник сходит сюда
            board[row][col] = self.opponent_symbol
            
            threat_level = 0
            
            # 1. Проверяем создание множественных угроз
            multiple_threats = self._count_multiple_threats(board, row, col, self.opponent_symbol)
            threat_level += multiple_threats * 1000
            
            # 2. Проверяем создание неблокируемых комбинаций
            unblockable = self._creates_unblockable_threat(board, row, col, self.opponent_symbol)
            if unblockable:
                threat_level += 2000
            
            # 3. Проверяем создание выигрышных последовательностей
            winning_sequence = self._creates_winning_sequence(board, row, col, self.opponent_symbol)
            if winning_sequence:
                threat_level += 1500
            
            board[row][col] = '.'
            
            if threat_level > 1500:  # Критический уровень
                critical_threats.append((row, col, threat_level))
        
        if critical_threats:
            critical_threats.sort(key=lambda x: x[2], reverse=True)
            return (critical_threats[0][0], critical_threats[0][1])
        
        return None
    
    def _count_multiple_threats(self, board, row, col, symbol) -> int:
        """Подсчитывает количество создаваемых угроз"""
        threat_count = 0
        
        for dr, dc in self.directions:
            if self._creates_threat_in_direction(board, row, col, dr, dc, symbol):
                threat_count += 1
        
        return threat_count
    
    def _creates_unblockable_threat(self, board, row, col, symbol) -> bool:
        """Проверяет создание неблокируемой угрозы"""
        # Проверяем создание двух открытых троек одновременно
        open_three_count = 0
        
        for dr, dc in self.directions:
            if self._has_open_three_in_direction(board, row, col, dr, dc, symbol):
                open_three_count += 1
        
        return open_three_count >= 2
    
    def _creates_winning_sequence(self, board, row, col, symbol) -> bool:
        """Проверяет создание выигрышной последовательности"""
        # Проверяем комбинации типа 4+3, 3+3+3 и т.д.
        fours = self._count_fours(board, row, col, symbol)
        threes = self._count_open_threes(board, row, col, symbol)
        
        # Комбинация четверка + тройка = выигрыш
        if fours >= 1 and threes >= 1:
            return True
        
        # Три открытые тройки = выигрыш
        if threes >= 3:
            return True
        
        return False
    
    def _find_dangerous_open_three(self, board, valid_moves) -> Optional[Tuple[int, int]]:
        """Находит опасные открытые тройки для блокировки"""
        dangerous_threes = []
        
        for row, col in valid_moves:
            # Проверяем, блокирует ли ход опасную открытую тройку
            if self._blocks_dangerous_open_three(board, row, col):
                danger_level = self._evaluate_three_danger(board, row, col)
                dangerous_threes.append((row, col, danger_level))
        
        if dangerous_threes:
            dangerous_threes.sort(key=lambda x: x[2], reverse=True)
            return (dangerous_threes[0][0], dangerous_threes[0][1])
        
        return None
    
    def _blocks_dangerous_open_three(self, board, row, col) -> bool:
        """Проверяет, блокирует ли ход опасную открытую тройку"""
        # Ставим свою фигуру
        board[row][col] = self.symbol
        
        # Проверяем, была ли здесь открытая тройка соперника
        for dr, dc in self.directions:
            if self._check_blocked_open_three(board, row, col, dr, dc, self.opponent_symbol):
                board[row][col] = '.'
                return True
        
        board[row][col] = '.'
        return False
    
    def _check_blocked_open_three(self, board, row, col, dr, dc, symbol) -> bool:
        """Проверяет, была ли заблокирована открытая тройка"""
        # Проверяем паттерны вокруг заблокированной позиции
        for offset in range(-2, 3):
            pattern = []
            for i in range(5):
                r = row + (offset + i - 2) * dr
                c = col + (offset + i - 2) * dc
                
                if r == row and c == col:
                    pattern.append('.')  # Представляем как пустую для проверки
                elif 0 <= r < len(board) and 0 <= c < len(board[0]):
                    pattern.append(board[r][c])
                else:
                    pattern.append('#')
            
            # Проверяем, был ли здесь паттерн .XXX.
            pattern_str = ''.join(pattern)
            if f'.{symbol * 3}.' in pattern_str:
                return True
        
        return False
    
    def _evaluate_three_danger(self, board, row, col) -> float:
        """Оценивает опасность открытой тройки"""
        danger = 0
        
        # Базовая опасность открытой тройки
        danger += 500
        
        # Дополнительная опасность, если рядом есть другие фигуры соперника
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                r, c = row + dr, col + dc
                if (0 <= r < len(board) and 0 <= c < len(board[0]) and 
                    board[r][c] == self.opponent_symbol):
                    danger += 100
        
        # Опасность в зависимости от позиции на доске
        center = len(board) // 2
        distance_from_center = abs(row - center) + abs(col - center)
        danger += max(0, 200 - distance_from_center * 20)
        
        return danger 