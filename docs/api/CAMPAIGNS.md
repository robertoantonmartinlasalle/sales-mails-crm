## Campañas

---

### Plantillas de email

---

#### Listar plantillas

**Endpoint:**

GET /api/templates/

---

**Descripción:**

Obtiene el listado de plantillas de email disponibles.

Las plantillas contienen el asunto y el cuerpo del mensaje que se utilizará en las campañas.

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (200 OK):**

---
[
  {
    "id": 1,
    "nombre": "Bienvenida",
    "asunto": "Bienvenido a nuestro servicio",
    "cuerpo": "Hola {{nombre}}, gracias por registrarte."
  }
]
---

---

#### Crear plantilla

**Endpoint:**

POST /api/templates/

---

**Descripción:**

Permite crear una nueva plantilla de email.

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
  "nombre": "Bienvenida",
  "asunto": "Bienvenido",
  "cuerpo": "Hola {{nombre}}, gracias por confiar en nosotros."
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": 1,
  "nombre": "Bienvenida",
  "asunto": "Bienvenido",
  "cuerpo": "Hola {{nombre}}, gracias por confiar en nosotros."
}
---

---

### Campañas de email

---

#### Listar campañas

**Endpoint:**

GET /api/campaigns/

---

**Descripción:**

Obtiene el listado de campañas de email de la empresa del usuario autenticado.

Cada campaña utiliza una plantilla de email.

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (200 OK):**

---
[
  {
    "id": 1,
    "nombre": "Campaña bienvenida",
    "descripcion": "Primera campaña",
    "plantilla": 1,
    "empresa": "uuid_empresa",
    "fecha_creacion": "2026-03-20T10:00:00Z"
  }
]
---

---

#### Crear campaña

**Endpoint:**

POST /api/campaigns/

---

**Descripción:**

Permite crear una nueva campaña asociada a una plantilla.

La empresa se asigna automáticamente desde el usuario autenticado.

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
  "nombre": "Campaña bienvenida",
  "descripcion": "Primera campaña",
  "plantilla": 1
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": 1,
  "nombre": "Campaña bienvenida",
  "descripcion": "Primera campaña",
  "plantilla": 1,
  "empresa": "uuid_empresa",
  "fecha_creacion": "2026-03-20T10:00:00Z"
}
---

---

### Envíos de campañas

---

#### Listar envíos

**Endpoint:**

GET /api/campaign-sends/

---

**Descripción:**

Obtiene el listado de envíos de campañas pertenecientes a la empresa del usuario autenticado.

Cada envío representa el envío de una campaña a un cliente.

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (200 OK):**

---
[
  {
    "id": 1,
    "campana": 1,
    "cliente": 5,
    "estado": "pendiente",
    "fecha_envio": null,
    "empresa": "uuid_empresa"
  }
]
---

---

#### Crear envío

**Endpoint:**

POST /api/campaign-sends/

---

**Descripción:**

Permite crear un envío de campaña para un cliente.

El envío se crea inicialmente con estado **pendiente**.

La empresa se asigna automáticamente.

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
  "campana": 1,
  "cliente": 5
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": 1,
  "campana": 1,
  "cliente": 5,
  "estado": "pendiente",
  "fecha_envio": null,
  "empresa": "uuid_empresa"
}
---

---

### Acciones de envío

---

#### Enviar campaña individual

**Endpoint:**

POST /api/campaign-sends/{id}/send/

---

**Descripción:**

Envía una campaña a un cliente específico.

Flujo interno:

- Solo permite envíos en estado **pendiente**
- Sustituye `{{nombre}}` en el cuerpo del email
- Envía el email real
- Actualiza estado:
  - "enviado" si todo va bien
  - "error" si falla

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (200 OK):**

---
{
  "message": "Campaña enviada correctamente."
}
---

---

**Errores posibles:**

- **400 Bad Request**

---
{
  "error": "Este envío ya fue procesado."
}
---

- **500 Internal Server Error**

---
{
  "error": "Error al enviar el email."
}
---

---

#### Envío masivo de campañas

**Endpoint:**

POST /api/campaign-sends/send-bulk/

---

**Descripción:**

Envía todas las campañas en estado **pendiente** de la empresa del usuario autenticado.

Flujo interno:

- Filtra envíos pendientes
- Envía uno a uno
- Actualiza estado:
  - "enviado"
  - "error"
- Devuelve resumen final

---

**Headers:**

---
Authorization: Bearer <access_token>
---

---

**Respuesta exitosa (200 OK):**

---
{
  "total": 10,
  "enviados": 8,
  "errores": 2
}
---

---

**Notas:**

- Todos los datos están filtrados por empresa (multi-tenant).
- El campo `estado` puede ser:
  - pendiente
  - enviado
  - error
- El campo `fecha_envio` solo se completa cuando el envío se realiza correctamente.
- El sistema permite personalización de emails mediante variables como `{{nombre}}`.