from django.contrib import admin
from django.urls import path,include
from accounts import views
from django.contrib.auth import get_user_model


def create_admin_once():
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('owner', 'admin@example.com', '2691999')
        print("Done! Admin created.")

# بنادي الدالة دي عشان تشتغل أول ما السيرفر يقوم
try:
    create_admin_once()
except:
    pass

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('accounts/',include('accounts.urls')),
    path('storage/',include('storage.urls')),
    path('analytics/', include('analytics.urls')),
]
