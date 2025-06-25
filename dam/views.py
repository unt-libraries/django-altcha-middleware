from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .forms import DAMForm
from .decorators import altcha_verify


def process_dam(request):
    """Process Altcha form data."""
    if request.method == 'POST':
        altcha_session_key = getattr(settings,
                                     'ALTCHA_SESSION_KEY',
                                     'altcha_verified')
        form = DAMForm(request.POST)
        if form.is_valid():
            request.session[altcha_session_key] = True
            return HttpResponseRedirect(request.POST.get('next', '/'))
    form = DAMForm()
    js_src_url = getattr(settings, 'ALTCHA_JS_URL', '/static/altcha/altcha.min.js')
    context = {'form': form,
               'next_url': request.GET.get('next', '/'),
               'js_src_url': js_src_url}
    return render(request, 'dam_form.html', context)


@altcha_verify
def hello(request):
    return HttpResponse('hello there')


def test(request):
    return HttpResponse('Test')
