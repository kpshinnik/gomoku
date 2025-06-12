let gameState = {
    board: [],
    currentPlayer: 'X',
    userSymbol: 'X',
    aiSymbol: 'O',
    gameOver: false,
    winner: null,
    moveCount: 0
};

console.log('🚀 JavaScript загружен, начальное состояние:', gameState);

// Инициализация игры
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM загружен, начинаем инициализацию');
    
    // Проверяем наличие модального окна сразу при загрузке
    const modal = document.getElementById('game-result-modal');
    console.log('🔍 Проверка модального окна при загрузке:', modal ? 'НАЙДЕНО' : 'НЕ НАЙДЕНО');
    if (!modal) {
        console.error('❌ КРИТИЧЕСКАЯ ОШИБКА: Модальное окно отсутствует в HTML!');
    }
    
    // Проверяем все необходимые элементы
    const requiredElements = [
        'game-result-modal',
        'modal-content', 
        'result-icon',
        'result-title',
        'result-message'
    ];
    
    console.log('🔍 Проверка всех элементов модального окна:');
    requiredElements.forEach(id => {
        const element = document.getElementById(id);
        console.log(`  - ${id}: ${element ? 'НАЙДЕН' : 'НЕ НАЙДЕН'}`);
    });
    
    initializeBoard();
    setupEventListeners();
    
    // Убеждаемся, что кнопки выбора символа видны
    document.querySelector('.symbol-selection').style.display = 'block';
    
    // По умолчанию выбираем X (только если игра не идет)
    if (gameState.moveCount === 0) {
        chooseSymbol('X');
        document.getElementById('game-status').textContent = 'Символ X выбран по умолчанию. Нажмите "Новая игра" для начала или выберите другой символ.';
    }
    
    console.log('✅ Инициализация завершена');
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
    console.log('🎯 Настройка обработчиков событий');
    document.getElementById('new-game').addEventListener('click', startNewGameWithSelectedSymbol);
    document.getElementById('restart').addEventListener('click', startNewGameWithSelectedSymbol);
    document.getElementById('select-x').addEventListener('click', () => chooseSymbol('X'));
    document.getElementById('select-o').addEventListener('click', () => chooseSymbol('O'));
}

function startNewGameWithSelectedSymbol() {
    console.log('🎮 Запуск новой игры с выбранным символом');
    
    // Определяем выбранный символ по активной кнопке
    const activeButton = document.querySelector('.symbol-btn.active');
    if (!activeButton) {
        showStatus('Сначала выберите символ (X или O)!');
        return;
    }
    
    const selectedSymbol = activeButton.id === 'select-x' ? 'X' : 'O';
    console.log('🎯 Выбранный символ:', selectedSymbol);
    
    startNewGame(selectedSymbol);
}

function showSymbolChoice() {
    console.log('🎮 Показ выбора символа');
    
    // Сброс статуса игры
    gameState.gameOver = false;
    gameState.winner = null;
    
    // Показываем выбор символа (всегда видимый)
    document.querySelector('.symbol-selection').style.display = 'block';
    document.getElementById('game-status').textContent = 'Выберите ваш символ для новой игры';
    
    // Очищаем доску
    initializeBoard();
}

function chooseSymbol(symbol) {
    console.log('🎯 Выбран символ:', symbol);
    
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
    
    // Обновляем статус
    showStatus(`Символ ${symbol} выбран! Нажмите "Новая игра" для начала.`);
    
    // Сохраняем выбор в состоянии игры
    gameState.userSymbol = symbol;
    gameState.aiSymbol = symbol === 'X' ? 'O' : 'X';
}

