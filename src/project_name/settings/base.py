"""
Django settings for {{ project_name }} project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from django.core.urlresolvers import reverse_lazy
from os.path import dirname, join, exists

# Build paths inside the project like this: join(BASE_DIR, "directory")
BASE_DIR = dirname(dirname(dirname(__file__)))
STATICFILES_DIRS = [join(BASE_DIR, 'static')]
MEDIA_ROOT = join(BASE_DIR, 'media')
MEDIA_URL = "/media/"

# Use Django templates using the new Django 1.8 TEMPLATES settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
            # insert more TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                '{{ project_name }}.context_processors.generate_menu',
            ],
        },
    },
]

# Use 12factor inspired environment variables or from a file
import environ
env = environ.Env()

# Ideally move env file should be outside the git repo
# i.e. BASE_DIR.parent.parent
env_file = join(dirname(__file__), 'local.env')
if exists(env_file):
    environ.Env.read_env(str(env_file))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'authentication',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = '{{ project_name }}.urls'

WSGI_APPLICATION = '{{ project_name }}.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in
    # os.environ
    'default': env.db(var='DJANGO_DATABASE_URL'),
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

ALLOWED_HOSTS = []

# For Bootstrap 3, change error alert to 'danger'
from django.contrib import messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

# Authentication Settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
DISABLE_AUTHENTICATION = True
if not DISABLE_AUTHENTICATION:
    AUTHENTICATION_BACKENDS += [
        'authentication.backends.UniversalLdapBackendWithPassword',
        'authentication.backends.UniversalLdapBackendWithoutPassword',
        'authentication.backends.UniversalLdapBackendWithToken',
    ]
LOGIN_REDIRECT_URL = reverse_lazy("account:profile")
LOGIN_URL = reverse_lazy("account:login")

LDAP_ORIGIN = env('DJANGO_LDAP_ORIGIN')
LDAP_ROOT = env('DJANGO_LDAP_ROOT')
LDAP_SEARCH_FILTER = env('DJANGO_LDAP_SEARCH_FILTER')
LDAP_SEARCH_BASE = env('DJANGO_LDAP_SEARCH_BASE')
LDAP_MANAGER_DN = env('DJANGO_LDAP_MANAGER_DN')
LDAP_MANAGER_PASSWORD = env('DJANGO_LDAP_MANAGER_PASSWORD')
LDAP_MAPS = {
    'first_name': env('DJANGO_LDAP_FIRST_NAME'),
    'last_name': env('DJANGO_LDAP_LAST_NAME'),
    'email': env('DJANGO_LDAP_EMAIL')
}
LDAP_GROUP_LIST = env('DJANGO_LDAP_GROUP_LIST')
# a list of DNs that are separated by |
LDAP_GROUP_BASE = env('DJANGO_LDAP_GROUP_BASE')
LDAP_GROUP_NAME = env('DJANGO_LDAP_GROUP_NAME')

TEST_LDAP_USER = env('DJANGO_TEST_LDAP_USERNAME')
TEST_LDAP_PASS = env('DJANGO_TEST_LDAP_PASSWORD')
TEST_LDAP_FIRST_NAME = env('DJANGO_TEST_LDAP_FIRST_NAME')
TEST_LDAP_LAST_NAME = env('DJANGO_TEST_LDAP_LAST_NAME')
TEST_LDAP_EMAIL = env('DJANGO_TEST_LDAP_EMAIL')
