# Instalación del proyecto CRM Django

Esta guía describe los pasos necesarios para preparar un entorno de desarrollo
local para el proyecto **sales-mails-crm**, usando Python, entorno virtual y PostgreSQL.

---

## 1. Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.11 o superior
- pip (incluido con Python)
- Git
- PostgreSQL (en local)

Comprobar versiones:

```bash
py --version
pip --version
git --version
```
---

## 2. Clonar el repositorio

```bash
git clone https://github.com/robertoantonmartinlasalle/sales-mails-crm.git
cd sales-mails-crm
```

---

## 3. Crear y activar entorno virtual

```bash
py -m venv .venv
.venv\Scripts\activate
```

---

## 4. Instalación de dependencias

Instalar dependencias principales del proyecto:

```bash
pip install django
pip install psycopg[binary]
pip install django-environ
pip install djangorestframework
pip install django-cors-headers
pip install djangorestframework-simplejwt
pip install django-jazzmin
```
Guardar dependencias:

```bash
pip freeze > requirements.txt
```
Instalar requirements.txt

```bash
pip install -r requirements.txt
```

---
## 5. Crear el proyecto Django

crea la estructura base del proyecto Django dentro del repositorio

```bash
django-admin startproject config .
```

---

## 6. Configuración de variables de entorno

Generar una clave secreta del proyecto:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Crear un archivo .env en la raíz del proyecto y añadir:
```env
SECRET_KEY=clave_generada
DEBUG=True
```

---

## 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```
---

## 8. Crear aplicaciones Django

```bash
python manage.py startapp nombre_app
```
