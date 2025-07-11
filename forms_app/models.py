from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator

# Create your models here.


class UserProfile(models.Model):
    """
    Модель профиля пользователя для расширения встроенной модели User.
    Добавляет дополнительные поля: номер телефона и биографию.
    """
    # Связь один-к-одному со встроенной моделью User Django
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Связанный пользователь Django"
    )
    
    # Номер телефона пользователя (необязательное поле)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
        help_text="Номер телефона в формате +7XXXXXXXXXX"
    )
    
    # Биография пользователя (необязательное поле)
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="О себе",
        help_text="Краткая информация о пользователе (до 500 символов)"
    )
    
    # Дата создания профиля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    # Дата последнего обновления профиля
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        ordering = ['-created_at']  # Сортировка по дате создания (новые первые)

    def __str__(self):
        """Строковое представление модели"""
        return f"Профиль {self.user.username}"


class Message(models.Model):
    """
    Модель для хранения сообщений, отправленных через форму контактов.
    Может быть отправлена как зарегистрированным, так и анонимным пользователем.
    """
    # Имя отправителя (обязательное поле)
    name = models.CharField(
        max_length=100,
        verbose_name="Имя отправителя",
        help_text="Имя человека, отправившего сообщение",
        validators=[MinLengthValidator(2, "Имя должно содержать минимум 2 символа")]
    )
    
    # Email отправителя (обязательное поле)
    email = models.EmailField(
        verbose_name="Email отправителя",
        help_text="Электронная почта для обратной связи"
    )
    
    # Текст сообщения (обязательное поле с ограничением длины)
    message_text = models.TextField(
        verbose_name="Текст сообщения",
        help_text="Содержание сообщения (до 500 символов)",
        validators=[
            MinLengthValidator(10, "Сообщение должно содержать минимум 10 символов"),
            MaxLengthValidator(500, "Сообщение не должно превышать 500 символов")
        ]
    )
    
    # Связанный пользователь (необязательно - для анонимных сообщений)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        help_text="Пользователь, отправивший сообщение (если авторизован)"
    )
    
    # IP-адрес отправителя для отслеживания
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP-адрес",
        help_text="IP-адрес отправителя сообщения"
    )
    
    # Дата и время отправки сообщения
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата отправки"
    )
    
    # Флаг для отметки прочитанного сообщения
    is_read = models.BooleanField(
        default=False,
        verbose_name="Прочитано",
        help_text="Отметка о том, что сообщение было прочитано администратором"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']  # Сортировка по дате отправки (новые первые)
        indexes = [
            # Индекс для быстрого поиска непрочитанных сообщений
            models.Index(fields=['is_read', '-created_at']),
            # Индекс для поиска сообщений по пользователю
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        """Строковое представление модели"""
        return f"Сообщение от {self.name} ({self.email}) - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    def get_short_message(self):
        """Возвращает сокращенную версию сообщения для отображения в списках"""
        if len(self.message_text) > 50:
            return f"{self.message_text[:50]}..."
        return self.message_text
    
    def mark_as_read(self):
        """Отмечает сообщение как прочитанное"""
        self.is_read = True
        self.save(update_fields=['is_read'])
