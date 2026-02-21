document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие уведомлений через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Блокировка повторной отправки форм
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                const originalText = submitBtn.textContent;
                submitBtn.textContent = '⏳ Загрузка...';

                // Восстанавливаем кнопку через 10 секунд на случай ошибки
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }, 10000);
            }
        });
    });

    // Поиск сотрудников
    const searchInput = document.getElementById('employee-search');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            const query = this.value.trim();

            // Очищаем предыдущий таймер
            clearTimeout(searchTimeout);

            if (query.length < 2) {
                searchResults.classList.remove('active');
                searchResults.innerHTML = '';
                return;
            }

            // Задержка перед поиском (debounce)
            searchTimeout = setTimeout(() => {
                fetch(`/search/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            searchResults.innerHTML = '';
                            data.results.forEach(employee => {
                                const item = document.createElement('div');
                                item.className = 'search-result-item';
                                item.innerHTML = `
                                    <strong>${employee.full_name}</strong>
                                    <small>№${employee.username} · ${employee.position}</small>
                                `;
                                item.addEventListener('click', () => {
                                    window.location.href = `/profile/${employee.id}/`;
                                });
                                searchResults.appendChild(item);
                            });
                            searchResults.classList.add('active');
                        } else {
                            searchResults.innerHTML = '<div class="search-result-item"><small>Ничего не найдено</small></div>';
                            searchResults.classList.add('active');
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка поиска:', error);
                        searchResults.classList.remove('active');
                    });
            }, 300);
        });

        // Закрытие результатов при клике вне области поиска
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('active');
            }
        });

        // Показываем результаты при фокусе, если есть текст
        searchInput.addEventListener('focus', function() {
            if (this.value.trim().length >= 2 && searchResults.children.length > 0) {
                searchResults.classList.add('active');
            }
        });
    }

    // Предпросмотр загружаемых изображений (аватарка)
    const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const existingAvatar = document.querySelector('.profile-avatar, .profile-avatar-placeholder');
                    if (existingAvatar) {
                        if (existingAvatar.tagName === 'IMG') {
                            existingAvatar.src = event.target.result;
                        } else {
                            const img = document.createElement('img');
                            img.src = event.target.result;
                            img.className = 'profile-avatar';
                            existingAvatar.replaceWith(img);
                        }
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    console.log('HR Platform v2.0 initialized');
});
