## 👥 Clientes

---

### Listar clientes

**Endpoint:**

GET /api/clientes/

---

**Descripción:**

Obtiene el listado de clientes pertenecientes a la empresa del usuario autenticado.

Este endpoint está protegido, por lo que requiere un **access token válido**.

Los datos se filtran automáticamente por empresa (multi-tenant), evitando que un usuario acceda a clientes de otras organizaciones.

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
    "id": "uuid_cliente",
    "nombre": "Nombre del cliente",
    "email": "cliente@email.com",
    "telefono": "600000000",
    "empresa": "uuid_empresa",
    "estado_cliente": 1
  }
]
---

---

**Descripción de la respuesta:**

- Se devuelve una lista de clientes.
- Cada cliente contiene su información básica.
- Todos los clientes pertenecen a la empresa del usuario autenticado.

---

**Errores posibles:**

- **401 Unauthorized**

---
{
  "detail": "Authentication credentials were not provided."
}
---

---

### Crear cliente

**Endpoint:**

POST /api/clientes/

---

**Descripción:**

Permite crear un nuevo cliente asociado a la empresa del usuario autenticado.

El sistema asigna automáticamente la empresa del usuario, por lo que no es necesario enviarla en la petición.

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
  "nombre": "Juan Pérez García",
  "tipo": "persona",
  "email": "juan.perez@example.com",
  "telefono": "600123456",
  "direccion": "Calle Gran Vía 12",
  "ciudad": "Madrid",
  "pais": "España",
  "nif": "12345678A",
  "estado_cliente": 1
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": "uuid_cliente",
  "nombre": "Juan Pérez García",
  "email": "juan.perez@example.com",
  "telefono": "600123456",
  "empresa": "uuid_empresa",
  "estado_cliente": 1
}
---

---

**Errores posibles:**

- **400 Bad Request**

---
{
  "email": ["Este campo es obligatorio."]
}
---

- **401 Unauthorized**

---
{
  "detail": "Authentication credentials were not provided."
}
---

---

### Obtener detalle de cliente

**Endpoint:**

GET /api/clientes/{id}/

---

**Descripción:**

Obtiene la información detallada de un cliente concreto.

El cliente debe pertenecer a la empresa del usuario autenticado.

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (200 OK):**

---
{
  "id": "uuid_cliente",
  "nombre": "Juan Pérez García",
  "email": "juan.perez@example.com",
  "telefono": "600123456",
  "empresa": "uuid_empresa",
  "estado_cliente": 1
}
---

---

### Actualizar cliente

**Endpoint:**

PUT /api/clientes/{id}/

---

**Descripción:**

Permite actualizar todos los datos de un cliente existente.

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
  "nombre": "Nuevo nombre",
  "email": "nuevo@email.com"
}
---

---

**Respuesta exitosa (200 OK):**

---
{
  "id": "uuid_cliente",
  "nombre": "Nuevo nombre",
  "email": "nuevo@email.com"
}
---

---

### Eliminar cliente

**Endpoint:**

DELETE /api/clientes/{id}/

---

**Descripción:**

Permite eliminar un cliente existente.

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

### Estados de cliente

**Endpoint:**

GET /api/estado-clientes/

---

**Descripción:**

Obtiene el listado de estados de cliente disponibles para la empresa del usuario autenticado.

Los estados de cliente se utilizan para clasificar la situación de cada cliente dentro del sistema (por ejemplo: activo, inactivo, perdido, etc.).

Este endpoint está protegido y los datos se filtran automáticamente por empresa (multi-tenant).

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Parámetros:**

- No requiere parámetros.

---

**Respuesta exitosa (200 OK):**

---
[
  {
    "id": 1,
    "nombre": "Lead",
    "descripcion": "Primer contacto",
    "orden": 1,
    "empresa": "uuid_empresa"
  },
  {
    "id": 2,
    "nombre": "Cliente",
    "descripcion": "Cliente activo",
    "orden": 2,
    "empresa": "uuid_empresa"
  },
  {
    "id": 3,
    "nombre": "Inactivo",
    "descripcion": "Cliente sin actividad",
    "orden": 3,
    "empresa": "uuid_empresa"
  }
]
---

---

**Descripción de la respuesta:**

- **id**: Identificador único del estado.
- **nombre**: Nombre del estado.
- **descripcion**: Descripción opcional del estado.
- **orden**: Valor numérico utilizado para ordenar los estados.
- **empresa**: Identificador de la empresa a la que pertenece el estado.

---

**Errores posibles:**

- **401 Unauthorized**

---
{
  "detail": "Authentication credentials were not provided."
}
---

---

**Notas:**

- Todos los estados devueltos pertenecen a la empresa del usuario autenticado.
- Los estados están ordenados por el campo `orden` y, en caso de empate, por `nombre`.
- Cada cliente debe tener siempre un estado asociado.
- Este endpoint se utiliza normalmente para poblar listas desplegables en formularios de clientes.

### Crear estado de cliente

**Endpoint:**

POST /api/estado-clientes/

---

**Descripción:**

Permite crear un nuevo estado de cliente asociado a la empresa del usuario autenticado.

Los estados se utilizan para clasificar la situación de los clientes dentro del CRM (por ejemplo: lead, cliente activo, inactivo, etc.).

La empresa se asigna automáticamente a partir del usuario autenticado.

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
  "nombre": "Cliente activo",
  "descripcion": "Cliente con relación activa",
  "orden": 2
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": 2,
  "nombre": "Cliente activo",
  "descripcion": "Cliente con relación activa",
  "orden": 2,
  "empresa": "uuid_empresa"
}
---

---

**Errores posibles:**

- **400 Bad Request**

---
{
  "nombre": ["Este campo es obligatorio."]
}
---

- **401 Unauthorized**

---
{
  "detail": "Authentication credentials were not provided."
}
---

---

**Notas:**

- El estado se crea siempre dentro de la empresa del usuario autenticado.
- El campo `orden` permite definir el orden en el que se mostrarán los estados.
- Este endpoint permite personalizar el flujo de clientes dentro del CRM.