async function startNewGame(userSymbol) {
    console.log('🎮 Начало новой игры с символом:', userSymbol);
    
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
        console.log('📦 Ответ сервера на создание игры:', data);
        
        if (data.success) {
            console.log('✅ Игра успешно создана');
            
            // Принудительно обновляем локальное состояние
            gameState.userSymbol = data.user_symbol;
            gameState.aiSymbol = data.ai_symbol;
            gameState.currentPlayer = data.current_player;
            gameState.gameOver = false;
            gameState.winner = null;
            gameState.moveCount = data.move_count || 0;
            
            console.log('🔄 Обновленное состояние игры:', gameState);
            console.log('📊 Доска от сервера при создании игры:', data.board);
            
            // КРИТИЧЕСКИ ВАЖНО: Синхронизируем состояние доски с сервером
            updateBoard(data.board);
            updateGameInfo(data);
            
            // Оставляем выбор символа видимым для возможности смены
            // document.querySelector('.symbol-selection').style.display = 'none';
            
            // Проверяем, сделал ли ИИ первый ход
            if (data.ai_move) {
                const [aiRow, aiCol] = data.ai_move;
                console.log(`🤖 ИИ сделал первый ход на [${aiRow}][${aiCol}]`);
                highlightLastMove(aiRow, aiCol);
                showStatus(`Игра началась! Вы играете за ${userSymbol}. ИИ сходил на ${String.fromCharCode(65 + aiCol)}${aiRow + 1}. Ваш ход!`);
            } else if (data.current_player !== userSymbol) {
                // ИИ должен ходить первым, но еще не сходил (старая логика)
                showStatus(`Игра началась! Вы играете за ${userSymbol}. ИИ делает первый ход...`);
                setTimeout(() => requestAIMove(), 500);
            } else {
                // Пользователь ходит первым
                showStatus(`Игра началась! Вы играете за ${userSymbol}. Ваш ход!`);
            }
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
    console.log(`🎯 КЛИК по клетке [${row}][${col}]`);
    console.log('📊 Текущее состояние игры:', gameState);
    
    // Проверяем, что символ выбран
    if (!gameState.userSymbol || gameState.userSymbol === '') {
        console.log('❌ Символ не выбран! Показываем выбор символа.');
        showSymbolChoice();
        showStatus('Сначала выберите символ!');
        return;
    }
    
    // Если игра не инициализирована, создаем новую автоматически
    if (!gameState.board || gameState.board.length === 0 || gameState.moveCount === 0) {
        console.log('⚠️ Игра не инициализирована, создаем новую автоматически...');
        showStatus('Создание новой игры...');
        await startNewGame(gameState.userSymbol);
        
        // Проверяем, что игра успешно создана
        if (!gameState.board || gameState.board.length === 0) {
            console.error('❌ Не удалось создать игру');
            showStatus('Ошибка создания игры. Попробуйте еще раз.');
            return;
        }
    }
    
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
    console.log(`🔍 Проверка клетки [${row}][${col}]: "${gameState.board[row][col]}"`);
    console.log(`🔍 Полное состояние доски:`, gameState.board);
    
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
        
        console.log('📡 Получен ответ от сервера, статус:', response.status);
        
        const data = await response.json();
        console.log('📦 Данные ответа от сервера:', data);
        
        if (data.success) {
            console.log('✅ Сервер подтвердил ход');
            console.log('📊 Новая доска от сервера:', data.board);
            
            // Принудительно обновляем состояние
            gameState.board = data.board;
            gameState.currentPlayer = data.current_player;
            gameState.moveCount = data.move_count || 0;
            
            console.log('🎯 Вызываем updateBoard...');
            updateBoard(data.board);
            console.log('📝 Вызываем updateGameInfo...');
            updateGameInfo(data);
            
            // КРИТИЧЕСКАЯ ПРОВЕРКА ЗАВЕРШЕНИЯ ИГРЫ
            console.log('🔍 ПРОВЕРКА ЗАВЕРШЕНИЯ ИГРЫ:');
            console.log('🔍 data.game_over =', data.game_over);
            console.log('🔍 typeof data.game_over =', typeof data.game_over);
            console.log('🔍 data.winner =', data.winner);
            console.log('🔍 Полные данные ответа:', JSON.stringify(data, null, 2));
            
            // ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА СТАТУСА
            console.log('🔍 gameState.gameOver =', gameState.gameOver);
            console.log('🔍 gameState.winner =', gameState.winner);
            
            if (data.game_over) {
                console.log('🏁 ИГРА ЗАВЕРШЕНА! Данные:', data);
                gameState.gameOver = true;
                gameState.winner = data.winner;
                
                console.log('🏆 Победитель:', data.winner);
                console.log('👤 Символ пользователя:', gameState.userSymbol);
                console.log('🤖 Символ ИИ:', gameState.aiSymbol);
                
                if (data.winner === gameState.userSymbol) {
                    showStatus('🎉 Поздравляем! Вы выиграли!');
                } else if (data.winner === gameState.aiSymbol) {
                    showStatus('😔 ИИ выиграл. Попробуйте еще раз!');
                } else {
                    showStatus('🤝 Ничья!');
                }
                
                // Показываем модальное окно результата с задержкой
                console.log('⏰ Запуск таймера для показа модального окна...');
                setTimeout(() => {
                    console.log('🎯 Вызов showGameResultModal с параметрами:', {
                        winner: data.winner,
                        gameData: { move_count: gameState.moveCount }
                    });
                    showGameResultModal(data.winner, {
                        move_count: gameState.moveCount
                    });
                }, 1000);
            } else {
                console.log('❌ УСЛОВИЕ data.game_over НЕ ВЫПОЛНЕНО!');
                console.log('❌ Возможно, игра завершена, но условие не сработало');
                
                // Дополнительная проверка на наличие победителя
                if (data.winner) {
                    console.log('🚨 НАЙДЕН ПОБЕДИТЕЛЬ БЕЗ game_over! Принудительно показываем модальное окно');
                    gameState.gameOver = true;
                    gameState.winner = data.winner;
                    
                    if (data.winner === gameState.userSymbol) {
                        showStatus('🎉 Поздравляем! Вы выиграли!');
                    } else if (data.winner === gameState.aiSymbol) {
                        showStatus('😔 ИИ выиграл. Попробуйте еще раз!');
                    } else {
                        showStatus('🤝 Ничья!');
                    }
                    
                    setTimeout(() => {
                        console.log('🚨 ПРИНУДИТЕЛЬНЫЙ вызов showGameResultModal');
                        showGameResultModal(data.winner, {
                            move_count: gameState.moveCount
                        });
                    }, 1000);
                    return;
                }
                
                // Показываем ход ИИ, если он был сделан
                if (data.ai_move) {
                    const [aiRow, aiCol] = data.ai_move;
                    console.log(`🤖 ИИ сходил на [${aiRow}][${aiCol}]`);
                    highlightLastMove(aiRow, aiCol);
                    showStatus(`ИИ сходил на ${String.fromCharCode(65 + aiCol)}${aiRow + 1}. Ваш ход!`);
                } else {
                    showStatus('Ваш ход!');
                }
            }
            
            console.log('✅ Ход полностью обработан');
            
            // Проверяем целостность доски после хода
            setTimeout(() => validateBoardIntegrity(), 100);
        } else {
            // Если ошибка "Игра не инициализирована", пытаемся создать новую игру
            if (data.error && data.error.includes('не инициализирована')) {
                console.log('🔄 Пытаемся создать новую игру из-за ошибки инициализации...');
                await startNewGame(gameState.userSymbol);
                // Повторяем ход после создания игры
                setTimeout(() => handleCellClick(row, col), 500);
                return;
            }
            
            showStatus(`Ошибка хода: ${data.error}`);
            console.error('❌ Ошибка хода:', data);
        }
    } catch (error) {
        showStatus('Ошибка подключения к серверу');
        console.error('❌ Ошибка запроса:', error);
    }
}

