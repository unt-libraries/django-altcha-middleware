ALTCHA_HMAC_KEY = 'donotuseinproduction'

ALTCHA_MAX_NUMBER = 100000

ALTCHA_AUTH_EXPIRE_MINUTES = 480

ALTCHA_CHALLENGE_EXPIRE_MINUTES = 2

ALTCHA_SALT_PARAMS = {}

ALTCHA_SESSION_KEY = 'altcha_verified'

ALTCHA_SITE_ICON_URL = ''

ALTCHA_JS_URL = '/static/altcha/altcha.min.js'

ALTCHA_CSS_URL = '/static/dam/dam.css'

ALTCHA_MESSAGE = 'Gauging your humanity...This may take some seconds.'

ALTCHA_HELP_MESSAGE = 'If you are unable to reach our site content, please <a href="https://example.com">let us know.</a>'

ALTCHA_FAIL_MESSAGE = 'Challenge failed or no longer valid.'

ALTCHA_EXCLUDE_PATHS = []

ALTCHA_EXCLUDE_IPS = []

ALTCHA_EXCLUDE_HEADERS = {}

DEBUG = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dam',
]

SECRET_KEY = 'notverysecret'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATIC_URL = '/static/'

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
