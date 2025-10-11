# Sesiones de Testing Exploratorio - TFG IBEX

## Metodología: Session-Based Test Management (SBTM)

### Duración por sesión: 45 minutos
### Técnica principal: Freestyle exploration con heurísticas

---

## SESIÓN 1: Exploración de Límites y Casos Extremos
**Charter**: Explorar el comportamiento del sistema con entradas en los límites y casos no convencionales

### Áreas de Enfoque:
1. **Campos de texto**
   - [ ] Campos vacíos donde se requiere información
   - [ ] Textos extremadamente largos (>1000 caracteres)
   - [ ] Solo espacios en blanco
   - [ ] Caracteres especiales: `<>{}[]|\/~!@#$%^&*()`
   - [ ] Emojis: 😀🚀💰📈
   - [ ] Scripts: `<script>alert('test')</script>`
   - [ ] SQL: `'; DROP TABLE users; --`

2. **Campos numéricos**
   - [ ] Números negativos en precios
   - [ ] Cero en cantidades
   - [ ] Números muy grandes (999999999)
   - [ ] Decimales con muchos dígitos (9.999999999)
   - [ ] Notación científica (1e10)
   - [ ] Texto en campos numéricos

3. **Fechas**
   - [ ] Fechas futuras (año 2099)
   - [ ] Fechas pasadas (año 1900)
   - [ ] 29 de febrero en año no bisiesto
   - [ ] Formatos incorrectos (31/13/2024)

### Heurísticas a aplicar:
- **CRUD**: Create, Read, Update, Delete en límites
- **Zero, One, Many**: Probar con 0, 1 y muchos elementos
- **Some, None, All**: Seleccionar algunos, ninguno, todos

---

## SESIÓN 2: Exploración de Estados y Transiciones
**Charter**: Descubrir problemas relacionados con cambios de estado y concurrencia

### Escenarios:
1. **Multi-sesión**
   - [ ] Login en múltiples pestañas/navegadores
   - [ ] Logout en una pestaña mientras otras están activas
   - [ ] Cambiar contraseña con sesiones activas

2. **Interrupciones**
   - [ ] Cerrar navegador durante pago
   - [ ] Timeout durante edición de perfil
   - [ ] Pérdida de conexión durante suscripción
   - [ ] Botón atrás durante procesos de múltiples pasos

3. **Condiciones de carrera**
   - [ ] Doble click en "Suscribirse"
   - [ ] Múltiples envíos del mismo formulario
   - [ ] Editar mismo registro desde dos sesiones

### Técnica: State Transition Testing
- Mapear estados posibles
- Probar transiciones válidas e inválidas
- Verificar persistencia de estado

---

## SESIÓN 3: Exploración de Datos Inusuales
**Charter**: Probar el sistema con configuraciones de datos atípicas pero válidas

### Configuraciones a probar:
1. **Estructuras vacías**
   - [ ] Mercado sin bolsas
   - [ ] Bolsa sin empresas
   - [ ] Empresa sin noticias
   - [ ] Usuario sin suscripciones

2. **Estructuras sobrecargadas**
   - [ ] Mercado con 100+ bolsas
   - [ ] Empresa con 1000+ noticias
   - [ ] Usuario con múltiples suscripciones activas

3. **Datos edge case**
   - [ ] Nombres con tildes y ñ: "Ibáñez"
   - [ ] Empresas con nombres similares
   - [ ] Precios con céntimos: €9.99
   - [ ] Descripciones en múltiples idiomas

### Heurística: VADER
- **V**ariables: Identificar todas las variables
- **A**ctions: Acciones posibles sobre datos
- **D**ata: Tipos de datos a probar
- **E**nvironment: Condiciones del entorno
- **R**elationships: Relaciones entre datos

---

## SESIÓN 4: Exploración de Interacciones No Previstas
**Charter**: Descubrir problemas usando el sistema de formas no convencionales

### Patrones de interacción:
1. **Navegación alternativa**
   - [ ] Solo teclado (Tab, Enter, Esc)
   - [ ] Solo teclas de acceso rápido
   - [ ] Navegación por URL directa
   - [ ] Bookmarks a páginas internas

2. **Manipulación del cliente**
   - [ ] Desactivar JavaScript
   - [ ] Desactivar cookies
   - [ ] Modificar HTML con DevTools
   - [ ] Cambiar user-agent

3. **Operaciones no estándar**
   - [ ] Copiar/pegar desde Word con formato
   - [ ] Drag & drop donde no se espera
   - [ ] Zoom extremo (50% - 200%)
   - [ ] Imprimir páginas dinámicas

### Tour: Antisocial Tour
- Hacer todo lo que un usuario "no debería" hacer
- Buscar formas creativas de romper el flujo esperado

---

## SESIÓN 5: Exploración de Condiciones de Error
**Charter**: Provocar y analizar el manejo de errores del sistema

### Escenarios de error:
1. **Errores de red**
   - [ ] Conexión lenta (throttling)
   - [ ] Pérdida intermitente de conexión
   - [ ] Timeout en respuestas
   - [ ] Proxy con restricciones

2. **Errores de datos**
   - [ ] IDs inexistentes en URL: `/empresa/99999`
   - [ ] Parámetros faltantes en requests
   - [ ] Tokens expirados
   - [ ] Datos corruptos en formularios

3. **Errores de negocio**
   - [ ] Suscribirse sin método de pago
   - [ ] Acceder a contenido premium expirado
   - [ ] Operaciones sin permisos suficientes

### Heurística: Error Handling
- ¿El error es claro y útil?
- ¿Se puede recuperar del error?
- ¿Se registra el error para debugging?
- ¿Expone información sensible?

---

## Técnicas Generales de Exploración

### FEW HICCUPPS (Heurística de James Bach)
- **F**requent: Lo que se usa frecuentemente
- **E**rror: Manejo de errores
- **W**eird: Comportamientos extraños

- **H**igh: Valores altos
- **I**ntended: Uso previsto
- **C**omplex: Escenarios complejos
- **C**laimed: Lo que dice hacer
- **U**ser: Diferentes tipos de usuario
- **P**latform: Diferentes plataformas
- **P**opular: Características populares
- **S**tructure: Estructura del sistema

### SFDIPOT (Heurística de James Bach)
- **S**tructure: ¿Qué es?
- **F**unction: ¿Qué hace?
- **D**ata: ¿Qué procesa?
- **I**nterface: ¿Cómo se usa?
- **P**latform: ¿Dónde corre?
- **O**perations: ¿Cómo se opera?
- **T**ime: ¿Cuándo ocurre?

---

## Registro de Defectos

### Plantilla de reporte:
```
ID: ET-XXX
Sesión: [1-5]
Severidad: [Crítica|Alta|Media|Baja]
Timestamp: YYYY-MM-DD HH:MM
Descripción: [Qué sucedió]
Pasos: [Cómo reproducirlo]
Esperado: [Qué debería pasar]
Actual: [Qué pasó realmente]
Entorno: [Navegador, OS, etc.]
Evidence: [Screenshot/Video si aplica]
```

---

## Métricas a Capturar

1. **Cobertura**: Áreas exploradas vs. no exploradas
2. **Velocidad de descubrimiento**: Defectos/hora
3. **Severidad**: Distribución de severidad de defectos
4. **Áreas problemáticas**: Módulos con más defectos
5. **Tipos de defectos**: Categorización (UI, Lógica, Seguridad, etc.)