function updateBoard(board) {
    console.log('🔄 === НАЧАЛО ОБНОВЛЕНИЯ ДОСКИ ===');
    console.log('📊 Получена доска для обновления:', board);
    
    // Проверяем валидность доски
    if (!board || !Array.isArray(board) || board.length !== 15) {
        console.error('❌ Невалидная доска получена от сервера:', board);
        return;
    }
    
    // ПРИНУДИТЕЛЬНО копируем доску, а не просто присваиваем ссылку
    gameState.board = [];
    for (let row = 0; row < 15; row++) {
        gameState.board[row] = [];
        for (let col = 0; col < 15; col++) {
            // Нормализуем значения: пустые клетки всегда '.'
            const cellValue = board[row][col];
            if (cellValue === 'X' || cellValue === 'O') {
                gameState.board[row][col] = cellValue;
            } else {
                gameState.board[row][col] = '.';
            }
        }
    }
    
    let changesCount = 0;
    
    // Обновляем только те клетки, которые действительно изменились
    for (let row = 0; row < 15; row++) {
        for (let col = 0; col < 15; col++) {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (!cell) {
                console.error(`❌ Не найдена клетка [${row}][${col}]`);
                continue;
            }
            
            const newValue = gameState.board[row][col];
            const currentValue = cell.textContent.trim();
            
            // Обновляем только если значение действительно изменилось
            if ((newValue === 'X' && currentValue !== 'X') || 
                (newValue === 'O' && currentValue !== 'O') || 
                (newValue === '.' && currentValue !== '')) {
                
                // Сначала очищаем клетку
                cell.textContent = '';
                cell.className = 'cell';
                cell.style.color = '';
                cell.style.backgroundColor = '';
                cell.style.fontWeight = '';
                
                if (newValue === 'X') {
                    cell.textContent = 'X';
                    cell.classList.add('x');
                    cell.style.color = '#e74c3c';
                    cell.style.backgroundColor = '#fadbd8';
                    cell.style.fontWeight = 'bold';
                    
                    changesCount++;
                    console.log(`✅ ИЗМЕНЕНИЕ: Установлен X в [${row}][${col}]`);
                } else if (newValue === 'O') {
                    cell.textContent = 'O';
                    cell.classList.add('o');
                    cell.style.color = '#3498db';
                    cell.style.backgroundColor = '#d6eaf8';
                    cell.style.fontWeight = 'bold';
                    
                    changesCount++;
                    console.log(`✅ ИЗМЕНЕНИЕ: Установлен O в [${row}][${col}]`);
                } else {
                    // Пустая клетка
                    changesCount++;
                    console.log(`🧹 ОЧИСТКА: Очищена клетка [${row}][${col}]`);
                }
            }
        }
    }
    
    console.log(`📈 Общее количество изменений: ${changesCount}`);
    console.log('🔄 === КОНЕЦ ОБНОВЛЕНИЯ ДОСКИ ===');
}

