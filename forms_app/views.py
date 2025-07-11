from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import CustomUserRegistrationForm, CustomLoginForm, MessageForm, UserProfileForm
from .models import Message, UserProfile
import json

# Create your views here.


def home_view(request):
    """
    Главная страница сайта.
    Отображает основную информацию и ссылки на формы.
    """
    # Получаем последние сообщения для отображения (если пользователь авторизован)
    recent_messages = None
    if request.user.is_authenticated:
        recent_messages = Message.objects.filter(user=request.user)[:3]
    
    context = {
        'recent_messages': recent_messages,
        'total_messages': Message.objects.count() if request.user.is_superuser else None
    }
    return render(request, 'forms_app/home.html', context)


def register_view(request):
    """
    Представление для регистрации новых пользователей.
    Обрабатывает форму регистрации с валидацией.
    """
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Сохраняем пользователя и профиль
                user = form.save()
                
                # Автоматически авторизуем пользователя после регистрации
                login(request, user)
                
                # Добавляем сообщение об успешной регистрации
                messages.success(
                    request, 
                    f'Добро пожаловать, {user.first_name}! '
                    f'Вы успешно зарегистрированы и авторизованы.'
                )
                
                # Перенаправляем на главную страницу
                return redirect('home')
                
            except Exception as e:
                # Обработка ошибок при создании пользователя
                messages.error(
                    request, 
                    'Произошла ошибка при регистрации. Попробуйте еще раз.'
                )
        else:
            # Если форма невалидна, добавляем сообщение об ошибке
            messages.error(
                request, 
                'Пожалуйста, исправьте ошибки в форме.'
            )
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'forms_app/register.html', {'form': form})


def login_view(request):
    """
    Представление для авторизации пользователей.
    Поддерживает вход по имени пользователя или email.
    """
    # Если пользователь уже авторизован, перенаправляем на главную
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            
            # Аутентифицируем пользователя
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Настраиваем продолжительность сессии
                    if not remember_me:
                        # Сессия заканчивается при закрытии браузера
                        request.session.set_expiry(0)
                    
                    messages.success(
                        request, 
                        f'Добро пожаловать, {user.first_name or user.username}!'
                    )
                    
                    # Перенаправляем на запрошенную страницу или на главную
                    next_url = request.GET.get('next', 'home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Ваш аккаунт деактивирован.')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'forms_app/login.html', {'form': form})


def logout_view(request):
    """
    Представление для выхода из системы.
    """
    if request.user.is_authenticated:
        username = request.user.first_name or request.user.username
        logout(request)
        messages.info(request, f'До свидания, {username}! Вы вышли из системы.')
    
    return redirect('home')


def contact_view(request):
    """
    Представление для формы отправки сообщений.
    Поддерживает как обычную отправку, так и Ajax.
    """
    if request.method == 'POST':
        # Проверяем, это Ajax запрос или обычная форма
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Получаем IP адрес пользователя
        ip_address = get_client_ip(request)
        
        form = MessageForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                # Сохраняем сообщение
                message = form.save(commit=False)
                message.ip_address = ip_address
                message.save()
                
                success_message = (
                    'Спасибо за ваше сообщение! '
                    'Мы получили его и ответим в ближайшее время.'
                )
                
                if is_ajax:
                    # Ajax ответ
                    return JsonResponse({
                        'success': True,
                        'message': success_message
                    })
                else:
                    # Обычный ответ
                    messages.success(request, success_message)
                    return redirect('contact')
                    
            except Exception as e:
                error_message = 'Произошла ошибка при отправке сообщения. Попробуйте еще раз.'
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    })
                else:
                    messages.error(request, error_message)
        else:
            # Форма невалидна
            if is_ajax:
                # Возвращаем ошибки валидации для Ajax
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Пожалуйста, исправьте ошибки в форме.'
                })
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = MessageForm(user=request.user)
    
    return render(request, 'forms_app/contact.html', {'form': form})


@login_required
def profile_view(request):
    """
    Представление для просмотра и редактирования профиля пользователя.
    Доступно только авторизованным пользователям.
    """
    # Получаем или создаем профиль пользователя
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Получаем сообщения пользователя с пагинацией
    user_messages = Message.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(user_messages, 10)  # 10 сообщений на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'user_messages': page_obj,
        'messages_count': user_messages.count()
    }
    
    return render(request, 'forms_app/profile.html', context)


@login_required
def messages_list_view(request):
    """
    Представление для просмотра всех сообщений пользователя.
    С возможностью поиска и фильтрации.
    """
    # Базовый queryset сообщений пользователя
    messages_queryset = Message.objects.filter(user=request.user)
    
    # Поиск по тексту сообщения
    search_query = request.GET.get('search', '')
    if search_query:
        messages_queryset = messages_queryset.filter(
            Q(message_text__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Фильтр по прочитанности (если пользователь - администратор)
    read_filter = request.GET.get('read', '')
    if read_filter and request.user.is_superuser:
        if read_filter == 'read':
            messages_queryset = messages_queryset.filter(is_read=True)
        elif read_filter == 'unread':
            messages_queryset = messages_queryset.filter(is_read=False)
    
    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'created_at', 'name', 'email']:
        messages_queryset = messages_queryset.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(messages_queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'messages': page_obj,
        'search_query': search_query,
        'read_filter': read_filter,
        'sort_by': sort_by,
        'total_messages': messages_queryset.count()
    }
    
    return render(request, 'forms_app/messages_list.html', context)


def get_client_ip(request):
    """
    Утилита для получения IP адреса клиента.
    Учитывает возможные прокси и load balancer'ы.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_POST
@csrf_exempt
def ajax_contact_view(request):
    """
    Специальное представление только для Ajax отправки сообщений.
    Возвращает JSON ответ для обработки на фронтенде.
    """
    try:
        # Парсим JSON данные
        data = json.loads(request.body)
        
        # Создаем форму с данными
        form = MessageForm(data, user=request.user)
        
        if form.is_valid():
            # Сохраняем сообщение
            message = form.save(commit=False)
            message.ip_address = get_client_ip(request)
            message.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Сообщение успешно отправлено!',
                'message_id': message.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Ошибки в форме. Проверьте введенные данные.'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат данных.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка на сервере.'
        })
