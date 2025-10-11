# Batería de Tests de Caja Negra - TFG IBEX

## 1. MÓDULO DE AUTENTICACIÓN Y REGISTRO

### TC-AUTH-001: Registro de Usuario Nuevo
| Campo | Valor |
|-------|-------|
| **ID** | TC-AUTH-001 |
| **Descripción** | Verificar registro exitoso de nuevo usuario |
| **Precondiciones** | Usuario no registrado previamente |
| **Entrada** | Email: test@example.com, Password: Test1234!, Username: testuser |
| **Pasos** | 1. Acceder a /register/<br>2. Completar formulario<br>3. Enviar registro |
| **Salida Esperada** | Usuario creado, redirección a login |
| **Prioridad** | Alta |

### TC-AUTH-002: Registro con Email Duplicado
| Campo | Valor |
|-------|-------|
| **ID** | TC-AUTH-002 |
| **Descripción** | Verificar rechazo de email duplicado |
| **Precondiciones** | Email ya registrado en el sistema |
| **Entrada** | Email existente: admin@tfgibex.com |
| **Pasos** | 1. Acceder a /register/<br>2. Usar email existente<br>3. Enviar |
| **Salida Esperada** | Error: "Email ya registrado" |
| **Prioridad** | Alta |

### TC-AUTH-003: Login Exitoso
| Campo | Valor |
|-------|-------|
| **ID** | TC-AUTH-003 |
| **Descripción** | Verificar login con credenciales válidas |
| **Precondiciones** | Usuario registrado y activo |
| **Entrada** | Email: user@test.com, Password: correcta |
| **Pasos** | 1. Acceder a /access/<br>2. Introducir credenciales<br>3. Submit |
| **Salida Esperada** | Redirección a dashboard |
| **Prioridad** | Alta |

### TC-AUTH-004: Login con Contraseña Incorrecta
| Campo | Valor |
|-------|-------|
| **ID** | TC-AUTH-004 |
| **Descripción** | Verificar rechazo con contraseña incorrecta |
| **Precondiciones** | Usuario existe |
| **Entrada** | Email válido, Password incorrecta |
| **Pasos** | 1. Acceder a /access/<br>2. Password errónea<br>3. Submit |
| **Salida Esperada** | Error: "Credenciales inválidas" |
| **Prioridad** | Alta |

### TC-AUTH-005: Recuperación de Contraseña
| Campo | Valor |
|-------|-------|
| **ID** | TC-AUTH-005 |
| **Descripción** | Verificar proceso de recuperación de contraseña |
| **Precondiciones** | Usuario con email válido |
| **Entrada** | Email registrado |
| **Pasos** | 1. Click "Olvidé contraseña"<br>2. Introducir email<br>3. Enviar |
| **Salida Esperada** | Email enviado con enlace de recuperación |
| **Prioridad** | Media |

### TC-AUTH-006: Logout de Usuario
| Campo | Valor |
|-------|-------|
| **ID** | TC-AUTH-006 |
| **Descripción** | Verificar cierre de sesión correcto |
| **Precondiciones** | Usuario autenticado |
| **Entrada** | Click en logout |
| **Pasos** | 1. Click en "Cerrar sesión"<br>2. Confirmar |
| **Salida Esperada** | Sesión cerrada, redirección a login |
| **Prioridad** | Alta |

## 2. MÓDULO DE MERCADOS Y BOLSAS

### TC-MER-001: Listado de Mercados
| Campo | Valor |
|-------|-------|
| **ID** | TC-MER-001 |
| **Descripción** | Verificar visualización de mercados disponibles |
| **Precondiciones** | Usuario autenticado |
| **Entrada** | Acceso a /mercados/ |
| **Pasos** | 1. Login<br>2. Navegar a Mercados |
| **Salida Esperada** | Lista de mercados disponibles |
| **Prioridad** | Alta |

### TC-MER-002: Acceso a Bolsa Premium sin Suscripción
| Campo | Valor |
|-------|-------|
| **ID** | TC-MER-002 |
| **Descripción** | Verificar restricción de contenido premium |
| **Precondiciones** | Usuario sin suscripción activa |
| **Entrada** | Click en bolsa premium |
| **Pasos** | 1. Navegar a Bolsas<br>2. Click en bolsa premium |
| **Salida Esperada** | Mensaje: "Requiere suscripción premium" |
| **Prioridad** | Alta |

