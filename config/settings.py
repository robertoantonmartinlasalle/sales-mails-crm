"""
Configuración principal de Django para el proyecto Sales Mails CRM.

Este archivo se ha adaptado para utilizar variables de entorno mediante
la librería django-environ. De esta forma se separa la configuración del
código fuente, evitando exponer información sensible (como claves secretas
o credenciales de base de datos) en el repositorio.

Las variables se almacenan en un archivo `.env` ubicado en la raíz del
proyecto.
"""

from pathlib import Path
import environ
from datetime import timedelta  # 🔐 Necesario para configurar JWT


# =========================================================
# BASE_DIR
# =========================================================
# BASE_DIR representa la raíz del proyecto. Se utiliza para
# construir rutas relativas dentro de la aplicación.

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# CARGA DE VARIABLES DE ENTORNO
# =========================================================

env = environ.Env()

# Cargar archivo .env desde la raíz del proyecto
environ.Env.read_env(BASE_DIR / ".env")


# =========================================================
# CONFIGURACIÓN BÁSICA DE DJANGO
# =========================================================

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


# =========================================================
# APLICACIONES INSTALADAS
# =========================================================

INSTALLED_APPS = [
    # Aplicaciones internas de Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Librerías externas
    "rest_framework",
    "corsheaders",

    # Aplicaciones propias del proyecto
    "core",
    "users",
    "clients",
    "campaigns",
    "crm",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# CONFIGURACIÓN DE URLS
# =========================================================

ROOT_URLCONF = "config.urls"


# =========================================================
# CONFIGURACIÓN DE TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================================================
# CONFIGURACIÓN WSGI
# =========================================================

WSGI_APPLICATION = "config.wsgi.application"


# =========================================================
# BASE DE DATOS
# =========================================================

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}


# =========================================================
# VALIDADORES DE CONTRASEÑA
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================================================
# INTERNACIONALIZACIÓN
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =========================================================
# ARCHIVOS ESTÁTICOS
# =========================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# =========================================================
# CONFIGURACIÓN DE EMAIL
# =========================================================

EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)


# =========================================================
# CONFIGURACIÓN DE ID POR DEFECTO
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# MODELO DE USUARIO PERSONALIZADO
# =========================================================

AUTH_USER_MODEL = "users.Usuario"


# =========================================================
# CONFIGURACIÓN DE DJANGO REST FRAMEWORK (JWT)
# =========================================================
# Aquí definimos cómo se autentican las peticiones a nuestra API.
# En lugar de usar sesiones (cookies), usaremos JWT (tokens).

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Autenticación basada en JSON Web Tokens
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}


# =========================================================
# CONFIGURACIÓN DE JSON WEB TOKENS (JWT)
# =========================================================
# Aquí controlamos cómo se generan y validan los tokens.

SIMPLE_JWT = {
    # Tiempo de vida del token de acceso (el que se envía en cada request)
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),

    # Tiempo de vida del refresh token (para renovar sesión)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),

    # Tipo de cabecera esperada en las peticiones
    # Authorization: Bearer <token>
    "AUTH_HEADER_TYPES": ("Bearer",),

    # IMPORTANTE:
    # De momento NO cambiamos el campo de login (username/email)
    # Esto lo haremos en el siguiente paso con un serializer custom
}