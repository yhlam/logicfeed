from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS += (
    'django_extensions',
)

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'yhlam.bot'
EMAIL_HOST_PASSWORD = 'e2718281828'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