### TC-MER-003: Filtrado de Bolsas por Mercado
| Campo | Valor |
|-------|-------|
| **ID** | TC-MER-003 |
| **Descripción** | Verificar filtrado de bolsas según mercado |
| **Precondiciones** | Múltiples mercados con bolsas |
| **Entrada** | Selección de mercado específico |
| **Pasos** | 1. Acceder a /bolsas/<br>2. Seleccionar mercado<br>3. Aplicar filtro |
| **Salida Esperada** | Solo bolsas del mercado seleccionado |
| **Prioridad** | Media |

### TC-MER-004: Visualización de Empresas por Bolsa
| Campo | Valor |
|-------|-------|
| **ID** | TC-MER-004 |
| **Descripción** | Verificar listado de empresas de una bolsa |
| **Precondiciones** | Bolsa con empresas asociadas |
| **Entrada** | ID de bolsa válido |
| **Pasos** | 1. Navegar a bolsa específica<br>2. Ver empresas |
| **Salida Esperada** | Lista de empresas de la bolsa |
| **Prioridad** | Alta |

## 3. MÓDULO DE NOTICIAS

### TC-NOT-001: Listado de Noticias Generales
| Campo | Valor |
|-------|-------|
| **ID** | TC-NOT-001 |
| **Descripción** | Verificar visualización de noticias |
| **Precondiciones** | Noticias publicadas en sistema |
| **Entrada** | Acceso a /noticias/ |
| **Pasos** | 1. Login<br>2. Navegar a Noticias |
| **Salida Esperada** | Lista ordenada por fecha (más reciente primero) |
| **Prioridad** | Alta |

### TC-NOT-002: Detalle de Noticia
| Campo | Valor |
|-------|-------|
| **ID** | TC-NOT-002 |
| **Descripción** | Verificar visualización completa de noticia |
| **Precondiciones** | Noticia publicada |
| **Entrada** | ID de noticia válido |
| **Pasos** | 1. Click en noticia<br>2. Ver detalle |
| **Salida Esperada** | Título, descripción, contenido, fecha, autor |
| **Prioridad** | Alta |

### TC-NOT-003: Noticias por Empresa
| Campo | Valor |
|-------|-------|
| **ID** | TC-NOT-003 |
| **Descripción** | Verificar filtrado de noticias por empresa |
| **Precondiciones** | Empresa con noticias asociadas |
| **Entrada** | ID de empresa |
| **Pasos** | 1. Navegar a empresa<br>2. Ver sección noticias |
| **Salida Esperada** | Solo noticias de esa empresa |
| **Prioridad** | Media |

### TC-NOT-004: Búsqueda de Noticias
| Campo | Valor |
|-------|-------|
| **ID** | TC-NOT-004 |
| **Descripción** | Verificar búsqueda por palabras clave |
| **Precondiciones** | Noticias con términos específicos |
| **Entrada** | Término de búsqueda: "dividendo" |
| **Pasos** | 1. Introducir término<br>2. Buscar |
| **Salida Esperada** | Noticias que contienen el término |
| **Prioridad** | Baja |

## 4. MÓDULO DE SUSCRIPCIONES Y PAGOS

### TC-SUB-001: Proceso de Suscripción con Stripe
| Campo | Valor |
|-------|-------|
| **ID** | TC-SUB-001 |
| **Descripción** | Verificar suscripción exitosa vía Stripe |
| **Precondiciones** | Usuario sin suscripción activa |
| **Entrada** | Tarjeta de prueba: 4242 4242 4242 4242 |
| **Pasos** | 1. Seleccionar plan<br>2. Pago con Stripe<br>3. Confirmar |
| **Salida Esperada** | Suscripción activa, acceso a contenido premium |
| **Prioridad** | Alta |

### TC-SUB-002: Pago Rechazado
| Campo | Valor |
|-------|-------|
| **ID** | TC-SUB-002 |
| **Descripción** | Verificar manejo de pago rechazado |
| **Precondiciones** | Usuario sin suscripción |
| **Entrada** | Tarjeta rechazada: 4000 0000 0000 0002 |
| **Pasos** | 1. Intentar pago<br>2. Introducir tarjeta rechazada |
| **Salida Esperada** | Error: "Pago rechazado", sin suscripción |
| **Prioridad** | Alta |

