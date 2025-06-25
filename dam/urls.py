from django.urls import path

from .views import process_dam, hello, test


app_name = 'dam'

urlpatterns = [
    path('', process_dam, name='dam_form'),
    path('hello/', hello, name='hello'),
    path('test/', test, name='test'),
]
