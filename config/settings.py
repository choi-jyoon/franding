"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from django.urls import reverse_lazy
from dotenv import load_dotenv

load_dotenv()
DJANGO_SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT=os.getenv('DB_PORT')
DB_NAME=os.getenv('DB_NAME')
DB_HOST=os.getenv('DB_HOST')
GOOGLE_CLIEND_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_KEY = os.getenv('GOOGLE_KEY')
KAKAO_CLIENT_ID = os.getenv('KAKAO_CLIENT_ID')
KAKAO_KEY = os.getenv('KAKAO_KEY')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME  = os.getenv('AWS_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'widget_tweaks', 
    
    'item',
    'mypage',
    'review',
    'seller',
    'cart',
    'chatbot',
    # 'bootstrap4',
    'payment',
    'event',
    'subscribe',
    'guide',
    #allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #provider
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',
    
    # 'rest_framework',
    'QnA',
    # 'debug_toolbar',
    'django_filters',
    # storage
    'storages',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utils.context_processors.get_profile_image',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': 'postgres',
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,  # 또는 PostgreSQL 서버의 IP 주소
        'PORT': DB_PORT,       # PostgreSQL의 기본 포트 번호
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR/'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',
)


SITE_ID = 1

SOCIALACCOUNT_LOGIN_ON_GET = True
LOGIN_REDIRECT_URL='mypage:add_user_info'
# LOGOUT_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL = 'login'
# ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy('accountapp:login')
ACCOUNT_LOGOUT_ON_GET = True


MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/'media'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
# ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1', '[::1]']

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://54.180.201.192:16379',  # Redis 서버 위치
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}



INTERNAL_IPS = [
    # ...,
    '127.0.0.1',
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}


# 소셜 로그인을 위한 키와 시크릿 설정

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIEND_ID, 
            'secret': GOOGLE_KEY, 
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'kakao': {
        'APP': {
            'client_id': KAKAO_CLIENT_ID,
            'secret': KAKAO_KEY, 
            'key': ''
        }
    }
}

# Email 설정
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_PASSWORD
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# AWS settings
AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME =  AWS_BUCKET_NAME
AWS_S3_REGION_NAME = AWS_S3_REGION_NAME
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

# Static files (CSS, JavaScript, Images)
# AWS_STATIC_LOCATION = 'static'
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
# STATICFILES_STORAGE = 'config.storage_backends.StaticStorage'

# Media files (uploads)
AWS_MEDIA_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'