## 👤 Usuarios

---

### Listar usuarios

**Endpoint:**

GET /api/users/

---

**Descripción:**

Obtiene el listado de usuarios pertenecientes a la empresa del usuario autenticado.

Este endpoint está protegido, por lo que requiere un **access token válido**.

Los datos se filtran automáticamente por empresa (multi-tenant), evitando que un usuario acceda a usuarios de otras organizaciones.

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Parámetros:**

- No requiere parámetros obligatorios.

---

**Respuesta exitosa (200 OK):**

---
[
  {
    "id": "uuid_usuario",
    "email": "admin@empresa.com",
    "rol": "uuid_rol",
    "empresa": "uuid_empresa",
    "fecha_creacion": "2026-04-15T10:00:00Z"
  }
]
---

---

**Descripción de la respuesta:**

- Se devuelve una lista de usuarios.
- Cada usuario incluye su email, rol y empresa.
- Todos los usuarios pertenecen a la empresa del usuario autenticado.

---

**Errores posibles:**

- **401 Unauthorized**

---
{
  "detail": "Authentication credentials were not provided."
}
---

---

### Crear usuario

**Endpoint:**

POST /api/users/

---

**Descripción:**

Permite crear un nuevo usuario dentro de la empresa del usuario autenticado.

La empresa se asigna automáticamente en el backend, por lo que **no debe enviarse en la petición**.

Solo los usuarios con rol de **Administrador** pueden realizar esta acción.

Además, el sistema valida que el rol asignado pertenezca a la misma empresa.

---

**Headers:**

---
Authorization: Bearer <access_token>  
Content-Type: application/json
---

---

**Body (request):**

---
{
  "email": "nuevo@empresa.com",
  "password": "1234",
  "rol": "uuid_rol"
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": "uuid_usuario",
  "email": "nuevo@empresa.com",
  "rol": "uuid_rol",
  "empresa": "uuid_empresa",
  "fecha_creacion": "2026-04-15T10:00:00Z"
}
---

---

**Errores posibles:**

- **400 Bad Request**

---
{
  "rol": ["El rol seleccionado no pertenece a tu empresa"]
}
---

- **401 Unauthorized**

---
{
  "detail": "Authentication credentials were not provided."
}
---

- **403 Forbidden**

---
{
  "detail": "No tienes permisos para realizar esta acción."
}
---

---

### Obtener detalle de usuario

**Endpoint:**

GET /api/users/{id}/

---

**Descripción:**

Obtiene la información detallada de un usuario concreto.

El usuario debe pertenecer a la empresa del usuario autenticado.

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (200 OK):**

---
{
  "id": "uuid_usuario",
  "email": "admin@empresa.com",
  "rol": "uuid_rol",
  "empresa": "uuid_empresa",
  "fecha_creacion": "2026-04-15T10:00:00Z"
}
---

---

### Actualizar usuario

**Endpoint:**

PUT /api/users/{id}/

---

**Descripción:**

Permite actualizar los datos de un usuario existente.

Solo los administradores pueden realizar esta acción.

La empresa no puede modificarse, ya que se asigna automáticamente en el backend.

---

**Headers:**

---
Authorization: Bearer <access_token>  
Content-Type: application/json
---

---

**Body (request):**

---
{
  "email": "nuevo@email.com",
  "rol": "uuid_rol"
}
---

---

**Respuesta exitosa (200 OK):**

---
{
  "id": "uuid_usuario",
  "email": "nuevo@email.com",
  "rol": "uuid_rol",
  "empresa": "uuid_empresa",
  "fecha_creacion": "2026-04-15T10:00:00Z"
}
---

---

### Eliminar usuario

**Endpoint:**

DELETE /api/users/{id}/

---

**Descripción:**

Permite eliminar un usuario existente.

Solo los administradores pueden realizar esta acción.

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (204 No Content):**

- No devuelve contenido.

---

---

### Notas

- Todos los usuarios pertenecen a la empresa del usuario autenticado (multi-tenant).
- La empresa se asigna automáticamente en creación y actualización.
- Solo los administradores pueden crear, editar o eliminar usuarios.
- El rol debe pertenecer a la misma empresa del usuario autenticado.
- El campo `password` solo se utiliza en la creación y nunca se devuelve en la respuesta.
- Los identificadores (`id`, `rol`, `empresa`) son UUID.