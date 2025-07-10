from django.urls import include, path

from tests.views import protected_view, open_view


urlpatterns = [
    path('', include('dam.urls')),
    path('protected/', protected_view),
    path('open/', open_view),
]
