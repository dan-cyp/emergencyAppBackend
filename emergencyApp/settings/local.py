from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.0.[0-9]+', 'localhost', '127.0.0.1', '192.168.0.105', '192.168.88.82', '192.168.88.199']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DISABLE_QUERYSET_CACHE = True