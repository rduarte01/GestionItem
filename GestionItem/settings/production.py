from .base import *
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


"""
DATOS CAMBIADOS
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd3amrs8m7cjc4',
        'USER':'ezacwlizuiwqfc',
        'PASSWORD':'9432c121a841861f2e6d0fa051363f75c85adbaa8caa6a65782c80b7ad945dba',
        'HOST':'ec2-50-17-178-87.compute-1.amazonaws.com',
        'PORT':'5432',
    }
}
DEBUG = True

ALLOWED_HOSTS = ['djangoproyect.herokuapp.com']
