from django.contrib import admin
from .models import UserProfile, Message

# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Конфигурация админ-панели для модели UserProfile.
    Настраивает отображение и функциональность управления профилями пользователей.
    """
    # Поля для отображения в списке профилей
    list_display = ['user', 'phone_number', 'created_at', 'updated_at']
    
    # Поля для поиска
    search_fields = ['user__username', 'user__email', 'phone_number']
    
    # Фильтры в боковой панели
    list_filter = ['created_at', 'updated_at']
    
    # Поля только для чтения
    readonly_fields = ['created_at', 'updated_at']
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('user',)
        }),
        ('Дополнительная информация', {
            'fields': ('phone_number', 'bio'),
            'classes': ('collapse',)  # Сворачиваемая секция
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Количество записей на странице
    list_per_page = 25
    
    # Сортировка по умолчанию
    ordering = ['-created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Конфигурация админ-панели для модели Message.
    Настраивает отображение и функциональность управления сообщениями.
    """
    # Поля для отображения в списке сообщений
    list_display = ['name', 'email', 'get_short_message', 'user', 'is_read', 'created_at']
    
    # Поля для поиска
    search_fields = ['name', 'email', 'message_text', 'user__username']
    
    # Фильтры в боковой панели
    list_filter = ['is_read', 'created_at', 'user']
    
    # Поля только для чтения
    readonly_fields = ['created_at', 'ip_address']
    
    # Поля, которые можно редактировать прямо в списке
    list_editable = ['is_read']
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Информация об отправителе', {
            'fields': ('name', 'email', 'user')
        }),
        ('Содержание сообщения', {
            'fields': ('message_text',)
        }),
        ('Статус и метаданные', {
            'fields': ('is_read', 'ip_address', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Количество записей на странице
    list_per_page = 20
    
    # Сортировка по умолчанию (непрочитанные первыми, затем по дате)
    ordering = ['is_read', '-created_at']
    
    # Действия для массовых операций
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Массовое действие: отметить сообщения как прочитанные"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} сообщений отмечено как прочитанные.')
    mark_as_read.short_description = 'Отметить как прочитанные'
    
    def mark_as_unread(self, request, queryset):
        """Массовое действие: отметить сообщения как непрочитанные"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} сообщений отмечено как непрочитанные.')
    mark_as_unread.short_description = 'Отметить как непрочитанные'
