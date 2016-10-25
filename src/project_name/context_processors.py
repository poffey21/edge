from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.template import RequestContext
from django.urls import NoReverseMatch
from django.urls import Resolver404
from django.urls import reverse
from django.urls import resolve

validate = URLValidator(schemes=['http', 'https'])

def determine_url(url_passed):
    try:
        url = reverse(url_passed)
        return url
    except NoReverseMatch as e:
        pass

    try:
        resolve(url_passed)
        return url_passed
    except Resolver404:
        pass

    try:
        validate(url_passed)
        return url_passed
    except ValidationError as e:
        pass
    return None

def generate_menu(request):
    request_context = RequestContext(request)
    active_url = request.path
    menu = request_context.get('menu', []) + [
        {
            'title': 'Home',
            'url': determine_url('home'),
            # 'classes': '',
        },
        {
            'title': 'About',
            'url': determine_url('about'),
        },
    ]
    for item in menu:
        if active_url == item['url']:
            item['active'] = 'active'
    return {
        'menu': menu,
        'authentication_installed': 'authentication' in settings.INSTALLED_APPS and not settings.DISABLE_AUTHENTICATION,
    }
