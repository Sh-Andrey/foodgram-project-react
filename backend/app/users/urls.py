from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.users.views import CustomAuthToken, DestroyTokenAPIView, UserViewSet

v2_router = DefaultRouter()

v2_router.register('', UserViewSet, basename='users')

auth_urlpatterns = [
    path('login/', CustomAuthToken.as_view()),
    path('logout/', DestroyTokenAPIView.as_view()),
]

urlpatterns = [
    path('auth/token/', include(auth_urlpatterns)),
    path('users/', include(v2_router.urls))
]
