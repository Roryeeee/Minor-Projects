from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    #path('events/', include('eventpollapp.urls')),
    path('bills/', include('bills.urls')),
    path('dashboard/', include('eventpollapp.urls')),
    path('', lambda request: redirect('accounts:login')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)