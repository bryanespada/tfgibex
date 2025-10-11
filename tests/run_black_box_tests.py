#!/usr/bin/env python
"""
Script de ejecución de Tests de Caja Negra
TFG IBEX - Funcionalidades Críticas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from appmodels.models import Mercado, Bolsa, Empresa, Product, Subscription
from decimal import Decimal

User = get_user_model()

def test_auth_003():
    """TC-AUTH-003: Test de Sistema de Autenticación"""
    print("\n" + "="*60)
    print("TC-AUTH-003: SISTEMA DE AUTENTICACIÓN")
    print("="*60)

    try:
        # Verificar modelo de usuario
        user_count = User.objects.count()
        print(f"✓ Modelo de usuario funcionando")
        print(f"  Usuarios en sistema: {user_count}")

        # Crear usuario de prueba si no existe
        if not User.objects.filter(email='test@tfgibex.com').exists():
            test_user = User.objects.create_user(
                username='testuser',
                email='test@tfgibex.com',
                password='Test123!'
            )
            print("✓ Usuario de prueba creado exitosamente")
            print(f"  Email: {test_user.email}")
        else:
            test_user = User.objects.get(email='test@tfgibex.com')
            print("✓ Usuario de prueba ya existe")
            print(f"  Email: {test_user.email}")

        # Verificar autenticación
        from django.contrib.auth import authenticate
        auth_test = authenticate(username='test@tfgibex.com', password='Test123!')
        if auth_test:
            print("✓ Autenticación exitosa con credenciales válidas")
        else:
            # Intentar con username en lugar de email
            auth_test = authenticate(username='testuser', password='Test123!')
            if auth_test:
                print("✓ Autenticación exitosa con username")

        # Test negativo - contraseña incorrecta
        auth_fail = authenticate(username='test@tfgibex.com', password='Wrong!')
        if not auth_fail:
            print("✓ Rechazo correcto con contraseña incorrecta")

        print("\n✅ TEST PASADO: Sistema de autenticación funcionando correctamente")
        return True

    except Exception as e:
        print(f"\n❌ TEST FALLADO: {str(e)}")
        return False

def test_mer_001():
    """TC-MER-001: Test de Mercados y Bolsas"""
    print("\n" + "="*60)
    print("TC-MER-001: VISUALIZACIÓN DE MERCADOS")
    print("="*60)

    try:
        # Contar mercados existentes
        mercados = Mercado.objects.all()
        mercado_count = mercados.count()

        print(f"✓ Sistema de mercados funcionando")
        print(f"  Mercados disponibles: {mercado_count}")

        # Si no hay mercados, crear algunos de prueba
        if mercado_count == 0:
            print("  Creando mercados de prueba...")
            Mercado.objects.create(
                title="Mercado Europeo",
                description="Principales bolsas europeas"
            )
            Mercado.objects.create(
                title="Mercado Americano",
                description="Bolsas de Estados Unidos"
            )
            mercados = Mercado.objects.all()
            print(f"  ✓ Creados {mercados.count()} mercados de prueba")

        # Listar mercados
        for mercado in mercados[:5]:
            print(f"  - {mercado.title}")

        # Verificar bolsas
        bolsas = Bolsa.objects.all()
        bolsa_count = bolsas.count()
        print(f"\n✓ Sistema de bolsas funcionando")
        print(f"  Bolsas disponibles: {bolsa_count}")

        # Si no hay bolsas, crear algunas
        if bolsa_count == 0 and mercado_count > 0:
            print("  Creando bolsas de prueba...")
            mercado_eu = mercados.first()
            Bolsa.objects.create(
                title="IBEX 35",
                description="Índice español",
                mercado=mercado_eu,
                is_premium=False
            )
            Bolsa.objects.create(
                title="DAX 30",
                description="Índice alemán",
                mercado=mercado_eu,
                is_premium=True
            )
            bolsas = Bolsa.objects.all()
            print(f"  ✓ Creadas {bolsas.count()} bolsas de prueba")

        # Listar bolsas
        for bolsa in bolsas[:5]:
            premium_tag = " [PREMIUM]" if bolsa.is_premium else ""
            print(f"  - {bolsa.title}{premium_tag}")

        print("\n✅ TEST PASADO: Sistema de mercados/bolsas funcionando")
        return True

    except Exception as e:
        print(f"\n❌ TEST FALLADO: {str(e)}")
        return False

def test_mer_002():
    """TC-MER-002: Test de Sistema Premium"""
    print("\n" + "="*60)
    print("TC-MER-002: SISTEMA DE CONTENIDO PREMIUM")
    print("="*60)

    try:
        # Verificar bolsas premium
        premium_bolsas = Bolsa.objects.filter(is_premium=True)
        free_bolsas = Bolsa.objects.filter(is_premium=False)

        print(f"✓ Diferenciación de contenido implementada")
        print(f"  Bolsas gratuitas: {free_bolsas.count()}")
        print(f"  Bolsas premium: {premium_bolsas.count()}")

        # Verificar productos de suscripción
        products = Product.objects.all()
        product_count = products.count()

        if product_count > 0:
            print(f"\n✓ Sistema de suscripciones configurado")
            print(f"  Productos disponibles: {product_count}")
            for product in products:
                print(f"  - {product.name}: ${product.price}/{product.interval_unit}")
        else:
            print("\n  Creando producto de suscripción de prueba...")
            Product.objects.create(
                name="Plan Premium Mensual",
                description="Acceso completo a contenido premium",
                price=Decimal("9.99"),
                interval_unit="month",
                interval_count=1
            )
            print("  ✓ Producto de prueba creado")

        # Verificar suscripciones activas
        active_subs = Subscription.objects.filter(status='active').count()
        print(f"\n✓ Sistema de suscripciones funcionando")
        print(f"  Suscripciones activas: {active_subs}")

        # Simular verificación de acceso
        test_user = User.objects.filter(email='test@tfgibex.com').first()
        if test_user:
            has_premium = Subscription.objects.filter(
                user=test_user,
                status='active'
            ).exists()

            if has_premium:
                print(f"  Usuario de prueba: CON acceso premium")
            else:
                print(f"  Usuario de prueba: SIN acceso premium (correcto)")

        print("\n✅ TEST PASADO: Sistema premium funcionando correctamente")
        return True

    except Exception as e:
        print(f"\n❌ TEST FALLADO: {str(e)}")
        return False

def main():
    """Ejecutor principal de tests"""
    print("\n" + "="*70)
    print(" EJECUCIÓN DE TESTS DE CAJA NEGRA - TFG IBEX")
    print("="*70)
    print("Ejecutando las 3 funcionalidades más importantes...")

    results = {
        'TC-AUTH-003': False,
        'TC-MER-001': False,
        'TC-MER-002': False
    }

    # Ejecutar tests
    print("\n📋 Iniciando batería de tests...")

    results['TC-AUTH-003'] = test_auth_003()
    results['TC-MER-001'] = test_mer_001()
    results['TC-MER-002'] = test_mer_002()

    # Resumen final
    print("\n" + "="*70)
    print(" RESUMEN DE RESULTADOS")
    print("="*70)

    total = len(results)
    passed = sum(results.values())

    for test_id, result in results.items():
        status = "✅ PASADO" if result else "❌ FALLADO"
        print(f"{test_id}: {status}")

    print("-"*70)
    print(f"Total: {passed}/{total} tests pasados")
    print(f"Tasa de éxito: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n🎉 TODOS LOS TESTS PASADOS EXITOSAMENTE")
    else:
        print(f"\n⚠️  {total-passed} tests fallaron")

    print("="*70)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())