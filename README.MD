# 📧 Sales Mails CRM

CRM orientado a campañas de email desarrollado con Django y Django REST Framework.

Este sistema permite gestionar:

* Clientes
* Estados de cliente
* Campañas de email
* Plantillas de correo
* Envíos individuales y masivos

Además, implementa un sistema multiempresa (multi-tenant), donde cada usuario solo puede acceder a los datos de su propia organización.

---

# Puesta en marcha del proyecto

A continuación se detallan los pasos necesarios para ejecutar el proyecto desde cero.

---

## 1. Clonar el repositorio

git clone <url-del-repositorio>
cd sales-mails-crm

---

## 2. Crear y activar entorno virtual

python -m venv .venv

### Activar en Windows:

.venv\Scripts\activate

### Activar en Linux/Mac:

source .venv/bin/activate

---

## 3. Instalar dependencias

pip install -r requirements.txt

---

## 4. Configurar variables de entorno

Este proyecto utiliza django-environ para la gestión de variables de entorno.

Debes crear un archivo .env en la raíz del proyecto con la configuración de base de datos.

Ejemplo:

DEBUG=True

DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432

---

## 5. Aplicar migraciones

Este paso crea la estructura de la base de datos:

python manage.py makemigrations
python manage.py migrate

---

## 6. Inicializar datos del sistema (IMPORTANTE)

Debido a la arquitectura multiempresa, no es posible crear un superusuario con el comando estándar de Django.

Por ello, hemos implementado un comando personalizado que crea automáticamente:

* Empresa por defecto
* Rol administrador
* Usuario administrador

Ejecutar:

python manage.py init_admin

### Credenciales por defecto:

Email: [admin@crm.com](mailto:admin@crm.com)
Password: admin123

---

## 7. Ejecutar el servidor

python manage.py runserver

El sistema estará disponible en:

http://127.0.0.1:8000/

---

# Autenticación

El sistema utiliza JWT (JSON Web Tokens).

Para obtener un token:

POST /api/token/

---

# Arquitectura del proyecto

El sistema está dividido en módulos principales:

* core → lógica base (multiempresa, utilidades)
* users → usuarios, roles y permisos
* clients → gestión de clientes y estados
* campaigns → campañas, plantillas y envíos

---

# Multiempresa (Multi-Tenant)

Todo el sistema está diseñado para trabajar con múltiples empresas:

* Cada usuario pertenece a una empresa
* Los datos se filtran automáticamente por empresa
* Se evita el acceso cruzado entre organizaciones

Esto se implementa mediante:

* TenantModel
* TenantManager
* Validaciones en serializers
* Filtros en ViewSets

---

# Seguridad

El sistema incluye:

* Autenticación JWT
* Permisos por rol (Administrador / Comercial)
* Aislamiento de datos por empresa
* Validaciones a nivel de backend y base de datos

---

# Autoría

Proyecto desarrollado como práctica de backend, aplicando:

* Arquitectura modular
* Multiempresa real
* Buenas prácticas en Django REST Framework
* Validaciones y seguridad en APIs
