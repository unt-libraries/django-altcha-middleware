from django.urls import path

from dam.views import dam_challenge


app_name = 'dam'

urlpatterns = [
    path('', dam_challenge, name='challenge'),
]