### TC-SUB-003: Cancelación de Suscripción
| Campo | Valor |
|-------|-------|
| **ID** | TC-SUB-003 |
| **Descripción** | Verificar cancelación de suscripción activa |
| **Precondiciones** | Suscripción activa |
| **Entrada** | Click en cancelar suscripción |
| **Pasos** | 1. Ir a /subscription/<br>2. Cancelar<br>3. Confirmar |
| **Salida Esperada** | Suscripción cancelada, acceso hasta fin de período |
| **Prioridad** | Alta |

### TC-SUB-004: Verificación de Estado de Suscripción
| Campo | Valor |
|-------|-------|
| **ID** | TC-SUB-004 |
| **Descripción** | Verificar visualización de estado actual |
| **Precondiciones** | Usuario autenticado |
| **Entrada** | Acceso a página de suscripción |
| **Pasos** | 1. Navegar a /subscription/ |
| **Salida Esperada** | Estado, plan, fecha renovación/expiración |
| **Prioridad** | Media |

## 5. MÓDULO DE PERFIL DE USUARIO

### TC-PRO-001: Actualización de Perfil
| Campo | Valor |
|-------|-------|
| **ID** | TC-PRO-001 |
| **Descripción** | Verificar actualización de datos de perfil |
| **Precondiciones** | Usuario autenticado |
| **Entrada** | Nuevos datos: nombre, apellido |
| **Pasos** | 1. Ir a /profile/<br>2. Editar datos<br>3. Guardar |
| **Salida Esperada** | Datos actualizados correctamente |
| **Prioridad** | Media |

### TC-PRO-002: Cambio de Contraseña
| Campo | Valor |
|-------|-------|
| **ID** | TC-PRO-002 |
| **Descripción** | Verificar cambio de contraseña desde perfil |
| **Precondiciones** | Usuario autenticado |
| **Entrada** | Contraseña actual y nueva |
| **Pasos** | 1. Ir a cambiar contraseña<br>2. Introducir contraseñas<br>3. Confirmar |
| **Salida Esperada** | Contraseña actualizada, requiere nuevo login |
| **Prioridad** | Alta |

### TC-PRO-003: Cambio de Email
| Campo | Valor |
|-------|-------|
| **ID** | TC-PRO-003 |
| **Descripción** | Verificar actualización de email |
| **Precondiciones** | Usuario autenticado |
| **Entrada** | Nuevo email válido |
| **Pasos** | 1. Editar email<br>2. Confirmar con contraseña<br>3. Verificar email |
| **Salida Esperada** | Email actualizado tras verificación |
| **Prioridad** | Media |

## 6. VALIDACIONES DE SEGURIDAD

### TC-SEC-001: Inyección SQL en Login
| Campo | Valor |
|-------|-------|
| **ID** | TC-SEC-001 |
| **Descripción** | Verificar protección contra SQL injection |
| **Precondiciones** | Página de login |
| **Entrada** | Email: ' OR '1'='1' -- |
| **Pasos** | 1. Introducir payload SQL<br>2. Intentar login |
| **Salida Esperada** | Login rechazado, sin exposición de datos |
| **Prioridad** | Crítica |

### TC-SEC-002: XSS en Formularios
| Campo | Valor |
|-------|-------|
| **ID** | TC-SEC-002 |
| **Descripción** | Verificar protección contra XSS |
| **Precondiciones** | Formulario de entrada |
| **Entrada** | `<script>alert('XSS')</script>` |
| **Pasos** | 1. Introducir script en campos<br>2. Enviar |
| **Salida Esperada** | Script sanitizado, no ejecutado |
| **Prioridad** | Crítica |

### TC-SEC-003: Acceso sin Autenticación
| Campo | Valor |
|-------|-------|
| **ID** | TC-SEC-003 |
| **Descripción** | Verificar restricción de acceso a rutas protegidas |
| **Precondiciones** | Usuario no autenticado |
| **Entrada** | URL directa: /dashboard/ |
| **Pasos** | 1. Acceder directamente a URL protegida |
| **Salida Esperada** | Redirección a login |
| **Prioridad** | Crítica |

