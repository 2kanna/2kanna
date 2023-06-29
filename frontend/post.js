
function formatPostMessage(message) {
    const backtickRegex = /```([\s\S]*?)```/g;
    message = message.replace(backtickRegex, (match, p1) => `<pre>${p1}</pre>`);

    const formattedLines = message.split('\n').map(line => {
        if (line.startsWith('&gt;')) {
            const quoteRegex = /^&gt;&gt;(\d+)/;
            const match = line.match(quoteRegex);
            if (match) {
                const quoteNumber = match[1];
                return `<span class="quote"><a href="#post-${quoteNumber}">${line}</a></span>`;
            }
            return `<span class="quote">${line}</span>`;
        }
        return line;
    }).join('<br>');

    const linkRegex = /https?:\/\/[^\s]+$/;
    const formattedMessageWithLinks = formattedLines.replace(linkRegex, link => `<a href="${link}">${link}</a>`);

    return formattedMessageWithLinks;
}


function createPost(post) {
    const template = document.querySelector('#post');
    const clone = template.content.cloneNode(true);

    const post_message = formatPostMessage(post.message);

    // post.date is in the format "2023-05-26 21:50:55.979636"
    // remove the microseconds
    const post_date = post.date.split('.')[0];

    clone.querySelector('.post-title').textContent = post.title;
    clone.querySelector('.post-date').textContent = post_date;
    clone.querySelector('.post-id a').textContent = post.post_id;
    clone.querySelector('.post-message').innerHTML = post_message;
    // set href to /board/{board}/posts/{post.post_id}
    clone.querySelector('.reply-button a').href = `?board=${board}&post=${post.post_id}`;

    // add event listener to reply button if its a child post
    if (post.parent_id) {
        clone.querySelector('.reply-button').addEventListener('click', function (event) {
            event.preventDefault();
            // append post_id to the post-form textarea
            const textarea = document.querySelector('.new-post textarea[name="message"]');
            textarea.value += `>>${post.post_id}\n`;
            textarea.focus();
        });
    }
    if ("children" in post && post.children.length > 0) {
        // set the post-count to number of children
        clone.querySelector('.post-count').textContent = `(${post.children.length} replies)`;
    }

    if (post.file) {
        const file = post.file;
        const file_source = `/uploads/${file.file_name}`;

        if (file.content_type.startsWith('image/')) {
            const fileTemplate = document.querySelector('#file-image');
            const fileClone = fileTemplate.content.cloneNode(true);

            fileClone.querySelector('.post-image').src = file_source;
            fileClone.querySelector('.post-image').classList.add('post-image');
            // add click event listener to open image in new tab
            fileClone.querySelector('.post-file-link').href = file_source;
            fileClone.querySelector('.post-file-link').addEventListener('click', function (event) {
                event.preventDefault();
                // add class to image to make it full size
                event.currentTarget.querySelector('.post-image').classList.toggle('full-size');
                event.currentTarget.parentNode.parentNode.classList.toggle('flex-wrap-wrap');
            });
            clone.querySelector('.post-file').appendChild(fileClone);
        } else {
            const fileTemplate = document.querySelector('#file-other');
            const fileClone = fileTemplate.content.cloneNode(true);

            fileClone.querySelector('.post-file-link').href = file_source;
            fileClone.querySelector('.post-file').textContent = `upload:[${file.file_name}]`;
            clone.querySelector('.post-file').appendChild(fileClone);
        }

    }
    return clone;
}


export function renderPosts(posts) {
    const container = document.querySelector('.posts-container');

    posts.forEach(post => {
        let clone;
        if ("children" in post) {
            clone = createPost(post);
        } else {
            clone = container.querySelector('.post');

            const child_clone = createPost(post);
            child_clone.querySelector('.post').classList.add('child');
            clone.querySelector('.children').appendChild(child_clone);

            return;
        }

        // children or new replies
        if (post.children.length > 0) {
            post.children.forEach(child => {
                const child_clone = createPost(child);
                child_clone.querySelector('.post').classList.add('child');
                clone.querySelector('.children').appendChild(child_clone);
            });
        }

        container.appendChild(clone);
    });
}
