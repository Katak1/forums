from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import User
from .utils import send_activation_code
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from .tasks import send_activation_code_celery


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=4, required=True)
    password_confirm = serializers.CharField(
        min_length=4, required=True
    )

    name = serializers.CharField(required=True)
    last_name = serializers.CharField()

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже зарегистрирован"
            )

        return email

    def validate(self, data):
        password = data.get('password')

        password_confirm = data.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError(
                "Пароль не совпадает"
            )
        print(data)
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        send_activation_code_celery.delay(user.email, user.activation_code)
        return user


class ActivationSerializer(serializers.Serializer):
    email = serializers.CharField()
    code = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')
        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return data

    def activate(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return email

    def validate(self, data):
        request = self.context.get('request')
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password, request=request)
            if not user:
                raise serializers.ValidationError('Неверный email или пароль')
        else:
            raise serializers.ValidationError('Email и пароль обязательны к заполнению')

        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=4, required=True)
    new_password = serializers.CharField(min_length=4, required=True)
    new_password_confirm = serializers.CharField(min_length=4, required=True)


    def validate_old_password(self, old_pass):
        request = self.context.get('request')
        user = request.user
        if not user.check_password(old_pass):
            raise serializers.ValidationError('Введите корректный пароль')
        return old_pass

    def validate(self, attrs):
        new_pass1 = attrs.get('new_password')
        new_pass2 = attrs.get('new_password_confirm')
        old_pass = attrs.get('old_password')
        if new_pass1 != new_pass2:
            raise serializers.ValidationError('Пароли не совпадают')
        if new_pass1 == old_pass:
            raise serializers.ValidationError('Пароли не должны совпадать')
        return attrs

    def set_new_password(self):
        new_pass = self.validated_data.get('new_password')
        user = self.context.get('request').user
        user.set_password(new_pass)
        user.save()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')

        return email

    def send_verification_email(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        send_mail(
            'Забыли пароль',
            f'Ваш код для активации для начала изменения пароля - {user.activation_code}',
            'test@gmail.com',
            [user.email]
        )


class ForgotPassCompleteSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=4, required=True)
    password_confirm = serializers.CharField(min_length=4, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password1 = attrs.get('password')
        password2 = attrs.get('password_confirm')
        code = attrs.get('code')

        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError("Данные не найдены")
        if password1 != password2:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def set_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()