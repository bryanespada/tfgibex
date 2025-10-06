# Implementación del Sistema de Pagos con Stripe

## 1. Introducción

La integración del sistema de pagos con Stripe proporciona una alternativa robusta y moderna para el procesamiento de suscripciones premium. Stripe es conocido por su API elegante, documentación exhaustiva y herramientas de desarrollo superiores. Esta implementación utiliza Stripe Checkout para una experiencia de usuario optimizada y webhooks para garantizar la sincronización automática entre los pagos procesados por Stripe y el estado de las suscripciones en la base de datos local.

## 2. Arquitectura del Sistema

### 2.1 Componentes Principales

El sistema de pagos con Stripe se compone de los siguientes elementos:

- **Frontend**: Botón de Stripe integrado que redirige a Stripe Checkout
- **Stripe Checkout**: Página de pago hosteada y optimizada por Stripe
- **Backend Django**: Gestión de sesiones de checkout y procesamiento de webhooks
- **Stripe API**: Creación de productos, precios y sesiones de checkout
- **Sistema de Webhooks**: Sincronización automática de estados de suscripción

### 2.2 Flujo de Datos

```
Usuario → Botón Stripe → Stripe Checkout → Pago → Webhook → Django → Base de Datos
```

### 2.3 Ventajas de Stripe sobre PayPal

- **Experiencia de Usuario**: Checkout optimizado y responsive
- **Funcionalidades Avanzadas**: Soporte para múltiples métodos de pago
- **Herramientas de Desarrollo**: Dashboard completo y APIs bien documentadas
- **Seguridad**: Cumplimiento PCI DSS nivel 1
- **Flexibilidad**: Personalización avanzada de la experiencia de pago

## 3. Configuración Inicial

### 3.1 Configuración de Stripe Dashboard

Para implementar el sistema de pagos con Stripe:

1. **Crear una cuenta en Stripe Dashboard**
   - Acceder a https://dashboard.stripe.com/
   - Crear una nueva cuenta o usar una existente
   - Activar el modo de prueba (Test mode)

2. **Obtener las claves de API**
   - Acceder a "Developers" → "API keys"
   - Copiar la Publishable key (`pk_test_...`)
   - Copiar la Secret key (`sk_test_...`)

3. **Configurar productos y precios**
   - Crear productos en "Product catalog" → "Products"
   - Definir precios recurrentes para suscripciones

### 3.2 Configuración en Django

Las credenciales de Stripe se almacenan en el modelo `GeneralConfig`:

```python
# appmodels/models.py
class GeneralConfig(models.Model):
    stripe_public_key = models.CharField(max_length=200, blank=False, null=False, default="")
    stripe_secret_key = models.CharField(max_length=200, blank=False, null=False, default="")
```

Las claves se configuran a través del panel de administración de Django y se utilizan en el código para autenticar las requests a la API de Stripe.

## 4. Implementación del Frontend

### 4.1 Integración del Botón de Stripe

El botón de Stripe se implementa como un enlace que redirige a la función de backend encargada de crear la sesión de checkout:

```html
<!-- templates/users/logged/subscription.html -->
{% if product.stripe_subscription_id %}
    <a href="{% url 'stripe_checkout' product_id=product.stripe_subscription_id %}" style="text-decoration: none;">
        <button class="stripe-button-custom">
            Pagar con <i class="fa-brands fa-stripe" style="font-size: 24px; margin-left: 8px;"></i>
        </button>
    </a>
{% endif %}
```

### 4.2 Estilos del Botón

```css
.stripe-button-custom {
    display: flex;
    background: linear-gradient(135deg, #635bff 0%, #4239c8 100%);
    justify-content: center;
    align-items: center;
    color: white;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
    border: none;
    box-shadow: 0 4px 15px rgba(99, 91, 255, 0.3);
}

.stripe-button-custom:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99, 91, 255, 0.4);
    color: white;
}
```

### 4.3 Página de Éxito

Tras completar el pago, Stripe redirige al usuario a la misma página de éxito que PayPal (`/users/successful/`), proporcionando una experiencia consistente:

```html
<!-- templates/paypal/success.html (compartida con Stripe) -->
<div class="count green" style="margin-top: 60px; margin-bottom: 20px;">
    Suscripción exitosa
</div>
<h6>Serás redirigido en unos segundos. Por favor espera...</h6>
```

