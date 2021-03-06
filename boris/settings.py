# coding=utf-8

import os,sys
from os.path import join
PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

# Django settings for boris project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'admin@admin.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'rocky_dev.db',          # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

#for the defined site translations
#first locale code, then language in its own descriptor
LANGUAGES = (('en', 'English'),
             ('es', 'Español'),
             ('ur', 'اردو'),
             ('bn', 'বাংলা'),
             ('zh', '中文（简体）'),
             ('zh-TW', '中文（繁体）'),
             ('ja', '日本語'),
             ('km', 'ភាសាខ្មែរ'),
             ('ko', '한국어'),
             ('ilo', 'Ilocano'),
             ('hi', 'अंग्रेज़ी'),
             ('tl', 'Tagalog'),
             ('th', 'ภาษาอังกฤษ'),
             ('vi', 'Bằng Tiếng Việt')
             )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH,'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH,'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    MEDIA_ROOT,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

#STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE =  'django.contrib.staticfiles.storage.StaticFilesStorage'
AWS_QUERYSTRING_AUTH = False
from boto.s3.connection import OrdinaryCallingFormat
AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #cache first
    'django.middleware.cache.UpdateCacheMiddleware',
    #then redirection
    'sslify.middleware.SSLifyMiddleware',
    'registrant.middleware.ResponseInjectP3PMiddleware',
    #then session, locale, mobile
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'registrant.middleware.MobileDetectionMiddleware',
    #then django common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #then facebook
    'facebook.middleware.FacebookCanvasMiddleware',
    #and finally cache
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'boris.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH,'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request", #add so we can access session in templates
    "registrant.context_processors.source",
    "registrant.context_processors.whitelabel",
    "registrant.context_processors.facebook",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    #3rd party packages for deployment
    'storages',
    'gunicorn',
    'django_evolution',
    'raven.contrib.django.raven_compat',
    #internal apps
    'registrant',
    'proxy',
    'ziplookup'
    )

#use sentry logging, don't email admins directly
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'suds.client': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

LOCALE_PATHS = (os.path.join(PROJECT_PATH,'locale'),)

EMAIL_SUBJECT_PREFIX = "[Rocky-Boris] "

def get_cache():
    import os
    try:
        os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
        os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
        os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
        return {
          'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'LOCATION': os.environ['MEMCACHIER_SERVERS'],
            'TIMEOUT': 500,
            'BINARY': True,
          }
        }
    except:
        return {
          'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
          }
        }

CACHES = get_cache()

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

CSRF_FAILURE_VIEW = 'registrant.views.csrf_failure'

FACEBOOK_APP_SECRET = "" #local testing id, actual is in the environ

#maps facebook page ids to partner ids
FACEBOOK_PARTNERS_MAP = {'422539957805075':9937} #local testing

try:
    from settings_local import *
except:
    #we're on Heroku, sensitive info is in environ
    DEBUG = False
    PROXY_DOMAIN = "rtvstaging.osuosl.org"
    #changed for testing
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
    #facebook settings
    FACEBOOK_APP_SECRET = os.environ['FACEBOOK_APP_SECRET']
    #sendgrid settings
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST= 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    #s3 settings
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_CUSTOM_DOMAIN = os.environ['AWS_S3_CUSTOM_DOMAIN']
    STATIC_URL = 'https://'+AWS_S3_CUSTOM_DOMAIN
    #storage
    DEFAULT_FILE_STORAGE = 'storage.MediaRootS3BotoStorage'
    STATICFILES_STORAGE = 'storage.StaticRootS3BotoStorage'
    #STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
    #use heroku db
    import dj_database_url
    #DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}
    DATABASES['default'] =  dj_database_url.config()
    #sentry
    SENTRY_DSN = os.environ['SENTRY_DSN']
