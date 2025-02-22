document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;
    const navContainers = document.querySelectorAll('.nav-links');
    const dropBtn = document.querySelector('.dropbtn');
    const toolsContainer = document.getElementById('tools-container');

    // ✅ Theme toggling with persistence
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') body.classList.add('dark-mode');
    themeToggle?.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    // ✅ Dynamic navigation & tool card generation
    fetch('/tools/tools_list.json')
        .then(response => response.json())
        .then(data => {
            // 🔗 Load navigation
            navContainers.forEach(navContainer => {
                data.tools.forEach(tool => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="/tools/${tool.slug}/index.html">${tool.name}</a>`;
                    navContainer.appendChild(li);
                });
            });

            // 🏗️ Load homepage grid with descriptions
            if (toolsContainer) {
                data.tools.forEach(tool => {
                    const description = tool.description || 'A powerful online tool designed for productivity and efficiency.';
                    const toolCard = document.createElement('div');
                    toolCard.className = 'tool-card';
                    toolCard.innerHTML = `
                        <a href="/tools/${tool.slug}/index.html" class="tool-link">
                            <h3>${tool.name}</h3>
                            <p>${description}</p>
                        </a>`;
                    toolsContainer.appendChild(toolCard);
                });
            }
        })
        .catch(error => console.error('❌ Navigation load error:', error));

    // ✅ Dropdown toggle
    dropBtn?.addEventListener('click', () => {
        document.querySelector('.dropdown-content').classList.toggle('show');
    });

    window.addEventListener('click', (e) => {
        if (!dropBtn.contains(e.target)) {
            document.querySelector('.dropdown-content').classList.remove('show');
        }
    });
});