### TC-SEC-004: Fuerza Bruta en Login
| Campo | Valor |
|-------|-------|
| **ID** | TC-SEC-004 |
| **Descripción** | Verificar protección contra fuerza bruta |
| **Precondiciones** | Página de login |
| **Entrada** | 10 intentos fallidos consecutivos |
| **Pasos** | 1. Intentar login 10 veces con contraseña incorrecta |
| **Salida Esperada** | Bloqueo temporal o captcha requerido |
| **Prioridad** | Alta |

## 7. PRUEBAS DE RENDIMIENTO

### TC-PER-001: Tiempo de Carga Dashboard
| Campo | Valor |
|-------|-------|
| **ID** | TC-PER-001 |
| **Descripción** | Verificar tiempo de carga aceptable |
| **Precondiciones** | Usuario autenticado, conexión estándar |
| **Entrada** | Acceso a dashboard |
| **Pasos** | 1. Login<br>2. Medir tiempo de carga dashboard |
| **Salida Esperada** | Carga completa < 3 segundos |
| **Prioridad** | Media |

### TC-PER-002: Carga de Lista de Noticias
| Campo | Valor |
|-------|-------|
| **ID** | TC-PER-002 |
| **Descripción** | Verificar paginación con muchas noticias |
| **Precondiciones** | 100+ noticias en sistema |
| **Entrada** | Acceso a /noticias/ |
| **Pasos** | 1. Navegar a noticias<br>2. Verificar paginación |
| **Salida Esperada** | Máximo 20 noticias por página, navegación fluida |
| **Prioridad** | Media |

## 8. COMPATIBILIDAD Y RESPONSIVIDAD

### TC-COM-001: Visualización en Móvil
| Campo | Valor |
|-------|-------|
| **ID** | TC-COM-001 |
| **Descripción** | Verificar diseño responsive en móvil |
| **Precondiciones** | Dispositivo móvil o emulador |
| **Entrada** | Resolución 375x667px |
| **Pasos** | 1. Acceder desde móvil<br>2. Navegar por módulos |
| **Salida Esperada** | Interfaz adaptada, menú hamburguesa, scroll correcto |
| **Prioridad** | Alta |

### TC-COM-002: Compatibilidad con Navegadores
| Campo | Valor |
|-------|-------|
| **ID** | TC-COM-002 |
| **Descripción** | Verificar funcionamiento en navegadores principales |
| **Precondiciones** | Chrome, Firefox, Safari, Edge |
| **Entrada** | Acceso desde cada navegador |
| **Pasos** | 1. Probar funcionalidades básicas en cada navegador |
| **Salida Esperada** | Funcionamiento correcto en todos |
| **Prioridad** | Media |

## Resumen de Cobertura

| Módulo | Tests Críticos | Tests Alta | Tests Media | Tests Baja | Total |
|--------|---------------|------------|-------------|------------|-------|
| Autenticación | 0 | 4 | 1 | 1 | 6 |
| Mercados/Bolsas | 0 | 3 | 1 | 0 | 4 |
| Noticias | 0 | 2 | 1 | 1 | 4 |
| Suscripciones | 0 | 3 | 1 | 0 | 4 |
| Perfil | 0 | 1 | 2 | 0 | 3 |
| Seguridad | 3 | 1 | 0 | 0 | 4 |
| Rendimiento | 0 | 0 | 2 | 0 | 2 |
| Compatibilidad | 0 | 1 | 1 | 0 | 2 |
| **TOTAL** | **3** | **15** | **9** | **2** | **29** |

## Matriz de Trazabilidad

| Requisito Funcional | Tests Asociados |
|--------------------|-----------------|
| RF01: Registro de usuarios | TC-AUTH-001, TC-AUTH-002 |
| RF02: Autenticación | TC-AUTH-003, TC-AUTH-004 |
| RF03: Gestión de mercados | TC-MER-001, TC-MER-003 |
| RF04: Gestión de bolsas | TC-MER-002, TC-MER-004 |
| RF05: Sistema de noticias | TC-NOT-001, TC-NOT-002, TC-NOT-003 |
| RF06: Suscripciones premium | TC-SUB-001, TC-SUB-002, TC-SUB-003 |
| RF07: Perfil de usuario | TC-PRO-001, TC-PRO-002 |
| RNF01: Seguridad | TC-SEC-001, TC-SEC-002, TC-SEC-003 |
| RNF02: Rendimiento | TC-PER-001, TC-PER-002 |
| RNF03: Usabilidad | TC-COM-001, TC-COM-002 |