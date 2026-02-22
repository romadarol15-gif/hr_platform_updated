// Поиск сотрудников в реальном времени
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('employee-search');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) {
        return; // Нет полей поиска на странице
    }
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Очистка предыдущего таймаута
        clearTimeout(searchTimeout);
        
        // Если менее 2 символов - скрываем результаты
        if (query.length < 2) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }
        
        // Задержка 300мс перед поиском
        searchTimeout = setTimeout(() => {
            fetch(`/employee-search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.results && data.results.length > 0) {
                        displayResults(data.results);
                    } else {
                        searchResults.innerHTML = '<div style="padding: 1rem; color: #6b7280;">Ничего не найдено</div>';
                        searchResults.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Ошибка поиска:', error);
                    searchResults.innerHTML = '<div style="padding: 1rem; color: #ef4444;">Ошибка поиска</div>';
                    searchResults.style.display = 'block';
                });
        }, 300);
    });
    
    // Отображение результатов (правильная разметка)
    function displayResults(results) {
        let html = '';
        results.forEach(result => {
            html += `
                <a href="/profile/${result.id}/" class="search-result-item" style="display: block; text-decoration: none; color: inherit;">
                    <strong style="color: #111827;">${result.full_name}</strong>
                    <small style="color: #6b7280; display: block; margin-top: 0.25rem;">${result.position} • №${result.username}</small>
                </a>
            `;
        });
        searchResults.innerHTML = html;
        searchResults.style.display = 'block';
    }
    
    // Закрытие результатов при клике вне поиска
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
    
    // Показ результатов при фокусе
    searchInput.addEventListener('focus', function() {
        if (searchResults.innerHTML && this.value.trim().length >= 2) {
            searchResults.style.display = 'block';
        }
    });
});
