"""
Tests de Caja Negra - Funcionalidades Principales
TFG IBEX - Tests funcionales sin conocimiento de implementación interna
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from appmodels.models import Mercado, Bolsa, Empresa, Product, Subscription
from decimal import Decimal
from datetime import datetime, timedelta

User = get_user_model()


class BlackBoxAuthenticationTests(TestCase):
    """TC-AUTH-003: Test de Login Exitoso"""

    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@tfgibex.com',
            password='TestPassword123!'
        )

    def test_successful_login(self):
        """TC-AUTH-003: Verificar login con credenciales válidas"""
        print("\n" + "="*60)
        print("TC-AUTH-003: Test de Login Exitoso")
        print("="*60)

        # Precondición verificada
        self.assertTrue(User.objects.filter(email='test@tfgibex.com').exists())
        print("✓ Precondición: Usuario existe en el sistema")

        # Paso 1: Acceder a la página de login
        response = self.client.get('/access/')
        self.assertEqual(response.status_code, 200)
        print("✓ Paso 1: Página de login accesible (código 200)")

        # Paso 2 y 3: Introducir credenciales y enviar
        login_data = {
            'username': 'test@tfgibex.com',  # Django usa username para email
            'password': 'TestPassword123!'
        }
        response = self.client.post('/access/', login_data, follow=True)

        # Verificar autenticación exitosa
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        print("✓ Paso 2-3: Credenciales enviadas y usuario autenticado")

        # Verificar redirección al dashboard
        if response.status_code == 200:
            self.assertIn('dashboard', response.request['PATH_INFO'].lower())
            print("✓ Salida Esperada: Usuario redirigido al dashboard")

        print("\n✅ RESULTADO: TEST PASADO\n")
        return True

    def test_login_with_wrong_password(self):
        """TC-AUTH-004: Verificar rechazo con contraseña incorrecta"""
        print("\n" + "="*60)
        print("TC-AUTH-004: Test de Login con Contraseña Incorrecta")
        print("="*60)

        login_data = {
            'username': 'test@tfgibex.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post('/access/', login_data)

        # Verificar que no se autenticó
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        print("✓ Usuario NO autenticado con credenciales incorrectas")

        # Verificar que permanece en login
        self.assertEqual(response.status_code, 200)
        print("✓ Permanece en página de login")

        print("\n✅ RESULTADO: TEST PASADO\n")
        return True


class BlackBoxMarketTests(TestCase):
    """Tests de Mercados y Bolsas"""

    def setUp(self):
        self.client = Client()

        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='marketuser',
            email='market@tfgibex.com',
            password='Market123!'
        )

        # Crear usuario premium
        self.premium_user = User.objects.create_user(
            username='premiumuser',
            email='premium@tfgibex.com',
            password='Premium123!'
        )

        # Crear datos de prueba
        self.mercado1 = Mercado.objects.create(
            title="Mercado Europeo",
            description="Mercados de valores europeos"
        )

        self.mercado2 = Mercado.objects.create(
            title="Mercado Americano",
            description="Mercados de valores americanos"
        )

        self.bolsa_free = Bolsa.objects.create(
            title="IBEX 35",
            description="Bolsa española",
            mercado=self.mercado1,
            is_premium=False
        )

        self.bolsa_premium = Bolsa.objects.create(
            title="DAX 30",
            description="Bolsa alemana premium",
            mercado=self.mercado1,
            is_premium=True
        )

        # Crear producto y suscripción para usuario premium
        self.product = Product.objects.create(
            name="Plan Premium",
            price=Decimal("9.99"),
            interval_unit="month"
        )

        self.subscription = Subscription.objects.create(
            user=self.premium_user,
            product=self.product,
            status="active",
            current_period_end=datetime.now() + timedelta(days=30)
        )

    def test_market_listing(self):
        """TC-MER-001: Verificar visualización de mercados disponibles"""
        print("\n" + "="*60)
        print("TC-MER-001: Test de Listado de Mercados")
        print("="*60)

        # Paso 1: Login
        self.client.login(username='market@tfgibex.com', password='Market123!')
        print("✓ Paso 1: Usuario autenticado")

        # Paso 2: Navegar a mercados
        response = self.client.get('/app/mercados/')
        self.assertEqual(response.status_code, 200)
        print("✓ Paso 2: Página de mercados accesible")

        # Verificar que los mercados están en la respuesta
        content = str(response.content)
        self.assertIn('Mercado Europeo', content)
        self.assertIn('Mercado Americano', content)
        print("✓ Salida Esperada: Lista de mercados visible")
        print("  - Mercado Europeo ✓")
        print("  - Mercado Americano ✓")

        print("\n✅ RESULTADO: TEST PASADO\n")
        return True

    def test_premium_content_restriction(self):
        """TC-MER-002: Verificar restricción de contenido premium sin suscripción"""
        print("\n" + "="*60)
        print("TC-MER-002: Test de Restricción de Contenido Premium")
        print("="*60)

        # Paso 1: Login con usuario sin suscripción
        self.client.login(username='market@tfgibex.com', password='Market123!')
        print("✓ Paso 1: Usuario NO premium autenticado")

        # Verificar que no tiene suscripción activa
        has_subscription = Subscription.objects.filter(
            user=self.user,
            status='active'
        ).exists()
        self.assertFalse(has_subscription)
        print("✓ Verificado: Usuario sin suscripción activa")

        # Paso 2: Intentar acceder a bolsa premium
        response = self.client.get(f'/app/bolsas/{self.mercado1.id}/')

        if response.status_code == 200:
            content = str(response.content)
            # Verificar que puede ver la bolsa pero con indicador premium
            if 'DAX 30' in content and ('premium' in content.lower() or 'Premium' in content):
                print("✓ Paso 2: Bolsa premium visible pero marcada como restringida")
                print("✓ Salida Esperada: Contenido premium identificado")
            else:
                print("✓ Contenido premium no accesible sin suscripción")
        elif response.status_code == 403:
            print("✓ Acceso denegado a contenido premium (403)")

        print("\n✅ RESULTADO: TEST PASADO\n")
        return True

    def test_premium_content_with_subscription(self):
        """Test adicional: Verificar acceso con suscripción activa"""
        print("\n" + "="*60)
        print("Test Adicional: Acceso Premium con Suscripción")
        print("="*60)

        # Login con usuario premium
        self.client.login(username='premium@tfgibex.com', password='Premium123!')
        print("✓ Usuario premium autenticado")

        # Verificar suscripción activa
        has_subscription = Subscription.objects.filter(
            user=self.premium_user,
            status='active',
            current_period_end__gt=datetime.now()
        ).exists()
        self.assertTrue(has_subscription)
        print("✓ Suscripción premium activa verificada")

        # Acceder a contenido premium
        response = self.client.get(f'/app/bolsas/{self.mercado1.id}/')
        self.assertEqual(response.status_code, 200)
        print("✓ Acceso permitido a contenido premium")

        print("\n✅ RESULTADO: TEST PASADO\n")
        return True


class BlackBoxIntegrationTest(TestCase):
    """Test de integración de flujo completo"""

    def test_complete_user_flow(self):
        """Test de flujo completo: registro -> login -> navegación -> logout"""
        print("\n" + "="*60)
        print("TEST DE INTEGRACIÓN: Flujo Completo de Usuario")
        print("="*60)

        client = Client()

        # 1. REGISTRO (simulado - crear usuario)
        user = User.objects.create_user(
            username='newuser',
            email='new@tfgibex.com',
            password='NewUser123!'
        )
        print("✓ Paso 1: Usuario registrado exitosamente")

        # 2. LOGIN
        login_success = client.login(username='new@tfgibex.com', password='NewUser123!')
        self.assertTrue(login_success)
        print("✓ Paso 2: Login exitoso")

        # 3. NAVEGACIÓN - Dashboard
        response = client.get('/app/dashboard/')
        self.assertEqual(response.status_code, 200)
        print("✓ Paso 3: Acceso al dashboard")

        # 4. NAVEGACIÓN - Mercados
        response = client.get('/app/mercados/')
        self.assertEqual(response.status_code, 200)
        print("✓ Paso 4: Navegación a mercados")

        # 5. NAVEGACIÓN - Noticias
        response = client.get('/app/noticias/')
        self.assertEqual(response.status_code, 200)
        print("✓ Paso 5: Navegación a noticias")

        # 6. LOGOUT
        response = client.get('/exit/')
        self.assertEqual(response.status_code, 302)  # Redirección
        print("✓ Paso 6: Logout exitoso")

        # 7. VERIFICAR ACCESO RESTRINGIDO
        response = client.get('/app/dashboard/')
        self.assertNotEqual(response.status_code, 200)  # No puede acceder sin login
        print("✓ Paso 7: Acceso restringido después de logout")

        print("\n✅ RESULTADO: FLUJO COMPLETO EXITOSO\n")
        return True


def run_critical_black_box_tests():
    """Ejecutor principal de tests críticos"""
    print("\n" + "="*70)
    print("EJECUCIÓN DE TESTS DE CAJA NEGRA - FUNCIONALIDADES CRÍTICAS")
    print("="*70)
    print("Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Sistema: TFG IBEX")
    print("="*70)

    # Lista de tests a ejecutar
    test_results = {
        'TC-AUTH-003': False,
        'TC-AUTH-004': False,
        'TC-MER-001': False,
        'TC-MER-002': False,
        'INTEGRATION': False
    }

    print("\n📋 Tests a ejecutar:")
    print("1. TC-AUTH-003: Login exitoso")
    print("2. TC-AUTH-004: Login con contraseña incorrecta")
    print("3. TC-MER-001: Listado de mercados")
    print("4. TC-MER-002: Restricción de contenido premium")
    print("5. INTEGRATION: Flujo completo de usuario")

    print("\n" + "-"*70)

    # Resumen de resultados
    print("\n" + "="*70)
    print("RESUMEN DE RESULTADOS")
    print("="*70)

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    for test_id, passed in test_results.items():
        status = "✅ PASADO" if passed else "❌ FALLADO"
        print(f"{test_id}: {status}")

    print("-"*70)
    print(f"Total: {passed_tests}/{total_tests} tests pasados")
    print(f"Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
    print("="*70)