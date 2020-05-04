from .base import *
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


"""
DATOS CAMBIADOS
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'prueba2',
        'USER':'postgres',
        'PASSWORD':'root',
        'HOST':'127.0.0.1',
        'PORT':'5432',
    }
}
DEBUG = True

ALLOWED_HOSTS = []
