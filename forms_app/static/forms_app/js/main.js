/**
 * Основной JavaScript файл для Forms App
 * Содержит функциональность для Ajax форм, валидации и улучшения UX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов при загрузке страницы
    initializeAjaxForms();
    initializeFormValidation();
    initializeCharacterCounters();
    initializeTooltips();
    initializeAlerts();
    
    console.log('Forms App JavaScript инициализирован');
});

/**
 * Инициализация Ajax обработки форм
 */
function initializeAjaxForms() {
    const ajaxForms = document.querySelectorAll('.ajax-form');
    
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleAjaxSubmit(this);
        });
    });
}

/**
 * Обработка Ajax отправки формы
 * @param {HTMLFormElement} form - Форма для отправки
 */
function handleAjaxSubmit(form) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    const method = form.method || 'POST';
    
    // Показываем индикатор загрузки
    showLoadingState(form);
    
    // Получаем CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Отправляем Ajax запрос
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingState(form);
        
        if (data.success) {
            // Успешная отправка
            showAlert('success', data.message || 'Форма успешно отправлена!');
            form.reset();
            clearFormErrors(form);
        } else {
            // Ошибки валидации
            showFormErrors(form, data.errors || {});
            showAlert('error', data.message || 'Ошибка при отправке формы');
        }
    })
    .catch(error => {
        hideLoadingState(form);
        console.error('Ajax ошибка:', error);
        showAlert('error', 'Произошла ошибка при отправке. Попробуйте еще раз.');
    });
}

/**
 * Показать состояние загрузки для формы
 * @param {HTMLFormElement} form - Форма
 */
