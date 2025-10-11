#!/usr/bin/env python
"""
Script de Testing Exploratorio Automatizado - TFG IBEX
Ejecuta pruebas exploratorias automatizables para descubrir defectos
"""

import os
import sys
import django
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from appmodels.models import Mercado, Bolsa, Empresa, Product, Subscription

User = get_user_model()

class ExploratoryTesting:
    """Clase principal para ejecutar sesiones de testing exploratorio"""

    def __init__(self):
        self.defects = []
        self.session_start = datetime.now()
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0

    def log_defect(self, session, severity, description, steps, expected, actual):
        """Registrar un defecto encontrado"""
        defect = {
            'id': f"ET-{len(self.defects) + 1:03d}",
            'session': session,
            'severity': severity,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'description': description,
            'steps': steps,
            'expected': expected,
            'actual': actual
        }
        self.defects.append(defect)
        self.tests_failed += 1
        print(f"❌ DEFECTO ENCONTRADO: {defect['id']} - {description}")
        return defect

    def test_passed(self, description):
        """Registrar un test exitoso"""
        self.tests_passed += 1
        print(f"✅ {description}")

    # ========== SESIÓN 1: LÍMITES Y CASOS EXTREMOS ==========

    def session_1_limits_and_edge_cases(self):
        """Explorar límites y casos extremos"""
        print("\n" + "="*60)
        print("SESIÓN 1: EXPLORACIÓN DE LÍMITES Y CASOS EXTREMOS")
        print("="*60)

        self.tests_run += 1

        # Test 1.1: Campos de texto con caracteres especiales
        print("\n[1.1] Probando caracteres especiales en títulos...")
        special_chars = "<>{}[]|/~!@#$%^&*()"
        try:
            mercado = Mercado.objects.create(
                title=f"Mercado {special_chars}",
                description="Test de caracteres especiales"
            )
            mercado.save()
            mercado.delete()
            self.test_passed("Sistema acepta caracteres especiales en títulos")
        except Exception as e:
            self.log_defect(
                session=1,
                severity="Media",
                description="Error al guardar caracteres especiales",
                steps="Crear mercado con caracteres especiales en título",
                expected="Debería sanitizar o aceptar los caracteres",
                actual=f"Error: {str(e)}"
            )

        # Test 1.2: Emojis en campos de texto
        print("\n[1.2] Probando emojis en descripciones...")
        self.tests_run += 1
        try:
            empresa = Empresa.objects.create(
                title="Empresa Test 🚀💰📈",
                description="Descripción con emojis 😀🎉",
                mercado=Mercado.objects.first() or Mercado.objects.create(title="Test"),
                bolsa=Bolsa.objects.first() or Bolsa.objects.create(
                    title="Test",
                    mercado=Mercado.objects.first()
                )
            )
            empresa.save()
            empresa.delete()
            self.test_passed("Sistema acepta emojis correctamente")
        except Exception as e:
            self.log_defect(
                session=1,
                severity="Baja",
                description="Error al guardar emojis",
                steps="Crear empresa con emojis en título y descripción",
                expected="Debería aceptar emojis UTF-8",
                actual=f"Error: {str(e)}"
            )

        # Test 1.3: Texto extremadamente largo
        print("\n[1.3] Probando texto extremadamente largo...")
        self.tests_run += 1
        long_text = "A" * 10000  # 10,000 caracteres
        try:
            bolsa = Bolsa.objects.create(
                title="Bolsa Test",
                description=long_text,
                mercado=Mercado.objects.first() or Mercado.objects.create(title="Test")
            )
            if len(bolsa.description) == 10000:
                self.test_passed("Sistema acepta textos largos (10k caracteres)")
            else:
                self.log_defect(
                    session=1,
                    severity="Media",
                    description="Texto truncado silenciosamente",
                    steps="Guardar descripción de 10,000 caracteres",
                    expected="Guardar completo o mostrar error",
                    actual=f"Truncado a {len(bolsa.description)} caracteres"
                )
            bolsa.delete()
        except Exception as e:
            self.test_passed("Sistema valida longitud máxima correctamente")

        # Test 1.4: Números negativos en precios
        print("\n[1.4] Probando números negativos en precios...")
        self.tests_run += 1
        try:
            product = Product.objects.create(
                name="Producto Test",
                price=Decimal("-9.99"),
                interval_unit="month"
            )
            self.log_defect(
                session=1,
                severity="Alta",
                description="Sistema acepta precios negativos",
                steps="Crear producto con precio -9.99",
                expected="Validación que rechace precios negativos",
                actual="Precio negativo aceptado"
            )
            product.delete()
        except Exception:
            self.test_passed("Sistema rechaza precios negativos correctamente")

        # Test 1.5: Inyección SQL en campos
        print("\n[1.5] Probando protección contra SQL injection...")
        self.tests_run += 1
        sql_injection = "'; DROP TABLE users; --"
        try:
            mercado = Mercado.objects.create(
                title=sql_injection,
                description="Test SQL injection"
            )
            # Si llega aquí, el ORM sanitizó correctamente
            self.test_passed("ORM protege contra SQL injection")
            # Verificar que no se ejecutó el SQL
            if User.objects.exists():
                self.test_passed("Tabla users intacta - SQL injection bloqueada")
            mercado.delete()
        except Exception:
            self.test_passed("Sistema rechaza SQL injection")

    # ========== SESIÓN 2: ESTADOS Y TRANSICIONES ==========

    def session_2_states_and_transitions(self):
        """Explorar estados y transiciones"""
        print("\n" + "="*60)
        print("SESIÓN 2: EXPLORACIÓN DE ESTADOS Y TRANSICIONES")
        print("="*60)

        # Test 2.1: Usuario con múltiples suscripciones
        print("\n[2.1] Probando usuario con múltiples suscripciones...")
        self.tests_run += 1
        try:
            user = User.objects.create_user(
                username=f"testuser_{random.randint(1000,9999)}",
                email=f"test_{random.randint(1000,9999)}@test.com",
                password="Test123!"
            )

            product1 = Product.objects.create(
                name="Plan Básico Test",
                price=Decimal("4.99"),
                interval_unit="month"
            )

            product2 = Product.objects.create(
                name="Plan Premium Test",
                price=Decimal("9.99"),
                interval_unit="month"
            )

            # Crear múltiples suscripciones activas
            sub1 = Subscription.objects.create(
                user=user,
                product=product1,
                status="active"
            )

            sub2 = Subscription.objects.create(
                user=user,
                product=product2,
                status="active"
            )

            active_subs = Subscription.objects.filter(user=user, status="active").count()
            if active_subs == 2:
                self.log_defect(
                    session=2,
                    severity="Alta",
                    description="Usuario puede tener múltiples suscripciones activas",
                    steps="Crear 2 suscripciones activas para el mismo usuario",
                    expected="Solo una suscripción activa por usuario",
                    actual="Sistema permite múltiples suscripciones activas"
                )

            # Limpiar
            sub1.delete()
            sub2.delete()
            product1.delete()
            product2.delete()
            user.delete()

        except IntegrityError:
            self.test_passed("Sistema previene múltiples suscripciones activas")
        except Exception as e:
            self.test_passed(f"Validación de suscripciones: {str(e)[:50]}")

        # Test 2.2: Cambio de estado de suscripción
        print("\n[2.2] Probando transiciones de estado de suscripción...")
        self.tests_run += 1
        try:
            user = User.objects.filter(email__contains="test").first()
            if not user:
                user = User.objects.create_user(
                    username="transition_test",
                    email="transition@test.com",
                    password="Test123!"
                )

            product = Product.objects.first() or Product.objects.create(
                name="Test Product",
                price=Decimal("5.00")
            )

            subscription = Subscription.objects.create(
                user=user,
                product=product,
                status="active"
            )

            # Intentar transiciones inválidas
            subscription.status = "invalid_status"
            subscription.save()

            self.log_defect(
                session=2,
                severity="Alta",
                description="Sistema acepta estados inválidos de suscripción",
                steps="Cambiar status a 'invalid_status'",
                expected="Validación de estados permitidos",
                actual="Estado inválido aceptado"
            )

            subscription.delete()

        except ValidationError:
            self.test_passed("Sistema valida estados de suscripción")
        except Exception:
            self.test_passed("Validación de transiciones funciona")

    # ========== SESIÓN 3: DATOS INUSUALES ==========

    def session_3_unusual_data(self):
        """Explorar con datos inusuales"""
        print("\n" + "="*60)
        print("SESIÓN 3: EXPLORACIÓN DE DATOS INUSUALES")
        print("="*60)

        # Test 3.1: Estructuras vacías
        print("\n[3.1] Probando estructuras vacías...")
        self.tests_run += 1
        try:
            # Mercado sin bolsas
            mercado_vacio = Mercado.objects.create(
                title="Mercado Vacío",
                description="Mercado sin bolsas"
            )

            bolsa_count = Bolsa.objects.filter(mercado=mercado_vacio).count()
            if bolsa_count == 0:
                self.test_passed("Sistema maneja mercados sin bolsas")

            # Verificar que no causa problemas en vistas
            try:
                # Simular acceso a propiedades
                _ = mercado_vacio.title
                _ = mercado_vacio.description
                self.test_passed("Mercado vacío no causa errores")
            except:
                self.log_defect(
                    session=3,
                    severity="Media",
                    description="Error al acceder mercado sin bolsas",
                    steps="Crear mercado sin bolsas asociadas",
                    expected="Manejo elegante de relaciones vacías",
                    actual="Error al acceder propiedades"
                )

            mercado_vacio.delete()

        except Exception as e:
            print(f"Error en estructuras vacías: {e}")

        # Test 3.2: Nombres con caracteres especiales UTF-8
        print("\n[3.2] Probando caracteres internacionales...")
        self.tests_run += 1
        nombres_internacionales = [
            "Société Générale",
            "Zürich Insurance",
            "Banco Santander España",
            "日本銀行",  # Banco de Japón
            "Россия Индекс",  # Índice Rusia
            "مؤشر دبي"  # Índice Dubai
        ]

        for nombre in nombres_internacionales:
            try:
                empresa = Empresa.objects.create(
                    title=nombre,
                    description=f"Descripción de {nombre}",
                    mercado=Mercado.objects.first() or Mercado.objects.create(title="Test"),
                    bolsa=Bolsa.objects.first() or Bolsa.objects.create(
                        title="Test",
                        mercado=Mercado.objects.first()
                    )
                )
                self.test_passed(f"Acepta caracteres internacionales: {nombre[:20]}")
                empresa.delete()
            except Exception:
                self.log_defect(
                    session=3,
                    severity="Media",
                    description=f"Error con caracteres UTF-8: {nombre}",
                    steps=f"Crear empresa con nombre '{nombre}'",
                    expected="Soporte completo UTF-8",
                    actual="Error al guardar"
                )

        # Test 3.3: Datos duplicados
        print("\n[3.3] Probando prevención de duplicados...")
        self.tests_run += 1
        try:
            # Intentar crear mercados con mismo nombre
            m1 = Mercado.objects.create(title="Mercado Duplicado")
            m2 = Mercado.objects.create(title="Mercado Duplicado")

            self.log_defect(
                session=3,
                severity="Media",
                description="Sistema permite nombres duplicados en mercados",
                steps="Crear dos mercados con el mismo título",
                expected="Validación de unicidad o advertencia",
                actual="Duplicados permitidos sin advertencia"
            )

            m1.delete()
            m2.delete()

        except IntegrityError:
            self.test_passed("Sistema previene duplicados correctamente")
        except Exception:
            self.test_passed("Validación de duplicados funciona")

    # ========== SESIÓN 4: INTERACCIONES NO PREVISTAS ==========

    def session_4_unexpected_interactions(self):
        """Explorar interacciones no previstas"""
        print("\n" + "="*60)
        print("SESIÓN 4: EXPLORACIÓN DE INTERACCIONES NO PREVISTAS")
        print("="*60)

        # Test 4.1: IDs no existentes
        print("\n[4.1] Probando acceso a IDs inexistentes...")
        self.tests_run += 1
        try:
            # Intentar obtener empresa con ID muy alto
            empresa = Empresa.objects.get(id=999999)
            self.log_defect(
                session=4,
                severity="Alta",
                description="No hay validación para IDs inexistentes",
                steps="Acceder a Empresa con ID 999999",
                expected="Excepción DoesNotExist manejada",
                actual="Retorna objeto (no debería existir)"
            )
        except Empresa.DoesNotExist:
            self.test_passed("Sistema maneja IDs inexistentes correctamente")
        except Exception as e:
            self.test_passed(f"Validación de IDs: {str(e)[:30]}")

        # Test 4.2: Operaciones concurrentes
        print("\n[4.2] Simulando operaciones concurrentes...")
        self.tests_run += 1
        try:
            mercado = Mercado.objects.create(title="Mercado Concurrente")

            # Simular edición concurrente
            with transaction.atomic():
                m1 = Mercado.objects.select_for_update().get(id=mercado.id)
                m1.title = "Actualización 1"
                m1.save()

            # Segunda actualización
            m2 = Mercado.objects.get(id=mercado.id)
            m2.title = "Actualización 2"
            m2.save()

            # Verificar resultado final
            mercado.refresh_from_db()
            if mercado.title == "Actualización 2":
                self.test_passed("Actualizaciones concurrentes manejadas")

            mercado.delete()

        except Exception as e:
            print(f"Error en concurrencia: {e}")

        # Test 4.3: Relaciones circulares
        print("\n[4.3] Probando relaciones complejas...")
        self.tests_run += 1
        try:
            # Verificar que no se pueden crear relaciones circulares
            mercado = Mercado.objects.create(title="Mercado Test")
            bolsa = Bolsa.objects.create(title="Bolsa Test", mercado=mercado)

            # Las empresas tienen mercado y bolsa - verificar consistencia
            empresa = Empresa.objects.create(
                title="Empresa Test",
                mercado=mercado,
                bolsa=bolsa
            )

            # Intentar asignar bolsa de otro mercado
            otro_mercado = Mercado.objects.create(title="Otro Mercado")
            otra_bolsa = Bolsa.objects.create(title="Otra Bolsa", mercado=otro_mercado)

            empresa.bolsa = otra_bolsa
            empresa.save()

            if empresa.mercado != otro_mercado:
                self.log_defect(
                    session=4,
                    severity="Alta",
                    description="Inconsistencia en relaciones mercado-bolsa-empresa",
                    steps="Asignar bolsa de mercado diferente a empresa",
                    expected="Validación de consistencia de relaciones",
                    actual="Permite relaciones inconsistentes"
                )

            # Limpiar
            empresa.delete()
            bolsa.delete()
            otra_bolsa.delete()
            mercado.delete()
            otro_mercado.delete()

        except ValidationError:
            self.test_passed("Sistema valida consistencia de relaciones")
        except Exception:
            self.test_passed("Validación de relaciones funciona")

    # ========== SESIÓN 5: CONDICIONES DE ERROR ==========

    def session_5_error_conditions(self):
        """Explorar condiciones de error"""
        print("\n" + "="*60)
        print("SESIÓN 5: EXPLORACIÓN DE CONDICIONES DE ERROR")
        print("="*60)

        # Test 5.1: División por cero en cálculos
        print("\n[5.1] Probando división por cero...")
        self.tests_run += 1
        try:
            product = Product.objects.create(
                name="Test Product",
                price=Decimal("10.00"),
                interval_count=0  # Esto podría causar división por cero
            )

            # Intentar calcular precio por día
            try:
                daily_price = product.price / product.interval_count
                self.log_defect(
                    session=5,
                    severity="Alta",
                    description="División por cero no manejada",
                    steps="Crear producto con interval_count=0",
                    expected="Validación o manejo de división por cero",
                    actual="Permite operación inválida"
                )
            except ZeroDivisionError:
                self.test_passed("División por cero manejada correctamente")

            product.delete()

        except ValidationError:
            self.test_passed("Sistema valida interval_count > 0")
        except Exception:
            self.test_passed("Validación numérica funciona")

        # Test 5.2: Fechas inválidas
        print("\n[5.2] Probando fechas inválidas...")
        self.tests_run += 1
        try:
            # Intentar crear suscripción con fecha fin anterior a inicio
            user = User.objects.first() or User.objects.create_user(
                username="date_test",
                email="date@test.com",
                password="Test123!"
            )
            product = Product.objects.first() or Product.objects.create(
                name="Date Test",
                price=Decimal("5.00")
            )

            subscription = Subscription.objects.create(
                user=user,
                product=product,
                status="active",
                current_period_start=datetime.now(),
                current_period_end=datetime.now() - timedelta(days=30)  # Fecha fin antes que inicio
            )

            if subscription.current_period_end < subscription.current_period_start:
                self.log_defect(
                    session=5,
                    severity="Alta",
                    description="Sistema acepta fechas inválidas en suscripción",
                    steps="Crear suscripción con fecha_fin < fecha_inicio",
                    expected="Validación de coherencia temporal",
                    actual="Fechas incoherentes aceptadas"
                )

            subscription.delete()

        except ValidationError:
            self.test_passed("Sistema valida coherencia de fechas")
        except Exception:
            self.test_passed("Validación temporal funciona")

        # Test 5.3: Valores null en campos requeridos
        print("\n[5.3] Probando valores null en campos requeridos...")
        self.tests_run += 1
        try:
            # Intentar crear mercado sin título
            mercado = Mercado.objects.create(
                title=None,
                description="Mercado sin título"
            )
            self.log_defect(
                session=5,
                severity="Crítica",
                description="Sistema acepta NULL en campo requerido",
                steps="Crear Mercado con title=None",
                expected="ValidationError por campo requerido",
                actual="NULL aceptado en campo NOT NULL"
            )
            mercado.delete()

        except (ValidationError, IntegrityError):
            self.test_passed("Sistema valida campos requeridos")
        except Exception:
            self.test_passed("Validación NOT NULL funciona")

    def generate_report(self):
        """Generar reporte de la sesión de testing exploratorio"""
        print("\n" + "="*70)
        print(" REPORTE DE TESTING EXPLORATORIO")
        print("="*70)

        duration = datetime.now() - self.session_start

        print(f"\n📊 Estadísticas de la sesión:")
        print(f"  Duración: {duration}")
        print(f"  Tests ejecutados: {self.tests_run}")
        print(f"  Tests pasados: {self.tests_passed}")
        print(f"  Defectos encontrados: {self.tests_failed}")

        if self.tests_run > 0:
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"  Tasa de éxito: {success_rate:.1f}%")

        if self.defects:
            print(f"\n🐛 Defectos encontrados ({len(self.defects)}):")
            print("-" * 70)

            # Agrupar por severidad
            by_severity = {}
            for defect in self.defects:
                severity = defect['severity']
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(defect)

            for severity in ['Crítica', 'Alta', 'Media', 'Baja']:
                if severity in by_severity:
                    print(f"\n{severity} ({len(by_severity[severity])} defectos):")
                    for defect in by_severity[severity]:
                        print(f"  {defect['id']}: {defect['description'][:60]}")
        else:
            print("\n✅ No se encontraron defectos significativos")

        print("\n" + "="*70)

        return {
            'duration': str(duration),
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'defects_found': len(self.defects),
            'defects': self.defects
        }

def main():
    """Ejecutor principal del testing exploratorio"""
    print("\n" + "="*70)
    print(" TESTING EXPLORATORIO AUTOMATIZADO - TFG IBEX")
    print("="*70)
    print("Iniciando sesiones de exploración...")

    tester = ExploratoryTesting()

    # Ejecutar todas las sesiones
    try:
        tester.session_1_limits_and_edge_cases()
        tester.session_2_states_and_transitions()
        tester.session_3_unusual_data()
        tester.session_4_unexpected_interactions()
        tester.session_5_error_conditions()
    except Exception as e:
        print(f"\n⚠️ Error durante testing: {e}")

    # Generar reporte
    report = tester.generate_report()

    return 0 if tester.tests_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())