import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0!nhn#eryynq7@c7tl*qqg^g87!5o3k_-d1hzv7!dj^+74ditz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion.apps.GestionConfig',
    'social_django',
    'bootstrap4',
    'guardian',
]

# Auth0 settings
SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
#modificar con mi app
SOCIAL_AUTH_AUTH0_DOMAIN = 'ruben-dev.auth0.com'
SOCIAL_AUTH_AUTH0_KEY = 'q8WImi9pV1hGFO62esYPTyhtoBey1Tlk'
SOCIAL_AUTH_AUTH0_SECRET = '9sruysUq2lR46e5UmOzMgMmrl9gLaFCMMUP7dq-MpxB-PXYE8foxhg2bHVt8jsAp'
SOCIAL_AUTH_AUTH0_SCOPE = [
    'openid',
    'profile',
    'email'
]

AUTHENTICATION_BACKENDS = {
    'social_core.backends.auth0.Auth0OAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    #'app1.authOlogin.auth0backend.Auth0',
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
   # 'django_dropbox_upload_handler.apps.DjangoDropboxUploadHandlerConfig',
}

LOGIN_URL = '/login/auth0'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GestionItem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'GestionItem.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


"""
DATOS CAMBIADOS
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'prueba3',
        'USER':'postgres',
        'PASSWORD':'root',
        'HOST':'127.0.0.1',
        'PORT':'5432',
    }
}




# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/



LANGUAGE_CODE = 'es-py'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

#configuracion de email
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'GestionItems.FPUNA@gmail.com'
EMAIL_HOST_PASSWORD = 'GestionItems2020'
EMAIL_PORT = 587


####para manejar archivos
#MEDIA_URL = '/books/' #se utiliza para manejar los archivos subidos
#MEDIA_ROOT = os.path.join(BASE_DIR, 'books') #manejar donde subir los archivos

DROPBOX_ROOT ="/Dropbox/"
# Media path inside Dropbox folder
MEDIA_ROOT = os.path.join(DROPBOX_ROOT, "media")
MEDIA_URL = '/media/'


##dropbox
#DROPBOX_CONSUMER_KEY= "657yh6439e6zn8b"
#DROPBOX_CONSUMER_SECRET= "jnnh5qwh7p1nmid"
DROPBOX_OAUTH2_TOKEN = "GpsA66XtmLAAAAAAAAAATGBQLCDXPSILfau_PQgJ2Drmbsfj0E-Zn_EBdyQt2F3n"
'''
FILE_UPLOAD_HANDLERS = (
    "gestion.dropbox_upload_handler.DropboxFileUploadHandler",
)
'''
DEFAULT_FILE_STORAGE = 'storages.backends.dropbox.DropBoxStorage'