from django.urls import path
from . import views

# URL-маршруты для приложения forms_app
# Все маршруты с подробными комментариями для понимания структуры

urlpatterns = [
    # Главная страница сайта
    path('', views.home_view, name='home'),
    
    # Маршруты для аутентификации пользователей
    path('register/', views.register_view, name='register'),  # Регистрация нового пользователя
    path('login/', views.login_view, name='login'),          # Авторизация пользователя
    path('logout/', views.logout_view, name='logout'),       # Выход из системы
    
    # Маршруты для работы с сообщениями
    path('contact/', views.contact_view, name='contact'),    # Форма отправки сообщения
    path('ajax-contact/', views.ajax_contact_view, name='ajax_contact'),  # Ajax отправка сообщения
    
    # Маршруты для профиля пользователя (требуют авторизации)
    path('profile/', views.profile_view, name='profile'),    # Просмотр и редактирование профиля
    path('messages/', views.messages_list_view, name='messages_list'),  # Список сообщений пользователя
]
