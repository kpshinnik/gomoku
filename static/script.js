let gameState = {
    board: [],
    currentPlayer: 'X',
    userSymbol: 'X',
    aiSymbol: 'O',
    gameOver: false,
    winner: null,
    moveCount: 0
};

// Инициализация игры
document.addEventListener('DOMContentLoaded', function() {
    initializeBoard();
    setupEventListeners();
    showSymbolChoice();
});

function initializeBoard() {
    console.log('🎯 Инициализация доски');
    
    const gameBoard = document.getElementById('game-board');
    if (!gameBoard) {
        console.error('❌ Элемент game-board не найден!');
        return;
    }
    
    gameBoard.innerHTML = '';
    
    // Инициализируем пустую доску в состоянии
    gameState.board = [];
    for (let row = 0; row < 15; row++) {
        gameState.board[row] = [];
        for (let col = 0; col < 15; col++) {
            gameState.board[row][col] = '.';
        }
    }
    
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
    
    console.log('✅ Доска создана: 225 клеток');
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
    document.querySelectorAll('.symbol-selection button').forEach(btn => btn.classList.remove('active'));
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
            // Принудительно обновляем локальное состояние
            gameState.userSymbol = data.user_symbol;
            gameState.aiSymbol = data.ai_symbol;
            gameState.currentPlayer = data.current_player;
            gameState.gameOver = false;
            gameState.winner = null;
            gameState.moveCount = data.move_count || 0;
            
            updateBoard(data.board);
            updateGameInfo(data);
            
            // Скрываем выбор символа
            document.querySelector('.symbol-selection').style.display = 'none';
            
            // Если ИИ должен ходить первым (пользователь выбрал O)
            if (data.current_player !== userSymbol) {
                showStatus(`Игра началась! Вы играете за ${userSymbol}. ИИ делает первый ход...`);
                // Небольшая задержка перед ходом ИИ
                setTimeout(() => requestAIMove(), 500);
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
    console.log(`🎯 Клик по клетке [${row}][${col}]`);
    console.log('📊 Текущее состояние:', gameState);
    
    if (gameState.gameOver) {
        console.log('⏹️ Игра окончена');
        showStatus('Игра окончена! Начните новую игру.');
        return;
    }
    
    if (gameState.currentPlayer !== gameState.userSymbol) {
        console.log(`❌ Не ваш ход! Текущий: ${gameState.currentPlayer}, Ваш: ${gameState.userSymbol}`);
        showStatus('Сейчас не ваш ход!');
        return;
    }
    
    // Проверяем, что клетка пуста в локальном состоянии
    if (gameState.board[row] && gameState.board[row][col] !== '.') {
        console.log(`❌ Клетка [${row}][${col}] уже занята:`, gameState.board[row][col]);
        showStatus('Эта клетка уже занята!');
        return;
    }
    
    console.log(`✅ Отправка хода [${row}][${col}]`);
    
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
            // Принудительно обновляем состояние
            gameState.board = data.board;
            gameState.currentPlayer = data.current_player;
            gameState.moveCount = data.move_count || 0;
            
            updateBoard(data.board);
            updateGameInfo(data);
            
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
    console.log('🔄 Обновление доски:', board);
    
    // Обновляем локальное состояние
    gameState.board = board;
    
    for (let row = 0; row < 15; row++) {
        for (let col = 0; col < 15; col++) {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (!cell) {
                console.error(`❌ Не найдена клетка [${row}][${col}]`);
                continue;
            }
            
            const cellValue = board[row][col];
            
            // Принудительно очищаем клетку
            cell.textContent = '';
            cell.className = 'cell';
            
            if (cellValue === 'X') {
                cell.textContent = 'X';
                cell.classList.add('x');
                // Принудительно устанавливаем стили
                cell.style.color = '#e74c3c';
                cell.style.backgroundColor = '#fadbd8';
                cell.style.fontWeight = 'bold';
                console.log(`✅ Установлен X в [${row}][${col}]`);
            } else if (cellValue === 'O') {
                cell.textContent = 'O';
                cell.classList.add('o');
                // Принудительно устанавливаем стили
                cell.style.color = '#3498db';
                cell.style.backgroundColor = '#d6eaf8';
                cell.style.fontWeight = 'bold';
                console.log(`✅ Установлен O в [${row}][${col}]`);
            } else {
                // Сбрасываем стили для пустых клеток
                cell.style.color = '';
                cell.style.backgroundColor = '';
                cell.style.fontWeight = '';
            }
        }
    }
    
    console.log('✅ Доска обновлена');
}

function updateGameInfo(data) {
    document.getElementById('current-player').textContent = data.current_player || gameState.currentPlayer;
    document.getElementById('move-count').textContent = data.move_count || gameState.moveCount || 0;
    document.getElementById('human-symbol').textContent = data.user_symbol || gameState.userSymbol;
    document.getElementById('ai-symbol').textContent = data.ai_symbol || gameState.aiSymbol;
    
    // Обновляем локальное состояние
    if (data.current_player) gameState.currentPlayer = data.current_player;
    if (data.move_count !== undefined) gameState.moveCount = data.move_count;
    if (data.user_symbol) gameState.userSymbol = data.user_symbol;
    if (data.ai_symbol) gameState.aiSymbol = data.ai_symbol;
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
            // Принудительно обновляем состояние
            gameState.board = data.board;
            gameState.currentPlayer = data.current_player;
            gameState.moveCount = data.move_count || 0;
            
            updateBoard(data.board);
            updateGameInfo(data);
            
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

// Функция для получения текущего состояния игры
async function getGameState() {
    try {
        const response = await fetch('/api/game_state');
        const data = await response.json();
        
        if (data.success) {
            // Синхронизируем состояние с сервером
            gameState.board = data.board;
            gameState.currentPlayer = data.current_player;
            gameState.moveCount = data.move_count || 0;
            gameState.gameOver = data.game_over || false;
            gameState.winner = data.winner;
            
            updateBoard(data.board);
            updateGameInfo(data);
            
            console.log('📊 Состояние игры синхронизировано:', data);
            return data;
        } else {
            console.error('❌ Ошибка получения состояния:', data);
        }
    } catch (error) {
        console.error('❌ Ошибка запроса состояния:', error);
    }
}

// Автоматическая синхронизация состояния каждые 5 секунд (отключена для отладки)
// setInterval(async () => {
//     if (!gameState.gameOver) {
//         await getGameState();
//     }
// }, 5000);

// Тестовая функция для отладки
function testBoardUpdate() {
    console.log('🧪 Тестирование обновления доски');
    
    // Создаём тестовую доску
    const testBoard = [];
    for (let row = 0; row < 15; row++) {
        testBoard[row] = [];
        for (let col = 0; col < 15; col++) {
            testBoard[row][col] = '.';
        }
    }
    
    // Ставим несколько тестовых фигур
    testBoard[7][7] = 'X';
    testBoard[7][8] = 'O';
    testBoard[8][7] = 'X';
    
    console.log('🧪 Обновляем доску тестовыми данными');
    updateBoard(testBoard);
}

// Добавляем тестовую функцию в глобальную область
window.testBoardUpdate = testBoardUpdate; 