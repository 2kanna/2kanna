
async function checkAuth() {
    const token = localStorage.getItem('token');

    if (token) {
        const response = await fetch(`${API_URL}/user/me`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        const user = await response.json();

        document.querySelector('.logout').style.display = 'block';
        document.querySelector('.username').textContent = user.username;
        document.querySelector('.user-form-container').style.display = 'none';
        // document.querySelector('.login-form').style.display = 'none';
        // document.querySelector('.register-form').style.display = 'none';
    } else {
        // document.querySelector('.user-form-container').style.display = 'flex';
        // document.querySelector('.login-form').style.display = 'block';
        // document.querySelector('.register-form').style.display = 'block';
        document.querySelector('.logout').style.display = 'none';
        document.querySelector('.username').textContent = '';
    }
}

checkAuth();

document.querySelector('.logout').addEventListener('click', (event) => {
    localStorage.removeItem('token');
    // reload the page
    window.location.reload();
});


document.querySelector('.login').addEventListener('click', (event) => {
    // check textContent of the button
    if (event.target.textContent === 'Hide') {
        // hide user login/register forms
        document.querySelector('.user-form-container').style.display = 'none';

        // change text of the button to "Login"
        event.target.textContent = 'Login';
        return;
    }

    // show user login/register forms
    document.querySelector('.user-form-container').style.display = 'flex';

    // change text of the button to "Hide"
    event.target.textContent = 'Hide';
});


const registerForm = document.querySelector('.register-form');
registerForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = registerForm.querySelector('input[name="username"]').value;
    const password = registerForm.querySelector('input[name="password"]').value;

    const data = { username, plaintext_password: password };

    const response = await fetch(`${API_URL}/user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const { jwt: { access_token } } = await response.json();
    localStorage.setItem('token', access_token);

    // reload the page
    window.location.reload();
});

const loginForm = document.querySelector('.login-form');
loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = loginForm.querySelector('input[name="username"]').value;
    const password = loginForm.querySelector('input[name="password"]').value;

    const response = await fetch(`${API_URL}/user/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password })
    });

    if (response.status === 401) {
        throw new Error('Invalid credentials');
    }

    const { access_token } = await response.json();
    localStorage.setItem('token', access_token);
    // reload the page
    window.location.reload();
});