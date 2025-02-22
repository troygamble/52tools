document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;
    const navContainer = document.querySelector('.nav-links');

    // ✅ Theme toggling with localStorage persistence
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
    }

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    // ✅ Dynamic navigation loading
    fetch('/tools/tools_list.json');
        .then(response => {
            if (!response.ok) throw new Error('Failed to load navigation data.');
            return response.json();
        })
        .then(data => {
            data.tools.forEach(tool => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="/tools/${tool.slug}/index.html">${tool.name}</a>`;
                navContainer.appendChild(li);
            });
        })
        .catch(error => console.error('❌ Navigation load error:', error));

    // ✅ Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    navToggle.addEventListener('change', () => {
        if (navToggle.checked) {
            navContainer.style.display = 'flex';
        } else {
            navContainer.style.display = 'none';
        }
    });
});
