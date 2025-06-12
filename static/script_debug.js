// Очень простая версия для отладки
console.log('🚀 Простая версия JavaScript загружена');

let simpleGameState = {
    board: [],
    userSymbol: 'X'
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM загружен');
    createGameBoard();
    initSimpleBoard();
    addClickHandlers();
});

function createGameBoard() {
    console.log('🎯 Создание игровой доски');
    
    const gameBoard = document.getElementById('game-board');
    if (!gameBoard) {
        console.error('❌ Элемент game-board не найден!');
        return;
    }
    
    // Очищаем доску
    gameBoard.innerHTML = '';
    
    // Создаем сетку 15x15
    for (let row = 0; row < 15; row++) {
        for (let col = 0; col < 15; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            gameBoard.appendChild(cell);
        }
    }
    
    console.log('✅ Доска создана: 225 клеток');
}

function initSimpleBoard() {
    console.log('🎯 Инициализация простой доски');
    
    // Создаём пустую доску в памяти
    simpleGameState.board = [];
    for (let row = 0; row < 15; row++) {
        simpleGameState.board[row] = [];
        for (let col = 0; col < 15; col++) {
            simpleGameState.board[row][col] = '.';
        }
    }
    
    console.log('✅ Доска инициализирована:', simpleGameState.board);
}

function addClickHandlers() {
    console.log('🎯 Добавление обработчиков кликов');
    
    const cells = document.querySelectorAll('.cell');
    console.log(`📊 Найдено ${cells.length} клеток`);
    
    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        cell.addEventListener('click', function() {
            console.log(`🎯 КЛИК по клетке [${row}][${col}]`);
            testCellUpdate(row, col);
        });
    });
}

function testCellUpdate(row, col) {
    console.log(`🧪 Тестовое обновление клетки [${row}][${col}]`);
    
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (!cell) {
        console.error(`❌ Клетка [${row}][${col}] не найдена!`);
        return;
    }
    
    // Принудительно ставим X
    cell.textContent = 'X';
    cell.style.color = '#e74c3c';
    cell.style.backgroundColor = '#fadbd8';
    cell.style.fontWeight = 'bold';
    
    console.log(`✅ Поставлен X в клетку [${row}][${col}]`);
    console.log(`📊 Текущее содержимое клетки: "${cell.textContent}"`);
    console.log(`📊 Стили клетки:`, cell.style.cssText);
    
    // Обновляем локальное состояние
    simpleGameState.board[row][col] = 'X';
}

// Тестовая функция для консоли
function testAllCells() {
    console.log('🧪 Тестирование всех клеток');
    
    // Ставим несколько тестовых X и O
    const testMoves = [
        {row: 7, col: 7, symbol: 'X'},
        {row: 7, col: 8, symbol: 'O'},
        {row: 8, col: 7, symbol: 'X'},
        {row: 8, col: 8, symbol: 'O'}
    ];
    
    testMoves.forEach(move => {
        const cell = document.querySelector(`[data-row="${move.row}"][data-col="${move.col}"]`);
        if (cell) {
            cell.textContent = move.symbol;
            cell.style.color = move.symbol === 'X' ? '#e74c3c' : '#3498db';
            cell.style.backgroundColor = move.symbol === 'X' ? '#fadbd8' : '#d6eaf8';
            cell.style.fontWeight = 'bold';
            console.log(`✅ Поставлен ${move.symbol} в [${move.row}][${move.col}]`);
        }
    });
}

// Экспортируем в глобальную область для тестирования
window.testAllCells = testAllCells;
window.testCellUpdate = testCellUpdate;

console.log('✅ Простая версия JavaScript готова к работе'); 