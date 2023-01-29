from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
    path('about/', include('about.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),

]

if settings.DEBUG:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
