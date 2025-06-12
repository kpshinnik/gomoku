let gameState = {
    board: [],
    currentPlayer: 'X',
    userSymbol: 'X',
    aiSymbol: 'O',
    gameOver: false,
    winner: null
};

// Инициализация игры
document.addEventListener('DOMContentLoaded', function() {
    initializeBoard();
    setupEventListeners();
    showSymbolChoice();
});

function initializeBoard() {
    const gameBoard = document.getElementById('game-board');
    gameBoard.innerHTML = '';
    
    // Создаем сетку 15x15
    for (let row = 0; row < 15; row++) {
        for (let col = 0; col < 15; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.addEventListener('click', () => handleCellClick(row, col));
            gameBoard.appendChild(cell);
        }
    }
}

function setupEventListeners() {
    document.getElementById('new-game').addEventListener('click', showSymbolChoice);
    document.getElementById('restart').addEventListener('click', showSymbolChoice);
    document.getElementById('select-x').addEventListener('click', () => chooseSymbol('X'));
    document.getElementById('select-o').addEventListener('click', () => chooseSymbol('O'));
}

function showSymbolChoice() {
    // Сброс статуса игры
    gameState.gameOver = false;
    gameState.winner = null;
    
    // Показываем выбор символа
    document.querySelector('.symbol-selection').style.display = 'block';
    document.getElementById('game-status').textContent = 'Выберите ваш символ и нажмите "Новая игра"';
    
    // Очищаем доску
    initializeBoard();
}

function chooseSymbol(symbol) {
    // Обновляем UI
    document.querySelector('.symbol-selection button.active').classList.remove('active');
    if (symbol === 'X') {
        document.getElementById('select-x').classList.add('active');
    } else {
        document.getElementById('select-o').classList.add('active');
    }
    
    // Обновляем информационную панель
    document.getElementById('human-symbol').textContent = symbol;
    document.getElementById('ai-symbol').textContent = symbol === 'X' ? 'O' : 'X';
    
    startNewGame(symbol);
}

async function startNewGame(userSymbol) {
    try {
        showStatus('Создание новой игры...');
        
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol: userSymbol })
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameState.userSymbol = data.user_symbol;
            gameState.aiSymbol = data.ai_symbol;
            gameState.currentPlayer = data.current_player;
            gameState.gameOver = false;
            gameState.winner = null;
            
            updateBoard(data.board);
            updateGameInfo(data);
            
            // Если ИИ должен ходить первым (пользователь выбрал O)
            if (data.current_player !== userSymbol) {
                showStatus(`Игра началась! Вы играете за ${userSymbol}. ИИ делает первый ход...`);
                // Запрашиваем ход ИИ
                requestAIMove();
            } else {
                showStatus(`Игра началась! Вы играете за ${userSymbol}. Ваш ход!`);
            }
            
            console.log('✅ Игра успешно создана:', data);
        } else {
            showStatus(`Ошибка создания игры: ${data.error}`);
            console.error('❌ Ошибка создания игры:', data);
        }
    } catch (error) {
        showStatus('Ошибка подключения к серверу');
        console.error('❌ Ошибка запроса:', error);
    }
}