function showLoadingState(form) {
    form.classList.add('loading');
    
    // Создаем overlay с спиннером
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
        </div>
    `;
    
    form.style.position = 'relative';
    form.appendChild(overlay);
    
    // Отключаем все элементы формы
    const inputs = form.querySelectorAll('input, textarea, select, button');
    inputs.forEach(input => input.disabled = true);
}

/**
 * Скрыть состояние загрузки для формы
 * @param {HTMLFormElement} form - Форма
 */
function hideLoadingState(form) {
    form.classList.remove('loading');
    
    // Удаляем overlay
    const overlay = form.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
    
    // Включаем все элементы формы
    const inputs = form.querySelectorAll('input, textarea, select, button');
    inputs.forEach(input => input.disabled = false);
}

/**
 * Показать ошибки валидации в форме
 * @param {HTMLFormElement} form - Форма
 * @param {Object} errors - Объект с ошибками
 */
function showFormErrors(form, errors) {
    // Сначала очищаем все предыдущие ошибки
    clearFormErrors(form);
    
    // Отображаем новые ошибки
    Object.keys(errors).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const errorMessages = Array.isArray(errors[fieldName]) 
                ? errors[fieldName] 
                : [errors[fieldName]];
            
            // Добавляем класс ошибки к полю
            field.classList.add('is-invalid');
            
            // Создаем элемент с текстом ошибки
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.innerHTML = errorMessages.join('<br>');
            
            // Вставляем ошибку после поля
            field.parentNode.appendChild(errorDiv);
        }
    });
}

/**
 * Очистить все ошибки валидации в форме
 * @param {HTMLFormElement} form - Форма
 */
function clearFormErrors(form) {
    // Удаляем классы ошибок
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => field.classList.remove('is-invalid'));
    
    // Удаляем сообщения об ошибках
    const errorMessages = form.querySelectorAll('.invalid-feedback');
    errorMessages.forEach(message => message.remove());
}

/**
 * Показать уведомление пользователю
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {string} message - Текст сообщения
 */
function showAlert(type, message) {
    // Мапим типы к Bootstrap классам
    const typeMap = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    
    const alertClass = typeMap[type] || 'info';
    
    // Создаем элемент уведомления
    const alert = document.createElement('div');
    alert.className = `alert alert-${alertClass} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        <i class="bi bi-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Добавляем уведомление в контейнер
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

/**
 * Получить иконку для типа уведомления
 * @param {string} type - Тип уведомления
 * @returns {string} - Название иконки Bootstrap Icons
 */
function getIconForType(type) {
    const iconMap = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    
    return iconMap[type] || 'info-circle';
}

/**
 * Инициализация валидации форм в реальном времени
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        
        inputs.forEach(input => {
            // Валидация при потере фокуса
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            // Очистка ошибок при вводе
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    const errorMsg = this.parentNode.querySelector('.invalid-feedback');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
        });
    });
}

/**
 * Валидация отдельного поля
 * @param {HTMLInputElement} field - Поле для валидации
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Проверка обязательных полей
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Это поле обязательно для заполнения';
    }
    
    // Проверка email
    if (field.type === 'email' && value) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(value)) {
            isValid = false;
            errorMessage = 'Введите корректный email адрес';
        }
    }
    
    // Проверка минимальной длины
    if (field.hasAttribute('minlength')) {
        const minLength = parseInt(field.getAttribute('minlength'));
        if (value.length < minLength) {
            isValid = false;
            errorMessage = `Минимальная длина: ${minLength} символов`;
        }
    }
    
    // Проверка максимальной длины
    if (field.hasAttribute('maxlength')) {
        const maxLength = parseInt(field.getAttribute('maxlength'));
        if (value.length > maxLength) {
            isValid = false;
            errorMessage = `Максимальная длина: ${maxLength} символов`;
        }
    }
    
    // Отображаем результат валидации
    if (!isValid) {
        field.classList.add('is-invalid');
        
        // Удаляем предыдущую ошибку
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        // Добавляем новую ошибку
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = errorMessage;
        field.parentNode.appendChild(errorDiv);
    } else {
        field.classList.remove('is-invalid');
        const errorMsg = field.parentNode.querySelector('.invalid-feedback');
        if (errorMsg) {
            errorMsg.remove();
        }
    }
    
    return isValid;
}

/**
 * Инициализация счетчиков символов для текстовых полей
 */
function initializeCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        
        // Создаем счетчик
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        updateCounter(counter, textarea.value.length, maxLength);
        
        // Вставляем счетчик после textarea
        textarea.parentNode.appendChild(counter);
        
        // Обновляем счетчик при вводе
        textarea.addEventListener('input', function() {
            updateCounter(counter, this.value.length, maxLength);
        });
    });
}

/**
 * Обновить счетчик символов
 * @param {HTMLElement} counter - Элемент счетчика
 * @param {number} currentLength - Текущая длина
 * @param {number} maxLength - Максимальная длина
 */
function updateCounter(counter, currentLength, maxLength) {
    counter.textContent = `${currentLength}/${maxLength}`;
    
    // Меняем цвет в зависимости от заполненности
    counter.classList.remove('near-limit', 'over-limit');
    
    if (currentLength > maxLength) {
        counter.classList.add('over-limit');
    } else if (currentLength > maxLength * 0.8) {
        counter.classList.add('near-limit');
    }
}

/**
 * Инициализация всплывающих подсказок
 */
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element);
    });
}

/**
 * Инициализация автоматического скрытия уведомлений
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * Утилита для получения CSRF токена
 * @returns {string} CSRF токен
 */
function getCSRFToken() {
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    return tokenElement ? tokenElement.value : '';
}

/**
 * Утилита для плавной прокрутки к элементу
 * @param {string} selector - Селектор элемента
 */
function scrollToElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

/**
 * Конфирмация действий пользователя
 * @param {string} message - Сообщение для подтверждения
 * @param {Function} callback - Функция для выполнения при подтверждении
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Экспортируем функции для использования в других скриптах
window.FormsApp = {
    showAlert,
    validateField,
    scrollToElement,
    confirmAction,
    getCSRFToken
};