## 5. Implementación del Backend

### 5.1 Gestión de Sesiones de Checkout

La función `stripe_checkout` crea una sesión de Stripe Checkout y redirige al usuario:

```python
# users/views.py
def stripe_checkout(request, product_id):
    # Check if user already has an active subscription
    if user_is_premium(request.user):
        messages.error(request, "Ya tienes una suscripción activa. No puedes crear otra suscripción.")
        return redirect('user_subscription')

    config = get_object_or_404(GeneralConfig, id=1)

    stripe.api_key = config.stripe_secret_key
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        success_url=f'{config.app_url}users/successful',
        cancel_url=f'{config.app_url}users/cancel',
        line_items=[{"price": product_id, "quantity": 1}],
        mode="subscription",
        allow_promotion_codes=True,
        metadata={
            "user_id": f"{request.user.id}",
            "plan_id": f"{product_id}"
        },
    )

    return redirect(checkout_session.url)
```

#### 5.1.1 Parámetros de la Sesión

- **payment_method_types**: Especifica que solo se aceptan tarjetas
- **success_url/cancel_url**: URLs de redirección después del pago
- **line_items**: Lista de productos a comprar (usando Price ID)
- **mode**: "subscription" para suscripciones recurrentes
- **allow_promotion_codes**: Permite códigos de descuento
- **metadata**: Información adicional para identificar al usuario y producto

### 5.2 Sistema de Webhooks

El sistema de webhooks permite recibir notificaciones en tiempo real sobre eventos de Stripe:

```python
# users/views.py
@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook using adapter pattern
    """
    event_actions = {
        'customer.subscription.updated': stripe_handle_subscription_updated,
        'invoice.paid': stripe_handle_invoice_paid,
        'invoice.finalized': stripe_handle_invoice_paid,
        'checkout.session.completed': stripe_handle_checkout_session_completed,
        'invoice.payment_failed': stripe_handle_payment_failed,
        'payment_intent.payment_failed': stripe_handle_payment_failed,
        'customer.subscription.deleted': stripe_handle_subscription_deleted
    }

    return stripe_handle_event(request, event_actions)
```

### 5.3 Procesadores de Eventos

#### 5.3.1 Creación de Suscripción

```python
# utils/payment_gateway_stripe.py
def stripe_handle_subscription_updated(request, payload):
    subscription_id = payload['data']['object']['id']
    stripe_subscription_id = payload['data']['object']['items']['data'][0]['plan']['id']

    product = Product.objects.get(stripe_subscription_id=stripe_subscription_id)
    plan_id = product.id
    start_date, _ = product.get_period

    try:
        # Verificar si la suscripción ya existe
        subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
        response, details = 500, f"Subscription #{subscription.id} already exists"

    except Subscription.DoesNotExist:
        # Crear nueva suscripción en estado HIDDEN
        subscription = Subscription.objects.create(
            user=None,  # Se asignará en checkout.session.completed
            payment_datetime=timezone.now(),
            payment_method="Stripe",
            payment_product_id=product.id,
            payment_subscription_id=subscription_id,
            start_date=start_date,
            due_date=start_date,
            status='HIDDEN'
        )
        response, details = 200, f"Subscription #{subscription.id} created"

    return response, details
```

#### 5.3.2 Activación de Suscripción

```python
def stripe_handle_checkout_session_completed(request, payload):
    subscription_id = payload['data']['object']['subscription']
    stripe_subscription_id = payload['data']['object']['metadata']['plan_id']
    user_id = int(payload['data']['object']['metadata']['user_id'])

    # Obtener objetos relacionados
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    product = Product.objects.get(stripe_subscription_id=stripe_subscription_id)
    user = CustomUser.objects.get(id=user_id)

    # Calcular fecha de vencimiento
    _, due_date = product.get_period

    # Activar suscripción
    subscription.status = 'ACTIVE'
    subscription.due_date = due_date
    subscription.user = user
    subscription.save()

    # Actualizar estado premium del usuario
    user.is_premium = True
    user.save()

    response, details = 200, f"The subscription #{subscription.id} is been activated"
    return response, details
```

#### 5.3.3 Procesamiento de Pagos

