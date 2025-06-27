from django.urls import path

from .views import dam_challenge, hello


app_name = 'dam'

urlpatterns = [
    path('', dam_challenge, name='challenge'),
    path('hello/', hello, name='hello'),
]
