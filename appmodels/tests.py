from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import (
    GeneralConfig, Mercado, Bolsa, Empresa,
    Product, Noticia, Subscription
)
from decimal import Decimal
from datetime import datetime, timedelta


User = get_user_model()


class GeneralConfigTestCase(TestCase):
    """Tests para el modelo GeneralConfig"""

    def test_single_instance_only(self):
        """Verificar que solo puede existir una instancia de GeneralConfig"""
        GeneralConfig.objects.create(app_name="Test App")

        config2 = GeneralConfig(app_name="Another App")
        with self.assertRaises(ValidationError):
            config2.clean()

    def test_default_values(self):
        """Verificar valores por defecto de GeneralConfig"""
        config = GeneralConfig.objects.create()
        self.assertEqual(config.app_name, "Easy Regional Block")
        self.assertEqual(config.app_syncopation, "ERB")
        self.assertEqual(config.currency, "USD")
        self.assertEqual(config.smtp_port, 587)


class MercadoTestCase(TestCase):
    """Tests para el modelo Mercado"""

    def setUp(self):
        self.mercado = Mercado.objects.create(
            title="Mercado Europeo",
            description="Mercado de valores europeo"
        )

    def test_mercado_creation(self):
        """Verificar creación correcta de Mercado"""
        self.assertTrue(isinstance(self.mercado, Mercado))
        self.assertEqual(self.mercado.title, "Mercado Europeo")
        self.assertEqual(str(self.mercado), "Mercado Europeo")

    def test_mercado_fields(self):
        """Verificar campos de Mercado"""
        self.assertEqual(self.mercado.description, "Mercado de valores europeo")


class BolsaTestCase(TestCase):
    """Tests para el modelo Bolsa"""

    def setUp(self):
        self.mercado = Mercado.objects.create(title="Mercado Test")
        self.bolsa = Bolsa.objects.create(
            title="IBEX 35",
            description="Bolsa española",
            mercado=self.mercado,
            is_premium=False
        )

    def test_bolsa_creation(self):
        """Verificar creación correcta de Bolsa"""
        self.assertTrue(isinstance(self.bolsa, Bolsa))
        self.assertEqual(self.bolsa.title, "IBEX 35")
        self.assertEqual(str(self.bolsa), "IBEX 35")

    def test_bolsa_mercado_relationship(self):
        """Verificar relación Bolsa-Mercado"""
        self.assertEqual(self.bolsa.mercado, self.mercado)

    def test_is_premium_default(self):
        """Verificar valor por defecto de is_premium"""
        bolsa_default = Bolsa.objects.create(
            title="Test Bolsa",
            mercado=self.mercado
        )
        self.assertFalse(bolsa_default.is_premium)

    def test_total_noticias_property(self):
        """Verificar propiedad total_noticias"""
        self.assertEqual(self.bolsa.total_noticias, 0)


class EmpresaTestCase(TestCase):
    """Tests para el modelo Empresa"""

    def setUp(self):
        self.mercado = Mercado.objects.create(title="Mercado Test")
        self.bolsa = Bolsa.objects.create(
            title="Bolsa Test",
            mercado=self.mercado
        )
        self.empresa = Empresa.objects.create(
            title="Telefónica",
            description="Empresa de telecomunicaciones",
            public=True,
            mercado=self.mercado,
            bolsa=self.bolsa
        )

    def test_empresa_creation(self):
        """Verificar creación correcta de Empresa"""
        self.assertTrue(isinstance(self.empresa, Empresa))
        self.assertEqual(self.empresa.title, "Telefónica")
        self.assertEqual(str(self.empresa), "Telefónica")

    def test_empresa_relationships(self):
        """Verificar relaciones de Empresa"""
        self.assertEqual(self.empresa.mercado, self.mercado)
        self.assertEqual(self.empresa.bolsa, self.bolsa)

    def test_public_default(self):
        """Verificar valor por defecto de public"""
        empresa_default = Empresa.objects.create(
            title="Test Empresa",
            mercado=self.mercado,
            bolsa=self.bolsa
        )
        self.assertFalse(empresa_default.public)


class ProductTestCase(TestCase):
    """Tests para el modelo Product"""

    def test_product_creation(self):
        """Verificar creación de Product"""
        product = Product.objects.create(
            name="Plan Premium",
            description="Acceso completo",
            price=Decimal("9.99"),
            interval_unit="month",
            interval_count=1
        )
        self.assertEqual(product.name, "Plan Premium")
        self.assertEqual(product.price, Decimal("9.99"))
        self.assertEqual(str(product), "Plan Premium")

    def test_product_default_values(self):
        """Verificar valores por defecto de Product"""
        product = Product.objects.create(
            name="Test Product",
            price=Decimal("5.00")
        )
        self.assertEqual(product.interval_unit, "month")
        self.assertEqual(product.interval_count, 1)
        self.assertTrue(product.active)


class NoticiaTestCase(TestCase):
    """Tests para el modelo Noticia"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.mercado = Mercado.objects.create(title="Mercado Test")
        self.bolsa = Bolsa.objects.create(
            title="Bolsa Test",
            mercado=self.mercado
        )
        self.empresa = Empresa.objects.create(
            title="Empresa Test",
            mercado=self.mercado,
            bolsa=self.bolsa
        )

    def test_noticia_creation(self):
        """Verificar creación de Noticia"""
        noticia = Noticia.objects.create(
            title="Noticia Test",
            description="Descripción de la noticia",
            text="Contenido completo de la noticia",
            author=self.user,
            empresa=self.empresa
        )
        self.assertEqual(noticia.title, "Noticia Test")
        self.assertEqual(noticia.author, self.user)
        self.assertEqual(noticia.empresa, self.empresa)
        self.assertIsNotNone(noticia.publication_date)


class SubscriptionTestCase(TestCase):
    """Tests para el modelo Subscription"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.product = Product.objects.create(
            name="Plan Test",
            price=Decimal("10.00"),
            interval_unit="month",
            interval_count=1
        )

    def test_subscription_creation(self):
        """Verificar creación de Subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            product=self.product,
            status="active"
        )
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.product, self.product)
        self.assertEqual(subscription.status, "active")

    def test_subscription_dates(self):
        """Verificar fechas de Subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            product=self.product,
            status="active"
        )
        self.assertIsNotNone(subscription.created_at)
        self.assertIsNotNone(subscription.current_period_start)
        self.assertIsNotNone(subscription.current_period_end)

        # Verificar que el periodo es de un mes
        expected_end = subscription.current_period_start + timedelta(days=30)
        self.assertAlmostEqual(
            subscription.current_period_end.timestamp(),
            expected_end.timestamp(),
            delta=86400  # 1 día de diferencia aceptable
        )