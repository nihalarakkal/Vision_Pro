from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import Staff.urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace="core")),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('Staff/',include('Staff.urls')),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
