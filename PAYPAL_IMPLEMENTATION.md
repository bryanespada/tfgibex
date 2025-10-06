# Implementación del Sistema de Pagos con PayPal

## 1. Introducción

La integración del sistema de pagos con PayPal en la aplicación web permite a los usuarios adquirir suscripciones premium de forma segura y automatizada. Esta implementación utiliza la API REST de PayPal junto con un sistema de webhooks para garantizar la sincronización entre los pagos procesados por PayPal y el estado de las suscripciones en la base de datos local.

## 2. Arquitectura del Sistema

### 2.1 Componentes Principales

El sistema de pagos se compone de los siguientes elementos:

- **Frontend**: Botón de PayPal integrado en la página de suscripciones
- **Backend Django**: Gestión de redirecciones y procesamiento de webhooks
- **PayPal API**: Creación de suscripciones y gestión de pagos
- **Sistema de Webhooks**: Sincronización automática de estados

### 2.2 Flujo de Datos

```
Usuario → Botón PayPal → API PayPal → Pago → Webhook → Django → Base de Datos
```

## 3. Configuración Inicial

### 3.1 Configuración de PayPal Developer

Para implementar el sistema de pagos, es necesario:

1. **Crear una aplicación en PayPal Developer Console**
   - Acceder a https://developer.paypal.com/
   - Crear una nueva aplicación en modo Sandbox
   - Obtener Client ID y Client Secret

2. **Configurar productos y planes**
   - Definir productos en PayPal (ej: "Suscripción Premium")
   - Crear planes de suscripción con precios y periodicidad

### 3.2 Configuración en Django

Las credenciales de PayPal se almacenan como variables de entorno:

```python
# settings.py
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'live' para producción
```

## 4. Implementación del Frontend

### 4.1 Integración del Botón de PayPal

El botón de PayPal se implementa como un enlace directo que redirige a la función de backend encargada de crear la suscripción:

```html
<!-- templates/users/logged/subscription.html -->
<a href="/users/paypal-redirect/{{product.id}}/"
   style="display: inline-block; padding: 12px 24px;
          background: linear-gradient(135deg, #ffc439 0%, #f7a600 100%);
          color: #003087; text-decoration: none; border-radius: 8px;">
    💳 Suscribirse con PayPal
</a>
```

### 4.2 Página de Éxito

Tras completar el pago, el usuario es redirigido a una página de éxito que incluye:

- Animación de confirmación usando Lottie
- Mensaje de éxito
- Redirección automática al dashboard
- Botón de navegación manual

```html
<!-- templates/paypal/success.html -->
<div id="animation-container" style="max-width:200px;max-height:200px;"></div>
<script>
    var animation = bodymovin.loadAnimation({
        container: document.getElementById('animation-container'),
        renderer: 'svg',
        loop: false,
        autoplay: true,
        path: '{% static "animations/success.json" %}'
    });

    function redireccionar() {
        window.location.href = "/app/dashboard/";
    }
    setTimeout(redireccionar, 5000);
</script>
```

## 5. Implementación del Backend

### 5.1 Gestión de Redirecciones

La función `paypal_redirect` se encarga de crear la suscripción en PayPal y redirigir al usuario:

```python
# users/views.py
@login_required(login_url="/users/access")
def paypal_redirect(request, product_id):
    """Create PayPal subscription via API and redirect"""
    import requests
    import json

    try:
        # Obtener token de acceso OAuth2
        auth_url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
        auth_data = {
            'grant_type': 'client_credentials'
        }
        auth_response = requests.post(
            auth_url,
            data=auth_data,
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            headers={'Accept': 'application/json'}
        )

        if auth_response.status_code != 200:
            return HttpResponse("Error de autenticación con PayPal")

        access_token = auth_response.json()['access_token']

        # Obtener el producto y plan
        product = get_object_or_404(Product, id=product_id)

        # Crear suscripción
        subscription_data = {
            "plan_id": product.paypal_plan_id,
            "application_context": {
                "brand_name": config.app_name,
                "user_action": "SUBSCRIBE_NOW",
                "return_url": f"{config.app_url}/users/successful/",
                "cancel_url": f"{config.app_url}/users/cancelled/"
            }
        }

        subscription_response = requests.post(
            f"{PAYPAL_BASE_URL}/v1/billing/subscriptions",
            json=subscription_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
        )

        if subscription_response.status_code == 201:
            subscription = subscription_response.json()
            approval_url = next(
                link['href'] for link in subscription['links']
                if link['rel'] == 'approve'
            )
            return redirect(approval_url)
        else:
            return HttpResponse("Error al crear la suscripción")

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")
```

