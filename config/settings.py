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


# =========================================================
# BASE_DIR
# =========================================================
# BASE_DIR representa la raíz del proyecto. Se utiliza para
# construir rutas relativas dentro de la aplicación.

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# CARGA DE VARIABLES DE ENTORNO
# =========================================================
# Se utiliza la librería django-environ para leer las
# variables definidas en el archivo .env.
#
# Esto permite:
# - No incluir credenciales en el código
# - Tener configuraciones diferentes según el entorno
#   (desarrollo, testing, producción)

env = environ.Env()

# Cargar archivo .env desde la raíz del proyecto
environ.Env.read_env(BASE_DIR / ".env")


# =========================================================
# CONFIGURACIÓN BÁSICA DE DJANGO
# =========================================================

# Clave secreta usada por Django para seguridad interna
SECRET_KEY = env("SECRET_KEY")

# Activar modo debug en desarrollo
DEBUG = env.bool("DEBUG", default=False)

# Hosts permitidos para acceder a la aplicación
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


# =========================================================
# APLICACIONES INSTALADAS
# =========================================================
# Aquí se registran todas las aplicaciones que forman
# parte del proyecto.

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
]


# =========================================================
# MIDDLEWARE
# =========================================================
# El middleware es una capa intermedia que procesa las
# peticiones y respuestas HTTP.

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
# Aunque este proyecto será principalmente un backend API,
# Django requiere esta configuración para algunas
# funcionalidades internas.

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
# El proyecto utiliza PostgreSQL como base de datos
# principal. Las credenciales se cargan desde el archivo
# .env para evitar exponerlas en el código.

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

# Directorio donde se recopilarán los archivos estáticos
# en un entorno de producción
STATIC_ROOT = BASE_DIR / "staticfiles"


# =========================================================
# CONFIGURACIÓN DE EMAIL
# =========================================================
# Esta configuración será utilizada en el futuro para
# el sistema de envío de campañas del CRM.

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
# Django utilizará el modelo Usuario definido en la app users
# como modelo principal de autenticación del sistema.

AUTH_USER_MODEL = "users.Usuario"