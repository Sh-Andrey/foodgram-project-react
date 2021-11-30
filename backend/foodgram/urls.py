from django.contrib import admin
from django.urls import include, path

app_urlpatterns = [
    path('', include('app.users.urls')),
    path('', include('app.recipes.urls')),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(app_urlpatterns)),
]