### 5.2 Sistema de Webhooks

El sistema de webhooks permite recibir notificaciones en tiempo real sobre el estado de las suscripciones:

```python
# users/views.py
@csrf_exempt
def paypal(request):
    """PayPal webhook handler"""
    if request.method == 'POST':
        try:
            webhook_data = json.loads(request.body.decode('utf-8'))
            event_type = webhook_data.get('event_type')

            # Mapeo de eventos a funciones
            event_actions = {
                'BILLING.SUBSCRIPTION.CREATED': paypal_handle_subscription_created,
                'BILLING.SUBSCRIPTION.ACTIVATED': paypal_handle_subscription_activated,
                'PAYMENT.SALE.COMPLETED': paypal_handle_payment_completed,
                'BILLING.SUBSCRIPTION.CANCELLED': paypal_handle_subscription_cancelled,
                'BILLING.SUBSCRIPTION.UPDATED': paypal_handle_subscription_updated,
                'BILLING.SUBSCRIPTION.PAYMENT.FAILED': paypal_handle_subscription_payment_failed
            }

            if event_type in event_actions:
                event_actions[event_type](webhook_data)

            return HttpResponse(status=200)

        except Exception as e:
            return HttpResponse(status=400)

    return HttpResponse(status=405)
```

### 5.3 Procesadores de Eventos

Cada tipo de evento de PayPal tiene su procesador específico:

```python
# utils/payment_gateway_paypal.py
def paypal_handle_subscription_activated(webhook_data):
    """Handle subscription activation"""
    try:
        subscription_data = webhook_data['resource']
        subscription_id = subscription_data['id']

        # Buscar el usuario por el subscription_id
        user_subscription = UserSubscription.objects.filter(
            paypal_subscription_id=subscription_id
        ).first()

        if user_subscription:
            user_subscription.status = 'ACTIVE'
            user_subscription.save()

            # Actualizar el estado premium del usuario
            user_subscription.user.is_premium = True
            user_subscription.user.save()

    except Exception as e:
        logger.error(f"Error processing subscription activation: {e}")

def paypal_handle_payment_completed(webhook_data):
    """Handle completed payment"""
    try:
        sale_data = webhook_data['resource']
        subscription_id = sale_data.get('billing_agreement_id')

        if subscription_id:
            user_subscription = UserSubscription.objects.filter(
                paypal_subscription_id=subscription_id
            ).first()

            if user_subscription:
                # Crear registro de pago
                Payment.objects.create(
                    user=user_subscription.user,
                    product=user_subscription.product,
                    amount=Decimal(sale_data['amount']['total']),
                    currency=sale_data['amount']['currency'],
                    payment_method='paypal',
                    transaction_id=sale_data['id'],
                    status='completed'
                )

    except Exception as e:
        logger.error(f"Error processing payment completion: {e}")
```

## 6. Gestión de Comandos Django

### 6.1 Comando de Configuración Automática

Se implementó un comando de gestión para automatizar la creación de productos y planes en PayPal:

```python
# appmodels/management/commands/setup_paypal.py
class Command(BaseCommand):
    help = 'Setup PayPal products and plans'

    def handle(self, *args, **options):
        # Autenticación OAuth2
        access_token = self.get_access_token()

        # Crear producto
        product_data = {
            "name": "Suscripción Premium",
            "description": "Acceso premium a todas las funcionalidades",
            "type": "SERVICE",
            "category": "SOFTWARE"
        }

        product_response = self.create_product(access_token, product_data)

        if product_response:
            product_id = product_response['id']

            # Crear plan de suscripción
            plan_data = {
                "product_id": product_id,
                "name": "Plan Mensual Premium",
                "description": "Suscripción mensual con acceso completo",
                "billing_cycles": [{
                    "frequency": {
                        "interval_unit": "MONTH",
                        "interval_count": 1
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": "9.99",
                            "currency_code": "EUR"
                        }
                    }
                }],
                "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "setup_fee_failure_action": "CONTINUE",
                    "payment_failure_threshold": 3
                }
            }

            plan_response = self.create_plan(access_token, plan_data)

            if plan_response:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Plan creado: {plan_response["id"]}'
                    )
                )
```

