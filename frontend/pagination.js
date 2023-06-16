const paginationContainer = document.getElementById('pagination-container');
const urlParams = new URLSearchParams(window.location.search);
const board = urlParams.get('board');
const post = urlParams.get('post');


let page;

if (!urlParams.get('page')) {
    page = 1;
} else {
    page = urlParams.get('page');
}


fetch(`${API_URL}/board/tech/posts/pagecount`, {
    method: 'GET',
    headers: {
        'accept': 'application/json'
    }
})
    .then(response => response.json())
    .then(pageCount => {
        // Build pagination DOM element
        for (let i = 1; i <= pageCount; i++) {
            const pageElement = document.createElement('span');
            // double equals because page is a string
            if (i == page) {
                pageElement.textContent = i;
            } else {
                const pageLinkElement = document.createElement('a');
                pageLinkElement.href = `?board=${board}&page=${i}`;
                pageLinkElement.textContent = i;
                pageElement.appendChild(pageLinkElement);
            }
            paginationContainer.innerHTML += '[ ';
            paginationContainer.appendChild(pageElement);
            paginationContainer.innerHTML += ' ]';
        }
    })
    .catch(error => console.error(error));