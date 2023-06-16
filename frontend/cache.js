const boardList = localStorage.getItem('boardList');
if (boardList) {
    // If there is a cached board list, show it
    const boards = JSON.parse(boardList);
    boards.forEach(board => {
        const board_span = document.createElement('span');
        const board_link = document.createElement('a');
        board_link.href = `?board=${board.name}`;
        board_link.textContent = board.name;

        board_span.innerHTML = '[';
        board_span.appendChild(board_link);
        board_span.innerHTML += ']';

        document.querySelector('.board-list').appendChild(board_span);
    });
}