## Client Statuses

---

### List client statuses

**Endpoint:**

GET /api/client-status/

---

**Descripción:**

Obtiene el listado de estados de cliente pertenecientes a la empresa del usuario autenticado.

Este endpoint está protegido, por lo que requiere un **access token válido**.

Los datos se filtran automáticamente por empresa (multi-tenant), evitando que un usuario acceda a estados de otras organizaciones.

---

**Headers:**

---

## Authorization: Bearer <access_token>

---

**Parámetros:**

* No requiere parámetros obligatorios.

---

**Respuesta exitosa (200 OK):**

---

[
{
"id": 8,
"nombre": "Nuevo",
"descripcion": "Cliente recién creado en el sistema",
"orden": 1,
"empresa": "uuid_empresa"
},
{
"id": 9,
"nombre": "Contactado",
"descripcion": "Se ha establecido contacto inicial",
"orden": 2,
"empresa": "uuid_empresa"
}
]
-

---

**Descripción de la respuesta:**

* Se devuelve una lista de estados de cliente.
* Cada estado define una fase dentro del flujo comercial.
* Todos los estados pertenecen a la empresa del usuario autenticado.

---

**Errores posibles:**

* **401 Unauthorized**

---

{
"detail": "Authentication credentials were not provided."
}
-

---

### Create client status

**Endpoint:**

POST /api/client-status/

---

**Descripción:**

Permite crear un nuevo estado de cliente asociado a la empresa del usuario autenticado.

La empresa se asigna automáticamente en el backend a partir del usuario autenticado, por lo que no es necesario enviarla en la petición.

Este endpoint permite personalizar el flujo de clientes dentro del CRM.

---

**Headers:**

---

Authorization: Bearer <access_token>
Content-Type: application/json
------------------------------

---

**Body (request):**

---

{
"nombre": "Cliente activo",
"descripcion": "Cliente con relación activa",
"orden": 3
}
-

---

**Respuesta exitosa (201 Created):**

---

{
"id": 10,
"nombre": "Cliente activo",
"descripcion": "Cliente con relación activa",
"orden": 3,
"empresa": "uuid_empresa"
}
-

---

**Errores posibles:**

* **400 Bad Request**

---

{
"nombre": ["Este campo es obligatorio."]
}
-

* **401 Unauthorized**

---

{
"detail": "Authentication credentials were not provided."
}
-

---

### Retrieve client status

**Endpoint:**

GET /api/client-status/{id}/

---

**Descripción:**

Obtiene la información detallada de un estado de cliente concreto.

El estado debe pertenecer a la empresa del usuario autenticado.

---

**Headers:**

---

## Authorization: Bearer <access_token>

---

**Respuesta exitosa (200 OK):**

---

{
"id": 8,
"nombre": "Nuevo",
"descripcion": "Cliente recién creado en el sistema",
"orden": 1,
"empresa": "uuid_empresa"
}
-

---

### Update client status

**Endpoint:**

PUT /api/client-status/{id}/

---

**Descripción:**

Permite actualizar todos los datos de un estado de cliente existente.

---

**Headers:**

---

Authorization: Bearer <access_token>
Content-Type: application/json
------------------------------

---

**Body (request):**

---

{
"nombre": "Lead",
"descripcion": "Primer contacto comercial",
"orden": 1
}
-

---

**Respuesta exitosa (200 OK):**

---

{
"id": 8,
"nombre": "Lead",
"descripcion": "Primer contacto comercial",
"orden": 1,
"empresa": "uuid_empresa"
}
-

---

### Delete client status

**Endpoint:**

DELETE /api/client-status/{id}/

---

**Descripción:**

Permite eliminar un estado de cliente existente.

---

**Headers:**

---

## Authorization: Bearer <access_token>

---

**Respuesta exitosa (204 No Content):**

* No devuelve contenido.

---

---

### Notas

* Todos los estados pertenecen a la empresa del usuario autenticado (multi-tenant).
* Los estados están ordenados por el campo `orden` y, en caso de empate, por `nombre`.
* El campo `orden` permite definir el flujo lógico del cliente dentro del CRM.
* Cada cliente debe tener un estado asociado.
* Este endpoint se utiliza principalmente para poblar listas desplegables en formularios de clientes.

