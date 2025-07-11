from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, Message


class CustomUserRegistrationForm(UserCreationForm):
    """
    Кастомная форма регистрации пользователя.
    Расширяет стандартную форму Django дополнительными полями и валидацией.
    """
    # Дополнительные поля для регистрации
    email = forms.EmailField(
        required=True,
        label="Электронная почта",
        help_text="Введите действующий email адрес",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Имя",
        help_text="Введите ваше имя",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Фамилия",
        help_text="Введите вашу фамилию",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия'
        })
    )
    
    # Дополнительные поля профиля
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label="Номер телефона",
        help_text="Номер телефона в формате +7XXXXXXXXXX",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7XXXXXXXXXX'
        })
    )
    
    bio = forms.CharField(
        max_length=500,
        required=False,
        label="О себе",
        help_text="Краткая информация о вас (до 500 символов)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Расскажите немного о себе...'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """Инициализация формы с добавлением CSS классов"""
        super().__init__(*args, **kwargs)
        
        # Добавляем CSS классы для стандартных полей
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля'
        })
        
        # Русификация меток и подсказок
        self.fields['username'].label = "Имя пользователя"
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].label = "Подтверждение пароля"
        
        self.fields['username'].help_text = "Только буквы, цифры и символы @/./+/-/_"
        self.fields['password1'].help_text = "Пароль должен содержать минимум 8 символов"
        self.fields['password2'].help_text = "Повторите пароль для подтверждения"

    def clean_email(self):
        """Валидация email - проверка на уникальность"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(
                "Пользователь с таким email уже зарегистрирован. "
                "Попробуйте войти в систему или используйте другой email."
            )
        return email

    def clean_phone_number(self):
        """Валидация номера телефона"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Удаляем все символы кроме цифр и +
            cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
            if not cleaned_phone.startswith('+7') or len(cleaned_phone) != 12:
                raise ValidationError(
                    "Номер телефона должен быть в формате +7XXXXXXXXXX"
                )
        return phone

    def save(self, commit=True):
        """Сохранение пользователя и создание профиля"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', ''),
                bio=self.cleaned_data.get('bio', '')
            )
        return user


class CustomLoginForm(forms.Form):
    """
    Кастомная форма авторизации пользователя.
    Позволяет входить как по имени пользователя, так и по email.
    """
    username = forms.CharField(
        max_length=254,
        label="Имя пользователя или Email",
        help_text="Введите имя пользователя или email адрес",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя или email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        label="Запомнить меня",
        help_text="Оставаться в системе на этом устройстве",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean(self):
        """Валидация данных авторизации"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Проверяем, является ли username email адресом
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    cleaned_data['username'] = user.username
                except User.DoesNotExist:
                    raise ValidationError("Пользователь с таким email не найден.")
            
        return cleaned_data


class MessageForm(forms.ModelForm):
    """
    Форма для отправки сообщений.
    Может использоваться как авторизованными, так и анонимными пользователями.
    """
    
    class Meta:
        model = Message
        fields = ['name', 'email', 'message_text']
        
        # Кастомные виджеты с CSS классами и атрибутами
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
                'maxlength': 100
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'message_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите ваше сообщение...',
                'maxlength': 500
            })
        }
        
        # Русские метки для полей
        labels = {
            'name': 'Ваше имя',
            'email': 'Электронная почта',
            'message_text': 'Сообщение'
        }
        
        # Подсказки для полей
        help_texts = {
            'name': 'Как к вам обращаться (минимум 2 символа)',
            'email': 'Ваш email для обратной связи',
            'message_text': 'Текст сообщения (от 10 до 500 символов)'
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы"""
        # Извлекаем пользователя из kwargs, если он передан
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Если пользователь авторизован, предзаполняем поля
        if self.user and self.user.is_authenticated:
            self.fields['name'].initial = f"{self.user.first_name} {self.user.last_name}".strip()
            if not self.fields['name'].initial:
                self.fields['name'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def clean_name(self):
        """Валидация имени отправителя"""
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise ValidationError("Имя должно содержать минимум 2 символа.")
        return name.strip() if name else name

    def clean_message_text(self):
        """Валидация текста сообщения"""
        message = self.cleaned_data.get('message_text')
        if message:
            message = message.strip()
            if len(message) < 10:
                raise ValidationError("Сообщение должно содержать минимум 10 символов.")
            if len(message) > 500:
                raise ValidationError("Сообщение не должно превышать 500 символов.")
            
            # Проверка на спам (простая проверка)
            spam_words = ['spam', 'реклама', 'заработок', 'кредит', 'казино']
            message_lower = message.lower()
            for word in spam_words:
                if word in message_lower:
                    raise ValidationError(
                        "Сообщение содержит запрещенные слова. "
                        "Пожалуйста, измените текст."
                    )
        return message

    def save(self, commit=True):
        """Сохранение сообщения с привязкой к пользователю"""
        message = super().save(commit=False)
        
        # Привязываем пользователя, если он авторизован
        if self.user and self.user.is_authenticated:
            message.user = self.user
            
        if commit:
            message.save()
        return message


class UserProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.
    Позволяет изменять дополнительную информацию профиля.
    """
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio']
        
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7XXXXXXXXXX'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о себе...'
            })
        }
        
        labels = {
            'phone_number': 'Номер телефона',
            'bio': 'О себе'
        }

    def clean_phone_number(self):
        """Валидация номера телефона"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
            if not cleaned_phone.startswith('+7') or len(cleaned_phone) != 12:
                raise ValidationError(
                    "Номер телефона должен быть в формате +7XXXXXXXXXX"
                )
        return phone