async function handleCellClick(row, col) {
    if (gameState.gameOver) {
        showStatus('Игра окончена! Начните новую игру.');
        return;
    }
    
    if (gameState.currentPlayer !== gameState.userSymbol) {
        showStatus('Сейчас не ваш ход!');
        return;
    }
    
    // Проверяем, что клетка пуста
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (cell.textContent !== '') {
        showStatus('Эта клетка уже занята!');
        return;
    }
    
    try {
        showStatus('Обработка вашего хода...');
        
        const response = await fetch('/api/make_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ row: row, col: col })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateBoard(data.board);
            
            if (data.game_over) {
                gameState.gameOver = true;
                gameState.winner = data.winner;
                
                if (data.winner === gameState.userSymbol) {
                    showStatus('🎉 Поздравляем! Вы выиграли!');
                } else if (data.winner === gameState.aiSymbol) {
                    showStatus('😔 ИИ выиграл. Попробуйте еще раз!');
                } else {
                    showStatus('🤝 Ничья!');
                }
            } else {
                // Показываем ход ИИ, если он был сделан
                if (data.ai_move) {
                    const [aiRow, aiCol] = data.ai_move;
                    highlightLastMove(aiRow, aiCol);
                    showStatus(`ИИ сходил на ${String.fromCharCode(65 + aiCol)}${aiRow + 1}. Ваш ход!`);
                } else {
                    showStatus('Ваш ход!');
                }
                
                gameState.currentPlayer = data.current_player;
            }
            
            console.log('✅ Ход обработан:', data);
        } else {
            showStatus(`Ошибка хода: ${data.error}`);
            console.error('❌ Ошибка хода:', data);
        }
    } catch (error) {
        showStatus('Ошибка подключения к серверу');
        console.error('❌ Ошибка запроса:', error);
    }
}

function updateBoard(board) {
    for (let row = 0; row < 15; row++) {
        for (let col = 0; col < 15; col++) {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            const cellValue = board[row][col];
            
            cell.textContent = cellValue;
            cell.className = 'cell';
            
            if (cellValue === 'X') {
                cell.classList.add('x');
            } else if (cellValue === 'O') {
                cell.classList.add('o');
            }
        }
    }
}

function updateGameInfo(data) {
    document.getElementById('current-player').textContent = data.current_player;
    document.getElementById('move-count').textContent = data.move_count || 0;
    document.getElementById('human-symbol').textContent = data.user_symbol || gameState.userSymbol;
    document.getElementById('ai-symbol').textContent = data.ai_symbol || gameState.aiSymbol;
}

function highlightLastMove(row, col) {
    // Убираем предыдущую подсветку
    document.querySelectorAll('.cell.last-move').forEach(cell => {
        cell.classList.remove('last-move');
    });
    
    // Добавляем подсветку к последнему ходу
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (cell) {
        cell.classList.add('last-move');
    }
}

function showStatus(message) {
    document.getElementById('game-status').textContent = message;
}

async function requestAIMove() {
    try {
        showStatus('ИИ думает...');
        
        const response = await fetch('/api/ai_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateBoard(data.board);
            
            if (data.game_over) {
                gameState.gameOver = true;
                gameState.winner = data.winner;
                
                if (data.winner === gameState.userSymbol) {
                    showStatus('🎉 Поздравляем! Вы выиграли!');
                } else if (data.winner === gameState.aiSymbol) {
                    showStatus('😔 ИИ выиграл. Попробуйте еще раз!');
                } else {
                    showStatus('🤝 Ничья!');
                }
            } else {
                // Показываем ход ИИ
                if (data.ai_move) {
                    const [aiRow, aiCol] = data.ai_move;
                    highlightLastMove(aiRow, aiCol);
                    showStatus(`ИИ сходил на ${String.fromCharCode(65 + aiCol)}${aiRow + 1}. Ваш ход!`);
                } else {
                    showStatus('Ваш ход!');
                }
                
                gameState.currentPlayer = data.current_player;
            }
            
            console.log('✅ Ход ИИ обработан:', data);
        } else {
            showStatus(`Ошибка хода ИИ: ${data.error}`);
            console.error('❌ Ошибка хода ИИ:', data);
        }
    } catch (error) {
        showStatus('Ошибка подключения к серверу');
        console.error('❌ Ошибка запроса хода ИИ:', error);
    }
}

// Функция для получения текущего состояния игры (для отладки)
async function getGameState() {
    try {
        const response = await fetch('/api/game_state');
        const data = await response.json();
        
        if (data.success) {
            console.log('📊 Состояние игры:', data);
            return data;
        } else {
            console.error('❌ Ошибка получения состояния:', data);
        }
    } catch (error) {
        console.error('❌ Ошибка запроса состояния:', error);
    }
} 