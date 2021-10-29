from rest_framework.permissions import IsAuthenticated
from .serializers import RegistrationSerializer, ActivationSerializer, LoginSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, ForgotPassCompleteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .permissions import IsActivePermission


class RegistrationView(APIView):

    def post(self, request):
        data = request.data
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.create(serializer.validated_data)
            return Response(
                'Аккаунт успешно создан', status=201
            )


class ActivationView(APIView):

    def post(self, request):

        serializer = ActivationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.activate()
            return Response(
                'Аккаунт успешно активирован', status = 200
            )


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


# Если вам нужно передать request в serializers то нужно переопределить методы get_serializer_context & get_serializer



class LogoutView(APIView):

    permission_classes = [IsActivePermission]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('Вы успешно вышли из аккаунта')


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Status: 200. Пароль успешно обновлён')


class ForgotPasswordView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_email()
            return Response('Вам было выслано код активации на вашу почту для востановления пароля')


class ForgotPassCompleteView(APIView):

    def post(self, request):
        serializer = ForgotPassCompleteSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Пароль был успешно заменён')