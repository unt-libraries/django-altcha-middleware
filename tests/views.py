from django.http import HttpResponse
from dam.decorators import dam


@dam
def protected_view(request, *args, **kwargs):
    return HttpResponse('You made it to the protected view!')


def open_view(request, *args, **kwargs):
    return HttpResponse('This view is open to anyone. '
                        'View a <a href="/protected/">protected</a> page.')