```python
def stripe_handle_invoice_paid(request, payload):
    subscription_id = payload['data']['object']['subscription']
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)

    # Extraer información del pago
    amount_str = payload['data']['object']['lines']['data'][0]['plan']['amount']
    amount = (float(amount_str)) / 100  # Stripe maneja centavos

    # Actualizar monto de la suscripción
    subscription.amount = amount
    subscription.save()

    # Crear registro de pago
    Payment.objects.create(
        user=subscription.user,
        product_id=subscription.payment_product_id,
        amount=amount,
        currency='EUR',
        payment_method='Stripe',
        transaction_id=payload['data']['object']['id'],
        status='completed'
    )

    response, details = 200, f"The payment for subscription #{subscription.id} has been completed"
    return response, details
```

#### 5.3.4 Gestión de Errores de Pago

```python
def stripe_handle_payment_failed(request, payload):
    subscription_id = payload['data']['object']['subscription']
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)

    # Marcar suscripción con error de pago
    subscription.status = 'PAYMENT ERROR'
    subscription.save()

    # Actualizar estado del usuario
    subscription.user.is_premium = False
    subscription.user.save()

    response, details = 200, f"Subscription #{subscription.id} has encountered a payment error"
    return response, details
```

#### 5.3.5 Cancelación de Suscripciones

```python
def stripe_handle_subscription_deleted(request, payload):
    subscription_id = payload['data']['object']['id']
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)

    # Cancelar suscripción
    subscription.status = 'CANCELED'
    subscription.save()

    # Actualizar estado del usuario
    if subscription.user:
        subscription.user.is_premium = False
        subscription.user.save()

    response, details = 200, f"Subscription #{subscription.id} has been canceled"
    return response, details
```

## 6. Configuración de Productos y Precios

### 6.1 Creación en Stripe Dashboard

1. **Navegar a "Product catalog" → "Products"**
2. **Crear nuevo producto**:
   - **Name**: "Suscripción Premium"
   - **Description**: "Acceso premium a todas las funcionalidades"

3. **Configurar precio**:
   - **Pricing model**: "Recurring"
   - **Price**: 9.99 EUR
   - **Billing period**: Monthly
   - **Currency**: EUR

4. **Obtener Price ID**: `price_1SFJudASjloxQU5IqL16TD4Q`

### 6.2 Configuración en Django

```python
# En Django Admin → Products
# Campo: stripe_subscription_id = "price_1SFJudASjloxQU5IqL16TD4Q"
```

Esta configuración vincula el producto Django con el precio específico de Stripe, permitiendo que el sistema identifique qué producto está comprando el usuario.

## 7. Configuración de Webhooks

### 7.1 Configuración en Stripe Dashboard

1. **Navegar a "Developers" → "Webhooks"**
2. **Añadir endpoint**: `https://tu-dominio.com/users/stripe_webhook/`
3. **Seleccionar eventos**:
   - `customer.subscription.updated`
   - `invoice.paid`
   - `invoice.finalized`
   - `checkout.session.completed`
   - `invoice.payment_failed`
   - `payment_intent.payment_failed`
   - `customer.subscription.deleted`

### 7.2 Configuración para Desarrollo

Para desarrollo local con ngrok:

```bash
# URL del webhook
https://nonliable-karyn-nostologic.ngrok-free.dev/users/stripe_webhook/
```

### 7.3 Verificación de Webhooks

Stripe proporciona herramientas para verificar que los webhooks provienen realmente de Stripe:

```python
def verify_stripe_webhook(request):
    """Verify Stripe webhook signature"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = config.stripe_webhook_secret

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return False
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return False

    return True
```

## 8. Modelo de Datos

### 8.1 Estructura de Productos

```python
# appmodels/models.py
class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    paypal_subscription_id = models.CharField(max_length=100, blank=True, null=True)

    def get_period(self):
        """Calculate start and end dates for subscription"""
        start_date = timezone.now().date()
        if self.interval == 'month':
            end_date = start_date + relativedelta(months=1)
        elif self.interval == 'year':
            end_date = start_date + relativedelta(years=1)
        return start_date, end_date
```

### 8.2 Estructura de Suscripciones

