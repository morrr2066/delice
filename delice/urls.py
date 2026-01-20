from django.contrib import admin
from django.urls import include, path
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('storage/', include('storage.urls')),
    path('analytics/', include('analytics.urls')),
]
