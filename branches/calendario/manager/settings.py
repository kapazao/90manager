# -*- coding: utf-8 -*-
# Django settings for manager project.

import os.path

# Cargar datos sensibles (No deben de estar en el svn, son contraseñas y datos importantes)
try:
	import personales
except: # No hay personales, cargar config por defecto
	vper = None
	print "No hay variables personales, asi que a tomar configuracion por defecto"
else: # Hay personales, cargar configuracion de allí
	vper = personales.datos_personales

DEBUG = True
TEMPLATE_DEBUG = DEBUG


# Variables del proyecto
URL_PROPIA = 'http://localhost:8000/'
RUTA = os.path.dirname(__file__) + "/"

# Mandar reporte de error por correo a los siguientes destinatarios cuando DEBUG = False
ADMINS = (('Juanmi', 'ciberjm@gmail.com'), ('Pino', 'jllopezpino@gmail.com'), ('Carlos', 'carlos.kapazao@gmail.com'))

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': RUTA + 'datos.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Configuracion del e-mail
if vper:
	EMAIL_HOST = vper['email_host']
	EMAIL_HOST_USER = vper['email_host_user']
	EMAIL_HOST_PASSWORD = vper['email_host_password']

EMAIL_SUBJECT_PREFIX = '[90manager] '
SERVER_EMAIL = 'noreply@90manager.com'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-es'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# No se si es necesario (Carlos)
#MEDIA_PREFIX = '/media/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = RUTA + "public/site_media"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'f+8k5vf7x$n@kmd62c9!42i4)6-@v4%q6)+_9hq)+uz6wr3t!c'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

AUTHENTICATION_BACKENDS = (
    'manager.gestion_usuario.auth_backend.UsuarioModelBackend',
)

CUSTOM_USER_MODEL = 'gestion_usuario.Usuario'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'manager.urls'

# Cambio de variables para la redireccion del login
LOGIN_URL = "/cuentas/login/"
LOGOUT_URL = "/cuentas/logout/"
LOGIN_REDIRECT_URL = "/tablon/"

TEMPLATE_DIRS = (
	RUTA + "public/templates/",
	RUTA + "public/templates/juego/",
	RUTA + "public/templates/web/",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',

	# Aplicaciones caseras
    'gestion_base',
    'gestion_usuario',
    'gestion_usuario.gestion_notificacion',
    'gestion_sistema.gestion_liga',
    'gestion_sistema.gestion_calendario',
    'gestion_sistema.gestion_jornada',
    'gestion_sistema.gestion_equipo',
    'gestion_sistema.gestion_partido',
    'gestion_sistema.gestion_clasificacion',
    'gestion_sistema.gestion_jugador',

    'gestion_mercado.gestion_subasta',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#DECIMAL_PLACES = 2
NUMBER_GROUPING = 3
THOUSAND_SEPARATOR = '.'
#USE_THOUSAND_SEPARATOR = True