from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/map/', include('map.urls')),
    path('', RedirectView.as_view(url='/api/map/', permanent=True)),
]