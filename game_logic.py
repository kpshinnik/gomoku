import logging

logger = logging.getLogger(__name__)

class GameLogic:
    def __init__(self, board_size=15):
        self.board_size = board_size
        self.board = [['.' for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 'X'  # X всегда ходит первым
        self.move_count = 0
        self.game_over = False
        self.winner = None
        
    def make_move(self, row, col, player=None):
        """Сделать ход"""
        if player is None:
            player = self.current_player
            
        # Проверки валидности
        if self.game_over:
            logger.warning("⚠️ Игра уже окончена")
            return False
            
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            logger.warning(f"⚠️ Координаты вне доски: ({row}, {col})")
            return False
            
        if self.board[row][col] != '.':
            logger.warning(f"⚠️ Клетка уже занята: ({row}, {col})")
            return False
            
        # Проверка правила соседства (кроме первого хода)
        if self.move_count > 0 and not self._has_adjacent_piece(row, col):
            logger.warning(f"⚠️ Нет соседних фигур для хода ({row}, {col})")
            return False
            
        # Делаем ход
        self.board[row][col] = player
        self.move_count += 1
        
        # Проверяем победу
        if self.check_winner():
            self.game_over = True
            self.winner = player
            logger.info(f"🏆 Победа игрока {player}!")
        else:
            # Переключаем игрока
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            
        logger.info(f"✅ Ход {player} на ({row}, {col}), счетчик: {self.move_count}")
        return True
        
    def _has_adjacent_piece(self, row, col):
        """Проверить наличие соседних фигур"""
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if (0 <= nr < self.board_size and 0 <= nc < self.board_size and 
                self.board[nr][nc] != '.'):
                return True
        return False
        
    def check_winner(self):
        """Проверить наличие победителя"""
        if self.winner:
            return True
            
        # Проверяем все позиции с фигурами
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != '.':
                    if self._check_win_from_position(row, col, self.board[row][col]):
                        self.winner = self.board[row][col]
                        return True
        return False
        
    def _check_win_from_position(self, row, col, player):
        """Проверить победу от конкретной позиции"""
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        
        for dr, dc in directions:
            count = 1  # Считаем текущую клетку
            
            # Проверяем в положительном направлении
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and 
                   self.board[r][c] == player):
                count += 1
                r, c = r + dr, c + dc
                
            # Проверяем в отрицательном направлении  
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and 
                   self.board[r][c] == player):
                count += 1
                r, c = r - dr, c - dc
                
            if count >= 5:
                return True
                
        return False
        
    def get_valid_moves(self):
        """Получить список валидных ходов"""
        if self.game_over:
            return []
            
        valid_moves = []
        
        # Первый ход - можно ставить везде
        if self.move_count == 0:
            # Возвращаем только центральную область для первого хода
            center = self.board_size // 2
            for row in range(center-2, center+3):
                for col in range(center-2, center+3):
                    if 0 <= row < self.board_size and 0 <= col < self.board_size:
                        valid_moves.append([row, col])
            return valid_moves
            
        # Для остальных ходов - только рядом с существующими фигурами
        # Оптимизированная версия: ищем соседей занятых клеток
        occupied_neighbors = set()
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != '.':
                    # Добавляем всех соседей этой занятой клетки
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if (0 <= nr < self.board_size and 0 <= nc < self.board_size and 
                                self.board[nr][nc] == '.'):
                                occupied_neighbors.add((nr, nc))
        
        # Преобразуем в список
        valid_moves = [[r, c] for r, c in occupied_neighbors]
        
        logger.debug(f"📋 Найдено валидных ходов: {len(valid_moves)}")
        return valid_moves
        
    def is_board_full(self):
        """Проверить, заполнена ли доска"""
        for row in self.board:
            for cell in row:
                if cell == '.':
                    return False
        return True
        
    def reset_game(self):
        """Сбросить игру"""
        self.board = [['.' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'X'
        self.move_count = 0
        self.game_over = False
        self.winner = None
        logger.info("🔄 Игра сброшена")
        
    def get_board_state(self):
        """Получить состояние доски"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'move_count': self.move_count,
            'game_over': self.game_over,
            'winner': self.winner
        }

    def is_valid_move(self, row, col):
        """Проверяет, можно ли сделать ход в данную клетку"""        
        # Проверяем границы доски
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False
        
        # Проверяем, что клетка пустая
        if self.board[row][col] != '.':
            return False
        
        # Для первого хода можно ставить в любое место
        if self.move_count == 0:
            return True
        
        # Для остальных ходов используем общую функцию
        return self._has_adjacent_piece(row, col)
    
 