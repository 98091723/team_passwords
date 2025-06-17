from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from passwords.views import password_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('teams/', include('teams.urls')),
    path('passwords/', include('passwords.urls')),
    path('dashboard/', password_list, name='dashboard'),
]