function updateGameInfo(data) {
    console.log('📝 Обновление информации об игре:', data);
    
    document.getElementById('current-player').textContent = data.current_player || gameState.currentPlayer;
    document.getElementById('move-count').textContent = data.move_count || gameState.moveCount || 0;
    document.getElementById('human-symbol').textContent = data.user_symbol || gameState.userSymbol;
    document.getElementById('ai-symbol').textContent = data.ai_symbol || gameState.aiSymbol;
    
    // Обновляем локальное состояние
    if (data.current_player) gameState.currentPlayer = data.current_player;
    if (data.move_count !== undefined) gameState.moveCount = data.move_count;
    if (data.user_symbol) gameState.userSymbol = data.user_symbol;
    if (data.ai_symbol) gameState.aiSymbol = data.ai_symbol;
    
    // КРИТИЧЕСКАЯ ПРОВЕРКА ЗАВЕРШЕНИЯ ИГРЫ В updateGameInfo
    if (data.game_over) {
        console.log('🚨 ОБНАРУЖЕНО ЗАВЕРШЕНИЕ ИГРЫ В updateGameInfo!');
        console.log('🚨 data.game_over =', data.game_over);
        console.log('🚨 data.winner =', data.winner);
        
        gameState.gameOver = true;
        gameState.winner = data.winner;
        
        // Принудительно показываем модальное окно
        setTimeout(() => {
            console.log('🚨 ПРИНУДИТЕЛЬНЫЙ показ модального окна из updateGameInfo');
            showGameResultModal(data.winner, {
                move_count: gameState.moveCount
            });
        }, 1000);
    }
}

function highlightLastMove(row, col) {
    console.log(`🔦 Подсветка последнего хода [${row}][${col}]`);
    
    // Убираем предыдущую подсветку
    document.querySelectorAll('.cell.last-move').forEach(cell => {
        cell.classList.remove('last-move');
    });
    
    // Добавляем подсветку к последнему ходу
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (cell) {
        cell.classList.add('last-move');
        console.log('✅ Подсветка добавлена');
    } else {
        console.error('❌ Клетка для подсветки не найдена');
    }
}

function showStatus(message) {
    console.log('📢 Статус:', message);
    document.getElementById('game-status').textContent = message;
}

