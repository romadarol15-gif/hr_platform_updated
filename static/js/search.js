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
            // Правильный URL согласно urls.py: path('search/', ...)
            fetch(`/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.results && data.results.length > 0) {
                        displayResults(data.results);
                    } else {
                        searchResults.innerHTML = '<div class="search-no-results">Ничего не найдено</div>';
                        searchResults.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Ошибка поиска:', error);
                    searchResults.innerHTML = '<div class="search-error">Ошибка поиска</div>';
                    searchResults.style.display = 'block';
                });
        }, 300);
    });
    
    // Отображение результатов
    function displayResults(results) {
        let html = '';
        results.forEach(result => {
            html += `
                <a href="/profile/${result.id}/" class="search-result-item">
                    <div class="search-result-name">${result.full_name}</div>
                    <div class="search-result-info">
                        <span class="search-result-position">${result.position}</span>
                        <span class="search-result-username">№${result.username}</span>
                    </div>
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
