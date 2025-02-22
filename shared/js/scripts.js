document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;
    const navContainers = document.querySelectorAll('.nav-links'); // Handles navbar & sidebar nav
    const dropBtn = document.querySelector('.dropbtn');
    const toolsContainer = document.getElementById('tools-container'); // Only on homepage

    // ✅ Apply saved theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
    }

    // ✅ Theme toggle and persistence
    themeToggle?.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const newTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
    });

    // ✅ Dynamic navigation loading + homepage grid generation
    fetch('/tools/tools_list.json')
        .then(response => response.json())
        .then(data => {
            // 🔗 Populate navigation (dropdown + sidebar)
            navContainers.forEach(navContainer => {
                data.tools.forEach(tool => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="/tools/${tool.slug}/index.html">${tool.name}</a>`;
                    navContainer.appendChild(li);
                });
            });

            // 🏗️ Populate homepage tools grid if on the homepage
            if (toolsContainer) {
                data.tools.forEach(tool => {
                    const toolCard = document.createElement('div');
                    toolCard.className = 'tool-card';
                    toolCard.innerHTML = `
                        <h3>${tool.name}</h3>
                        <p>${tool.description || 'No description available.'}</p>
                        <a href="/tools/${tool.slug}/index.html">Try Tool →</a>`;
                    toolsContainer.appendChild(toolCard);
                });
            }
        })
        .catch(error => console.error('❌ Navigation load error:', error));

    // ✅ Dropdown toggle behavior
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