```python
class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_datetime = models.DateTimeField()
    payment_method = models.CharField(max_length=50)  # "Stripe", "PayPal"
    payment_product_id = models.IntegerField()
    payment_subscription_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='EUR')
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 8.3 Registros de Pagos

```python
class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    payment_method = models.CharField(max_length=50)  # "Stripe", "PayPal"
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 9. Validaciones y Seguridad

### 9.1 Prevención de Suscripciones Duplicadas

```python
def stripe_checkout(request, product_id):
    # Verificar si el usuario ya tiene una suscripción activa
    if user_is_premium(request.user):
        messages.error(request, "Ya tienes una suscripción activa. No puedes crear otra suscripción.")
        return redirect('user_subscription')

    # Continuar con la creación de la sesión de checkout...
```

### 9.2 Validaciones en Frontend

```html
<!-- templates/users/logged/subscription.html -->
{% if request.user|is_premium %}
    <div class="product-active">
        <i class="fa-solid fa-check-circle"></i> SUSCRIPCIÓN ACTIVA
    </div>
    <div style="text-align: center; margin-top: 15px; padding: 10px; background: #d4edda; border-radius: 8px; color: #155724;">
        <i class="fa-solid fa-info-circle"></i> Ya tienes una suscripción activa
    </div>
{% else %}
    <!-- Mostrar botones de pago -->
{% endif %}
```

### 9.3 Gestión de Errores

El sistema incluye manejo robusto de errores:

```python
def stripe_handle_event(request, event_actions):
    try:
        payload = json.loads(request.body)
        event_type = payload['type']

        if event_type in event_actions:
            response, details = event_actions[event_type](request, payload)
            return JsonResponse({'message': details}, status=response)
        else:
            return JsonResponse({'message': f'Event {event_type} not processed'}, status=200)

    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        return JsonResponse({'message': 'Error processing webhook'}, status=400)
```

## 10. Logging y Monitorización

### 10.1 Logging de Eventos

```python
def log_event_stripe(action, status, request, payload, details, subscription_id, plan_id, invoice_id):
    event_type = payload['type']

    # Obtener información del usuario y suscripción
    user = None
    subscription = None
    product = None

    if subscription_id:
        subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
        if subscription.user:
            user = subscription.user

    if plan_id:
        product = Product.objects.get(id=plan_id)

    # Crear estructura de datos para logging
    payment_gateway_details = {
        "stripe_event_type": event_type,
        "stripe_subscription_id": subscription_id,
        "stripe_invoice_id": invoice_id,
        "stripe_plan_id": plan_id,
    }

    # Registrar evento en el sistema de logs
    log(request, "SubscriptionLog", {
        "action_type": action,
        "status": status,
        "details": details,
        "payment_gateway": "Stripe",
        "product": product,
        "receptor": user,
        "subscription": subscription,
        "payment_gateway_details": json.dumps(payment_gateway_details, indent=4),
        "payload": payload
    })
```

### 10.2 Métricas de Rendimiento

- **Tiempo de respuesta**: Monitorización de la latencia de las APIs
- **Tasa de éxito**: Porcentaje de pagos completados exitosamente
- **Tasa de abandono**: Usuarios que abandonan en Stripe Checkout
- **Errores de webhook**: Seguimiento de webhooks fallidos

## 11. Testing y Validación

### 11.1 Entorno de Pruebas

Stripe Test Mode proporciona:

- **Tarjetas de prueba**: `4242 4242 4242 4242` (Visa), `4000 0566 5566 5556` (Visa Debit)
- **Simulación de errores**: `4000 0000 0000 0002` (tarjeta declinada)
- **Webhooks de prueba**: Envío manual de eventos desde el dashboard
- **Logs detallados**: Seguimiento completo de todas las transacciones

### 11.2 Casos de Prueba

1. **Flujo completo exitoso**:
   - Usuario hace clic en botón Stripe
   - Completa pago en Stripe Checkout
   - Webhook confirma suscripción
   - Usuario obtiene acceso premium

2. **Pago fallido**:
   - Usuario intenta pagar con tarjeta declinada
   - Stripe muestra error apropiado
   - Usuario es redirigido a página de cancelación

3. **Suscripción duplicada**:
   - Usuario premium intenta crear nueva suscripción
   - Sistema muestra mensaje de error
   - No se crea checkout session

### 11.3 Validación de Webhooks