---

## 👥 Clients

---

### List clients

**Endpoint:**

GET /api/clients/

---

**Descripción:**

Obtiene el listado de clientes pertenecientes a la empresa del usuario autenticado.

Este endpoint está protegido, por lo que requiere un **access token válido**.

Los datos se filtran automáticamente por empresa (multi-tenant), evitando que un usuario acceda a clientes de otras organizaciones.

---

**Headers:**

---

## Authorization: Bearer <access_token>

---

**Parámetros:**

* No requiere parámetros obligatorios.

---

**Respuesta exitosa (200 OK):**

---

[
{
"id": "uuid_cliente",
"nombre": "Nombre del cliente",
"email": "[cliente@email.com](mailto:cliente@email.com)",
"telefono": "600000000",
"empresa": "uuid_empresa",
"estado_cliente": 1
}
]
-

---

**Descripción de la respuesta:**

* Se devuelve una lista de clientes.
* Cada cliente contiene su información básica.
* Todos los clientes pertenecen a la empresa del usuario autenticado.

---

**Errores posibles:**

* **401 Unauthorized**

---

{
"detail": "Authentication credentials were not provided."
}
-

---

### Create client

**Endpoint:**

POST /api/clients/

---

**Descripción:**

Permite crear un nuevo cliente asociado a la empresa del usuario autenticado.

El sistema asigna automáticamente la empresa del usuario, por lo que no es necesario enviarla en la petición.

---

**Headers:**

---

Authorization: Bearer <access_token>
Content-Type: application/json
------------------------------

---

**Body (request):**

---

{
"nombre": "Juan Pérez García",
"tipo": "persona",
"email": "[juan.perez@example.com](mailto:juan.perez@example.com)",
"telefono": "600123456",
"direccion": "Calle Gran Vía 12",
"ciudad": "Madrid",
"pais": "España",
"nif": "12345678A",
"estado_cliente": 1
}
-

---

**Respuesta exitosa (201 Created):**

---

{
"id": "uuid_cliente",
"nombre": "Juan Pérez García",
"email": "[juan.perez@example.com](mailto:juan.perez@example.com)",
"telefono": "600123456",
"empresa": "uuid_empresa",
"estado_cliente": 1
}
-

---

**Errores posibles:**

* **400 Bad Request**

---

{
"email": ["Este campo es obligatorio."]
}
-

* **401 Unauthorized**

---

{
"detail": "Authentication credentials were not provided."
}
-

---

### Retrieve client

**Endpoint:**

GET /api/clients/{id}/

---

**Descripción:**

Obtiene la información detallada de un cliente concreto.

El cliente debe pertenecer a la empresa del usuario autenticado.

---

**Headers:**

---

## Authorization: Bearer <access_token>

---

**Respuesta exitosa (200 OK):**

---

{
"id": "uuid_cliente",
"nombre": "Juan Pérez García",
"email": "[juan.perez@example.com](mailto:juan.perez@example.com)",
"telefono": "600123456",
"empresa": "uuid_empresa",
"estado_cliente": 1
}
-

---

### Update client

**Endpoint:**

PUT /api/clients/{id}/

---

**Descripción:**

Permite actualizar todos los datos de un cliente existente.

---

**Headers:**

---

Authorization: Bearer <access_token>
Content-Type: application/json
------------------------------

---

**Body (request):**

---

{
"nombre": "Nuevo nombre",
"email": "[nuevo@email.com](mailto:nuevo@email.com)"
}
-

---

**Respuesta exitosa (200 OK):**

---

{
"id": "uuid_cliente",
"nombre": "Nuevo nombre",
"email": "[nuevo@email.com](mailto:nuevo@email.com)"
}
-

---

### Delete client

**Endpoint:**

DELETE /api/clients/{id}/

---

**Descripción:**

Permite eliminar un cliente existente.

---

**Headers:**

---

## Authorization: Bearer <access_token>

---

**Respuesta exitosa (204 No Content):**

* No devuelve contenido.

---
