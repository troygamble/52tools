document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;
    const navContainers = document.querySelectorAll('.nav-links'); // Handle multiple navs (top & sidebar)
    const dropBtn = document.querySelector('.dropbtn');

    // ✅ Theme toggling with localStorage persistence
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
    }

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    // ✅ Dynamic navigation loading (dropdown & sidebar)
    fetch('/tools/tools_list.json')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load navigation data.');
            return response.json();
        })
        .then(data => {
            navContainers.forEach(navContainer => {
                data.tools.forEach(tool => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="/tools/${tool.slug}/index.html">${tool.name}</a>`;
                    navContainer.appendChild(li);
                });
            });
        })
        .catch(error => console.error('❌ Navigation load error:', error));

    // ✅ Dropdown toggle for "All Tools"
    dropBtn?.addEventListener('click', () => {
        const dropdownContent = document.querySelector('.dropdown-content');
        dropdownContent.classList.toggle('show');
    });

    // ✅ Close dropdown when clicking outside
    window.addEventListener('click', (e) => {
        if (!dropBtn.contains(e.target)) {
            document.querySelector('.dropdown-content').classList.remove('show');
        }
    });
});
