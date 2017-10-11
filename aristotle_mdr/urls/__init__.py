from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import password_reset
from django.views.generic.base import RedirectView
from aristotle_mdr.views.user_pages import friendly_redirect_login

admin.autodiscover()

urlpatterns = [
    url(r'^', include('aristotle_mdr.urls.base')),
    url(r'^', include('aristotle_mdr.urls.aristotle', app_name="aristotle_mdr", namespace="aristotle")),
    url(r'^ac/', include('aristotle_mdr.contrib.autocomplete.urls', namespace="aristotle-autocomplete")),
    url(r'^', include('aristotle_mdr.contrib.healthcheck.urls', app_name="aristotle_mdr_hb", namespace="aristotle_hb")),
]


# This is only for dev work, so we can skip it.
if settings.DEBUG:  # pragma: no cover
    from django.conf import settings
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = 'aristotle_mdr.views.unauthorised'