async function fetchGameState() {
    console.log('🔄 Запрос актуального состояния игры с сервера...');
    
    try {
        const response = await fetch('/api/game_state', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        console.log('📦 Состояние игры с сервера:', data);
        
        if (data.success) {
            // Принудительно обновляем локальное состояние
            gameState.currentPlayer = data.current_player;
            gameState.userSymbol = data.user_symbol;
            gameState.aiSymbol = data.ai_symbol;
            gameState.moveCount = data.move_count || 0;
            gameState.gameOver = data.game_over || false;
            gameState.winner = data.winner || null;
            
            console.log('✅ Состояние синхронизировано с сервером');
            updateBoard(data.board);
            updateGameInfo(data);
        } else {
            console.error('❌ Ошибка получения состояния игры:', data.error);
        }
    } catch (error) {
        console.error('❌ Ошибка запроса состояния игры:', error);
    }
}

// Функция для проверки целостности доски
function validateBoardIntegrity() {
    console.log('🔍 Проверка целостности доски...');
    
    let totalPieces = 0;
    let xCount = 0;
    let oCount = 0;
    
    for (let row = 0; row < 15; row++) {
        for (let col = 0; col < 15; col++) {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (cell && cell.textContent.trim()) {
                totalPieces++;
                if (cell.textContent.trim() === 'X') xCount++;
                if (cell.textContent.trim() === 'O') oCount++;
            }
        }
    }
    
    console.log(`📊 Фигур на доске: всего=${totalPieces}, X=${xCount}, O=${oCount}`);
    
    // Если фигур меньше чем ожидается, синхронизируемся с сервером
    if (totalPieces < gameState.moveCount) {
        console.log('⚠️ Обнаружена потеря фигур, синхронизация с сервером...');
        fetchGameState();
    }
}

async function requestAIMove() {
    console.log('🤖 Запрос хода ИИ...');
    
    try {
        showStatus('ИИ думает...');
        showAIThinking(); // Показываем прогресс-бар
        
        const response = await fetch('/api/ai_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        console.log('🤖 Ответ ИИ:', data);
        
        hideAIThinking(); // Скрываем прогресс-бар
        
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
                
                // Показываем модальное окно результата с задержкой
                setTimeout(() => {
                    showGameResultModal(data.winner, {
                        move_count: gameState.moveCount
                    });
                }, 1000);
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
            
            console.log('✅ Ход ИИ обработан');
        } else {
            hideAIThinking(); // Скрываем прогресс-бар при ошибке
            showStatus(`Ошибка хода ИИ: ${data.error}`);
            console.error('❌ Ошибка хода ИИ:', data);
        }
    } catch (error) {
        hideAIThinking(); // Скрываем прогресс-бар при ошибке
        showStatus('Ошибка подключения к серверу');
        console.error('❌ Ошибка запроса хода ИИ:', error);
    }
}

console.log('✅ JavaScript файл полностью загружен');

// ========== ФУНКЦИИ ПРОГРЕСС-БАРА ИИ ==========

let aiThinkingInterval = null;
let aiThinkingProgress = 0;

function showAIThinking() {
    console.log('🤖 Показ прогресс-бара ИИ');
    
    const overlay = document.getElementById('ai-thinking-overlay');
    const progressBar = document.getElementById('ai-progress-bar');
    const message = document.getElementById('ai-thinking-message');
    
    // Сбрасываем прогресс
    aiThinkingProgress = 0;
    progressBar.style.width = '0%';
    
    // Показываем оверлей
    overlay.style.display = 'block';
    
    // Массив сообщений для разнообразия
    const messages = [
        'Анализирую возможные ходы...',
        'Оцениваю стратегические позиции...',
        'Ищу лучшие комбинации...',
        'Просчитываю варианты развития...',
        'Анализирую угрозы и возможности...',
        'Выбираю оптимальный ход...'
    ];
    
    let messageIndex = 0;
    
    // Запускаем анимацию прогресса
    aiThinkingInterval = setInterval(() => {
        aiThinkingProgress += Math.random() * 15 + 5; // Случайный прирост 5-20%
        
        if (aiThinkingProgress > 95) {
            aiThinkingProgress = 95; // Не доходим до 100% пока не получим ответ
        }
        
        progressBar.style.width = aiThinkingProgress + '%';
        
        // Меняем сообщение каждые 1.5 секунды
        if (Math.random() < 0.3) {
            messageIndex = (messageIndex + 1) % messages.length;
            message.textContent = messages[messageIndex];
        }
    }, 200);
    
    console.log('✅ Прогресс-бар ИИ показан');
}

function hideAIThinking() {
    console.log('❌ Скрытие прогресс-бара ИИ');
    
    const overlay = document.getElementById('ai-thinking-overlay');
    const progressBar = document.getElementById('ai-progress-bar');
    
    // Завершаем прогресс до 100%
    progressBar.style.width = '100%';
    
    // Останавливаем интервал
    if (aiThinkingInterval) {
        clearInterval(aiThinkingInterval);
        aiThinkingInterval = null;
    }
    
    // Скрываем с небольшой задержкой для плавности
    setTimeout(() => {
        overlay.style.display = 'none';
        aiThinkingProgress = 0;
    }, 300);
    
    console.log('✅ Прогресс-бар ИИ скрыт');
}

// ========== ФУНКЦИИ МОДАЛЬНОГО ОКНА РЕЗУЛЬТАТА ИГРЫ ==========

function showGameResultModal(winner, gameData = {}) {
    console.log('🏆 ВЫЗВАНА ФУНКЦИЯ showGameResultModal!');
    console.log('🏆 Параметры:', { winner, gameData });
    console.log('🏆 Текущее состояние игры:', gameState);
    
    const modal = document.getElementById('game-result-modal');
    console.log('🏆 Найден элемент modal:', modal);
    
    if (!modal) {
        console.error('❌ КРИТИЧЕСКАЯ ОШИБКА: Модальное окно не найдено в DOM!');
        console.log('🔍 Все элементы с id в документе:');
        const allElementsWithId = document.querySelectorAll('[id]');
        allElementsWithId.forEach(el => console.log(`  - ${el.id}: ${el.tagName}`));
        return;
    }
    
    const modalContent = document.getElementById('modal-content');
    const resultIcon = document.getElementById('result-icon');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    
    console.log('🏆 Элементы модального окна:', {
        modalContent: !!modalContent,
        resultIcon: !!resultIcon,
        resultTitle: !!resultTitle,
        resultMessage: !!resultMessage
    });
    
    if (!modalContent || !resultIcon || !resultTitle || !resultMessage) {
        console.error('❌ ОШИБКА: Не все элементы модального окна найдены!');
        return;
    }
    
    // Очищаем предыдущие классы
    modalContent.className = 'modal-content';
    
    if (winner === 'draw') {
        // Ничья
        modalContent.classList.add('draw');
        resultIcon.textContent = '🤝';
        resultTitle.textContent = 'Ничья!';
        resultMessage.textContent = 'Отличная игра! Никто не смог одержать победу.';
    } else if (winner === gameState.userSymbol) {
        // Победа игрока
        modalContent.classList.add(`winner-${winner.toLowerCase()}`);
        resultIcon.textContent = winner === 'X' ? '❌' : '⭕';
        resultTitle.textContent = 'Поздравляем!';
        resultMessage.textContent = `Вы выиграли играя за ${winner}! Отличная стратегия!`;
    } else if (winner === gameState.aiSymbol) {
        // Победа ИИ
        modalContent.classList.add(`winner-${winner.toLowerCase()}`);
        resultIcon.textContent = winner === 'X' ? '❌' : '⭕';
        resultTitle.textContent = 'ИИ победил';
        resultMessage.textContent = `ИИ выиграл играя за ${winner}. Попробуйте еще раз!`;
    } else {
        // Общий случай
        modalContent.classList.add(`winner-${winner.toLowerCase()}`);
        resultIcon.textContent = '🏆';
        resultTitle.textContent = 'Игра окончена!';
        resultMessage.textContent = `Победил ${winner}!`;
    }
    
    // Добавляем информацию о количестве ходов
    if (gameData.move_count) {
        resultMessage.textContent += ` Игра длилась ${gameData.move_count} ходов.`;
    }
    
    // Показываем модальное окно
    console.log('🏆 Устанавливаем display: block для модального окна');
    modal.style.display = 'block';
    console.log('🏆 Стиль display установлен:', modal.style.display);
    
    // Дополнительная проверка CSS
    const computedStyle = window.getComputedStyle(modal);
    console.log('🏆 Computed display:', computedStyle.display);
    console.log('🏆 Computed visibility:', computedStyle.visibility);
    console.log('🏆 Computed z-index:', computedStyle.zIndex);
    console.log('🏆 Computed position:', computedStyle.position);
    
    // Принудительно устанавливаем стили
    modal.style.position = 'fixed';
    modal.style.zIndex = '9999';
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
    
    console.log('🏆 Принудительно установлены стили для модального окна');
    
    // Добавляем обработчик клика вне модального окна для закрытия
    modal.onclick = function(event) {
        if (event.target === modal) {
            closeGameResultModal();
        }
    };
    
    // Добавляем обработчик клавиши Escape
    document.addEventListener('keydown', handleEscapeKey);
    
    console.log('✅ МОДАЛЬНОЕ ОКНО РЕЗУЛЬТАТА ДОЛЖНО БЫТЬ ПОКАЗАНО!');
    console.log('✅ Финальная проверка modal.style.display:', modal.style.display);
    
    // Альтернативный способ показа результата, если модальное окно не работает
    setTimeout(() => {
        const computedStyle = window.getComputedStyle(modal);
        console.log('🔍 Проверка через 500мс - modal display:', computedStyle.display);
        console.log('🔍 Проверка через 500мс - modal visibility:', computedStyle.visibility);
        
        if (computedStyle.display === 'none' || computedStyle.visibility === 'hidden') {
            console.warn('⚠️ МОДАЛЬНОЕ ОКНО НЕ ОТОБРАЖАЕТСЯ! Показываем alert');
            let message = '';
            if (winner === 'draw') {
                message = '🤝 Ничья! Отличная игра!';
            } else if (winner === gameState.userSymbol) {
                message = `🎉 Поздравляем! Вы выиграли играя за ${winner}!`;
            } else if (winner === gameState.aiSymbol) {
                message = `😔 ИИ выиграл играя за ${winner}. Попробуйте еще раз!`;
            } else {
                message = `🏆 Игра окончена! Победил ${winner}!`;
            }
            
            if (gameData.move_count) {
                message += ` Игра длилась ${gameData.move_count} ходов.`;
            }
            
            alert(message);
        }
    }, 500);
}

function closeGameResultModal() {
    console.log('❌ Закрытие модального окна результата игры');
    
    const modal = document.getElementById('game-result-modal');
    modal.style.display = 'none';
    
    // Убираем обработчик клавиши Escape
    document.removeEventListener('keydown', handleEscapeKey);
    
    console.log('✅ Модальное окно результата закрыто');
}

function handleEscapeKey(event) {
    if (event.key === 'Escape') {
        closeGameResultModal();
    }
}

async function startNewGameFromModal() {
    console.log('🎮 Запуск новой игры из модального окна');
    
    // Закрываем модальное окно
    closeGameResultModal();
    
    // Запускаем новую игру с текущим выбранным символом
    if (gameState.userSymbol) {
        await startNewGame(gameState.userSymbol);
    } else {
        // Если символ не выбран, показываем выбор
        showSymbolChoice();
        showStatus('Выберите символ для новой игры!');
    }
}

// ========== ФУНКЦИИ МОДАЛЬНОГО ОКНА ЗАВЕРШЕНЫ ==========

console.log('✅ Функции модального окна результата игры загружены');

// ========== ФУНКЦИЯ ДЛЯ ТЕСТИРОВАНИЯ МОДАЛЬНОГО ОКНА ==========

// Функция для тестирования модального окна из консоли браузера
window.testModal = function(winner = 'X') {
    console.log('🧪 ТЕСТИРОВАНИЕ МОДАЛЬНОГО ОКНА');
    showGameResultModal(winner, { move_count: 10 });
};

console.log('🧪 Добавлена функция window.testModal() для тестирования');
console.log('🧪 Используйте testModal("X") или testModal("O") в консоли браузера'); 