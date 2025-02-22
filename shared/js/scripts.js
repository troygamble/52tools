document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;
    const navContainers = document.querySelectorAll('.nav-links');
    const dropBtn = document.querySelector('.dropbtn');

    // ✅ Apply saved theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
    }

    // ✅ Toggle dark mode and persist setting
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const newTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
    });

    // ✅ Dynamic navigation loading
    fetch('/tools/tools_list.json')
        .then(response => response.json())
        .then(data => {
            navContainers.forEach(navContainer => {
                data.tools.forEach(tool => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="/tools/${tool.slug}/index.html">${tool.name}</a>`;
                    navContainer.appendChild(li);
                });
            });
        });

    // ✅ Dropdown toggle for "All Tools"
    dropBtn?.addEventListener('click', () => {
        document.querySelector('.dropdown-content').classList.toggle('show');
    });

    // ✅ Close dropdown when clicking outside
    window.addEventListener('click', (e) => {
        if (!dropBtn.contains(e.target)) {
            document.querySelector('.dropdown-content').classList.remove('show');
        }
    });
});