```python
def test_stripe_webhook():
    """Test webhook processing"""
    webhook_payload = {
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'subscription': 'sub_test123',
                'metadata': {
                    'user_id': '1',
                    'plan_id': 'price_test456'
                }
            }
        }
    }

    response = stripe_handle_checkout_session_completed(None, webhook_payload)
    assert response[0] == 200  # Success status
```

## 12. Comparación con PayPal

### 12.1 Ventajas de Stripe

| Aspecto | Stripe | PayPal |
|---------|--------|--------|
| **API Design** | RESTful, consistente | Múltiples APIs, complejo |
| **Documentación** | Excelente, interactiva | Buena, pero fragmentada |
| **Checkout UX** | Optimizado, responsive | Funcional, menos moderno |
| **Herramientas Dev** | Dashboard avanzado | Dashboard básico |
| **Webhooks** | Confiables, bien documentados | Funcionales, menos flexibles |
| **Métodos de Pago** | Amplia gama | Principalmente PayPal/tarjetas |

### 12.2 Casos de Uso Recomendados

- **Stripe**: Ideal para aplicaciones modernas, usuarios técnicos, experiencia premium
- **PayPal**: Mejor para usuarios que prefieren PayPal, mercados internacionales

## 13. Despliegue en Producción

### 13.1 Configuración de Producción

```python
# settings.py (producción)
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_LIVE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
```

### 13.2 Lista de Verificación

- [ ] Cambiar a claves de producción de Stripe
- [ ] Configurar webhook URL de producción
- [ ] Configurar verificación de signatures de webhook
- [ ] Actualizar URLs de success/cancel
- [ ] Configurar monitorización de errores
- [ ] Revisar configuración de productos y precios
- [ ] Probar flujo completo en producción

### 13.3 Consideraciones de Seguridad

- **HTTPS Obligatorio**: Stripe requiere HTTPS para webhooks de producción
- **Verificación de Signatures**: Implementar verificación de webhooks
- **Manejo de Secretos**: Usar variables de entorno para claves sensibles
- **Logging Seguro**: No logear información sensible de tarjetas

## 14. Mantenimiento y Monitorización

### 14.1 Monitorización Continua

- **Stripe Dashboard**: Monitorización en tiempo real de pagos
- **Logs de Aplicación**: Seguimiento de errores y eventos
- **Alertas**: Notificaciones para fallos de webhook o pagos
- **Métricas de Negocio**: Seguimiento de conversiones y churn

### 14.2 Actualizaciones y Mantenimiento

- **Versiones de API**: Stripe mantiene compatibilidad hacia atrás
- **Webhooks**: Verificar nuevos tipos de eventos periódicamente
- **Tarjetas de Prueba**: Actualizar según cambios de Stripe
- **Documentación**: Mantener documentación actualizada con cambios

## 15. Conclusiones

La implementación del sistema de pagos con Stripe proporciona:

### 15.1 Beneficios Técnicos

1. **API Moderna**: Diseño RESTful consistente y predecible
2. **Experiencia de Usuario**: Checkout optimizado y responsive
3. **Herramientas de Desarrollo**: Dashboard avanzado con métricas detalladas
4. **Flexibilidad**: Soporte para múltiples métodos de pago y monedas
5. **Seguridad**: Cumplimiento PCI DSS y cifrado de extremo a extremo

### 15.2 Beneficios de Negocio

1. **Conversión Optimizada**: Checkout diseñado para maximizar conversiones
2. **Gestión Simplificada**: Dashboard intuitivo para gestión de pagos
3. **Escalabilidad**: Soporte para crecimiento del negocio
4. **Análisis Avanzado**: Métricas detalladas de rendimiento
5. **Soporte Global**: Procesamiento en múltiples países y monedas

### 15.3 Integración con PayPal

La implementación dual de Stripe y PayPal proporciona:

- **Flexibilidad de Elección**: Usuarios pueden elegir su método preferido
- **Redundancia**: Backup en caso de problemas con un proveedor
- **Optimización de Conversión**: Diferentes usuarios prefieren diferentes métodos
- **Cobertura Geográfica**: Mejor cobertura global combinada

Esta implementación garantiza una experiencia de pago robusta, segura y optimizada para usuarios, mientras proporciona herramientas de gestión avanzadas para administradores, cumpliendo con los estándares más altos de la industria de pagos digitales.