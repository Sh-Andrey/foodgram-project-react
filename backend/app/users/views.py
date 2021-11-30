from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response

from app.recipes.pagination import PageNumberAndLimitPagination
from app.users.models import Follow, User
from app.users.serializers import (CustomAuthTokenSerializer,
                                   SetPasswordSerializer, UserSerializer,
                                   UserSubscriptionSerializer)


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'auth_token': token.key
            },
            status=status.HTTP_201_CREATED
        )


class DestroyTokenAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user:
            Response(
                {
                    'detail': ('Учетные данные для '
                               'аутентификации не предоставлены.')
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            Response(
                {
                    'detail': 'Токен не существует.'
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(
        methods=['get'],
        detail=False,
        url_name='me',
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        url_name='set_password',
        url_path='set_password',
        permission_classes=[permissions.IsAuthenticated],
    )
    def set_password(self, request, *args, **kwargs):
        user = request.user
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data.get
        if user.check_password(validated('current_password')):
            user.set_password(validated('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'current_password': 'Введен неверный пароль.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        url_name='subscriptions',
        url_path='subscriptions',
        serializer_class=UserSubscriptionSerializer,
        pagination_class=PageNumberAndLimitPagination,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscription(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(subscribers__subscriber=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', 'delete'],
        url_name='subscribe',
        url_path=r'(?P<id>[\d]+)/subscribe',
        pagination_class=None,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs['id'])
        subscription = Follow.objects.filter(
            subscriber=user,
            author=author
        )
        if request.method == 'GET':
            if author != user and not subscription.exists():
                Follow.objects.create(
                    subscriber=user,
                    author=author
                )
                serializer = UserSubscriptionSerializer(
                    author,
                    context={
                        'request': request
                    }
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        if request.method == 'DELETE' and subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                'detail': 'Действие уже выполнено.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
