## Oportunidades

---

### Listar oportunidades

**Endpoint:**

GET /api/oportunidades/

---

**Descripción:**

Obtiene el listado de oportunidades comerciales de la empresa del usuario autenticado.

Permite gestionar el pipeline de ventas y realizar seguimiento de posibles negocios.

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
    "cliente": 20,
    "titulo": "Implementación CRM personalizado",
    "descripcion": "Proyecto de implementación adaptado al cliente",
    "valor_estimado": "12000.00",
    "estado": "en_progreso",
    "probabilidad": 40,
    "empresa": "uuid_empresa",
    "usuario_responsable": "uuid_usuario"
  }
]
---

---

### Crear oportunidad

**Endpoint:**

POST /api/oportunidades/

---

**Descripción:**

Permite crear una nueva oportunidad comercial.

La empresa y el usuario responsable se asignan automáticamente desde el usuario autenticado.

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
  "cliente": 20,
  "titulo": "Nueva oportunidad de negocio",
  "descripcion": "Proyecto de desarrollo a medida",
  "valor_estimado": "8000.00",
  "estado": "abierta",
  "probabilidad": 30,
  "fecha_cierre_prevista": "2026-04-01T10:00:00Z"
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": 2,
  "cliente": 20,
  "titulo": "Nueva oportunidad de negocio",
  "descripcion": "Proyecto de desarrollo a medida",
  "valor_estimado": "8000.00",
  "estado": "abierta",
  "probabilidad": 30,
  "empresa": "uuid_empresa",
  "usuario_responsable": "uuid_usuario"
}
---

---

## Actividades

---

### Listar actividades

**Endpoint:**

GET /api/actividades/

---

**Descripción:**

Obtiene el listado de actividades comerciales registradas.

Permite visualizar el historial de interacciones con clientes y oportunidades.

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
    "tipo": "llamada",
    "descripcion": "Llamada inicial con el cliente",
    "fecha": "2026-03-20T10:00:00Z",
    "completada": true,
    "cliente": 20,
    "oportunidad": 1,
    "empresa": "uuid_empresa",
    "usuario": "uuid_usuario"
  }
]
---

---

### Crear actividad

**Endpoint:**

POST /api/actividades/

---

**Descripción:**

Permite registrar una nueva actividad comercial.

Las actividades representan interacciones como llamadas, emails, reuniones o tareas.

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
  "cliente": 20,
  "oportunidad": 1,
  "tipo": "llamada",
  "descripcion": "Llamada inicial para presentar los servicios",
  "fecha": "2026-03-20T10:00:00Z",
  "completada": true
}
---

---

**Respuesta exitosa (201 Created):**

---
{
  "id": 1,
  "tipo": "llamada",
  "descripcion": "Llamada inicial para presentar los servicios",
  "fecha": "2026-03-20T10:00:00Z",
  "completada": true,
  "cliente": 20,
  "oportunidad": 1,
  "empresa": "uuid_empresa",
  "usuario": "uuid_usuario"
}
---

---

### Notas

- Todas las oportunidades y actividades están filtradas por empresa (multi-tenant)
- Los campos `empresa` y `usuario` se asignan automáticamente
- El campo `tipo` en actividades puede ser:
  - llamada
  - email
  - reunion
  - tarea
- Las actividades permiten llevar un historial completo de interacciones con el cliente
- Las oportunidades permiten gestionar el ciclo de ventas dentro del CRM