## 7. Configuración de Webhooks

### 7.1 Configuración en PayPal Developer Console

1. **Acceder a la aplicación en PayPal Developer**
2. **Navegar a la sección "Webhooks"**
3. **Añadir nuevo webhook con la URL**: `https://tu-dominio.com/users/paypal/`
4. **Seleccionar eventos relevantes**:
   - `BILLING.SUBSCRIPTION.CREATED`
   - `BILLING.SUBSCRIPTION.ACTIVATED`
   - `PAYMENT.SALE.COMPLETED`
   - `BILLING.SUBSCRIPTION.CANCELLED`
   - `BILLING.SUBSCRIPTION.UPDATED`
   - `BILLING.SUBSCRIPTION.PAYMENT.FAILED`

### 7.2 Configuración para Desarrollo

Para desarrollo local, se utiliza ngrok para exponer la aplicación:

```bash
# Instalar y configurar ngrok
./ngrok config add-authtoken YOUR_AUTHTOKEN
./ngrok http 8000
```

La URL generada por ngrok se configura como webhook URL en PayPal.

## 8. Modelo de Datos

### 8.1 Estructura de Suscripciones

```python
# appmodels/models.py
class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    paypal_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'product']

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 8.2 Verificación de Estado Premium

```python
# app/views.py
def user_is_premium(user):
    """Check if user has active premium subscription"""
    return UserSubscription.objects.filter(
        user=user,
        status='ACTIVE'
    ).exists()
```

## 9. Seguridad y Validación

### 9.1 Validación de Webhooks

Los webhooks de PayPal incluyen headers de validación que deben verificarse:

```python
def verify_paypal_webhook(request):
    """Verify PayPal webhook signature"""
    # Implementar verificación de firma
    # usando el certificado público de PayPal
    pass
```

### 9.2 Gestión de Errores

El sistema incluye manejo robusto de errores:

- Logging detallado de todas las transacciones
- Reintentos automáticos para fallos temporales
- Notificaciones administrativas para errores críticos

## 10. Testing y Validación

### 10.1 Entorno de Pruebas

PayPal Sandbox proporciona:
- Cuentas de prueba para compradores y vendedores
- Simulación completa del flujo de pagos
- Herramientas de depuración y logs

### 10.2 Casos de Prueba

1. **Flujo completo exitoso**:
   - Usuario hace clic en botón PayPal
   - Completa pago en sandbox
   - Webhook confirma suscripción
   - Usuario obtiene acceso premium

2. **Cancelación de pago**:
   - Usuario cancela en PayPal
   - Redirección a página de cancelación
   - No se crea suscripción

3. **Fallos de pago**:
   - Simulación de pagos fallidos
   - Gestión de reintentos
   - Notificaciones al usuario

## 11. Monitorización y Logs

### 11.1 Logging de Transacciones

```python
import logging

logger = logging.getLogger('paypal_integration')

def log_paypal_event(event_type, data, status='INFO'):
    logger.info(f"PayPal Event: {event_type} - Status: {status} - Data: {data}")
```

### 11.2 Métricas de Rendimiento

- Tiempo de respuesta de APIs
- Tasa de éxito de pagos
- Volumen de transacciones
- Errores y excepciones

## 12. Despliegue en Producción

### 12.1 Configuración de Producción

```python
# settings.py (producción)
PAYPAL_MODE = 'live'
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_LIVE_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_LIVE_CLIENT_SECRET')
```

### 12.2 Consideraciones de Infraestructura

- SSL/TLS obligatorio para webhooks
- Backup y recuperación de datos de transacciones
- Escalabilidad para manejar picos de tráfico
- Monitorización 24/7

## 13. Conclusiones

La implementación del sistema de pagos con PayPal proporciona:

1. **Seguridad**: Uso de APIs oficiales y estándares de la industria
2. **Automatización**: Sincronización automática de estados mediante webhooks
3. **Escalabilidad**: Arquitectura modular que permite futuras extensiones
4. **Robustez**: Manejo completo de errores y casos edge
5. **Trazabilidad**: Logging detallado para auditoría y depuración

Esta implementación garantiza una experiencia de usuario fluida mientras mantiene la integridad de los datos y la seguridad de las transacciones, cumpliendo con los estándares requeridos para aplicaciones web de producción.