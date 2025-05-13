from django.contrib import admin
from django.urls import path, include
from where_to_go.views import show_places, get_place_details
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', show_places),
    path(
        'places/<int:place_id>/json/',
        get_place_details,
        name='place-json-details'
    ),
    path('tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
