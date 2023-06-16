
import { renderPosts } from './post.js';

const urlParams = new URLSearchParams(window.location.search);
const board = urlParams.get('board');
const post = urlParams.get('post');

if (!board) {
    console.log("No board specified");
} else if (!post) {
    fetch(`${API_URL}/board/${board}/posts?page=${page}`)
        .then(response => response.json())
        .then(posts => renderPosts(posts));
} else {
    fetch(`${API_URL}/post/${post}`)
        .then(response => response.json())
        .then(post => {
            renderPosts([post]);
            document.querySelector('.new-post input[name="parent_id"]').value = post.post_id;
        });
}


// Fetch the board list from the API and update the cached list
fetch(`${API_URL}/board`)
    .then(function (response) {
        return response.json();
    })
    .then(function (boards) {
        // Update the cached board list
        localStorage.setItem('boardList', JSON.stringify(boards));

        // Clear the board list and add links to the `board-list` div
        document.querySelector('.board-list').innerHTML = '';
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
    });

const form = document.querySelector('.new-post .post-form');
form.addEventListener('submit', async event => {
    event.preventDefault();

    const { value: title } = document.querySelector('.new-post input[name="title"]');
    const { value: message } = document.querySelector('.new-post textarea[name="message"]');
    const { value: fileId } = document.querySelector('.new-post input[name="file_id"]');
    const { value: parentId } = document.querySelector('.new-post input[name="parent_id"]');

    const data = {
        board_name: board,
        title,
        message,
        ...(fileId && { file_id: fileId }),
        ...(parentId && { parent_id: parentId }),
    };

    const headers = {
        'Content-Type': 'application/json',
        ...(localStorage.getItem('token') && { Authorization: `Bearer ${localStorage.getItem('token')}` }),
    };

    const response = await fetch(`${API_URL}/post`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
    })

    if (!response.ok) {
        if (response.status === 403) {
            // Handle 403 error
            console.log('Access denied', await response.json());
        } else {
            // Handle other errors
            console.error(response);
        }
        return;
    }

    const post = await response.json();
    window.location.href = `?board=${board}&post=${post.post_id}`;
});

// event listener on the remove file button
document.querySelector('.new-post .remove-file').addEventListener('click', function (event) {
    event.preventDefault();
    document.querySelector('.new-post input[name="file_id"]').value = '';
    document.querySelector('.new-post .remove-file').classList.add('hidden');
    document.querySelector('.new-post .upload-form .spinner').classList.add('hidden');
    document.querySelector('.new-post input[name="file"]').value = '';
    document.querySelector('.new-post .upload-form').classList.remove('hidden');
});

async function uploadFile() {
    const uploadForm = document.querySelector('.new-post .upload-form');
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        console.log('uploading file');

        // show a spinner
        document.querySelector('.new-post .upload-form .spinner').classList.remove('hidden');

        const formData = new FormData(uploadForm);

        const response = await fetch(`${API_URL}/post/upload`, {
            method: 'POST',
            body: formData
        });

        const { file_id } = await response.json();

        document.querySelector('.new-post input[name="file_id"]').value = file_id;

        // hide the upload form
        document.querySelector('.new-post .upload-form').classList.add('hidden');

        // show a "remove file" button
        document.querySelector('.new-post .remove-file').classList.remove('hidden');
    });
}

uploadFile();