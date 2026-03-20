## Autenticación

### Login de usuario

**Endpoint:**

POST /api/auth/login/

---

**Descripción:**

Permite autenticar un usuario en el sistema mediante su email y contraseña.

Si las credenciales son correctas, el sistema devuelve:

- Un **access token** (para autenticación en peticiones)
- Un **refresh token** (para renovar el access)
- Información básica del usuario autenticado

Este sistema utiliza **JSON Web Tokens (JWT)**, por lo que no se gestionan sesiones en el servidor.

---

**Headers:**

Content-Type: application/json

---

**Body (request):**

---
{
  "email": "Tu email",
  "password": "Tu contraseña"
}
---

---

**Respuesta exitosa (200 OK):**

---
{
  "refresh": "token_refresh",
  "access": "token_access",
  "user": {
    "id": "uuid_usuario",
    "email": "Tu email",
    "empresa_id": "uuid_empresa",
    "rol": "Tu rol"
  }
}
---

---

**Descripción de la respuesta:**

- **access**: Token JWT utilizado para autenticar las peticiones a la API.
- **refresh**: Token utilizado para generar nuevos access tokens cuando expiren.
- **user**: Información básica del usuario autenticado.

---

**Errores posibles:**

- **400 Bad Request**

---
{
  "detail": "Credenciales inválidas"
}
---

- **401 Unauthorized**

---
{
  "detail": "Usuario inactivo"
}
---

---

**Notas:**

- El access token debe enviarse en las siguientes peticiones mediante el header:

---
Authorization: Bearer <access_token>
---

- Este endpoint es público (no requiere autenticación previa).
- El sistema está preparado para arquitectura multiempresa (multi-tenant).



### Renovación de token (Refresh)

**Endpoint:**

POST /api/auth/refresh/

---

**Descripción:**

Permite obtener un nuevo **access token** a partir de un **refresh token** válido.

Este endpoint se utiliza cuando el access token ha expirado, evitando que el usuario tenga que volver a autenticarse con email y contraseña.

---

**Headers:**

Content-Type: application/json

---

**Body (request):**

---
{
  "refresh": "tu_refresh_token"
}
---

---

**Respuesta exitosa (200 OK):**

---
{
  "access": "nuevo_access_token"
}
---

---

**Descripción de la respuesta:**

- **access**: Nuevo token JWT que sustituye al anterior una vez expirado.

---

**Errores posibles:**

- **401 Unauthorized**

---
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
---

---

**Notas:**

- Este endpoint no requiere enviar el header Authorization.
- El refresh token tiene mayor duración que el access token.
- Se recomienda almacenar el refresh token de forma segura en el cliente.
- Este endpoint es fundamental para mantener la sesión activa sin necesidad de re-login.


### Uso del token en endpoints protegidos

**Descripción:**

Una vez autenticado el usuario mediante el endpoint de login, el **access token** debe incluirse en todas las peticiones a endpoints protegidos.

Este token permite al servidor identificar al usuario y validar sus permisos.

---

**Header requerido:**

---
Authorization: Bearer <access_token>
---

---

**Ejemplo de petición:**

GET /api/clients/

Headers:

---
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
---

---

**Comportamiento del sistema:**

- Si el token es válido:
  - La petición se procesa correctamente.
  - El sistema identifica al usuario mediante `request.user`.

- Si el token no se envía:
  - Se devuelve error 401 Unauthorized.

- Si el token es inválido o ha expirado:
  - Se devuelve error 401 Unauthorized.
  - El cliente deberá utilizar el endpoint de refresh para obtener un nuevo access token.

---

**Errores posibles:**

- **401 Unauthorized**

---
{
  "detail": "Authentication credentials were not provided."
}
---

- **401 Unauthorized (token inválido o expirado)**

---
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
---

---

**Notas:**

- El prefijo **Bearer** es obligatorio y distingue el tipo de autenticación.
- El sistema no utiliza sesiones ni cookies, únicamente tokens JWT.
- El usuario autenticado estará disponible en el backend mediante:

---
request.user
---

- Este sistema permite implementar control de acceso por empresa (multi-tenant) y por rol.