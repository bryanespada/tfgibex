#!/usr/bin/env python3
"""
Script de prueba para el gestor de entidades
Ejecutar con: python test_entity_manager.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Ahora podemos importar nuestros modelos
from appmodels.utils.entity_manager import FinancialEntityManager

def main():
    print("=== PRUEBA DEL GESTOR DE ENTIDADES CON DJANGO ===")

    manager = FinancialEntityManager()

    # Probar con empresas conocidas y desconocidas
    test_companies = [
        "Banco Santander",  # Conocida - Madrid
        "Apple",            # Conocida - NASDAQ
        "Volkswagen",       # Conocida - Frankfurt
        "Empresa Inventada" # Desconocida - por defecto Madrid
    ]

    print(f"\n🧪 Probando con {len(test_companies)} empresas...")

    for i, company in enumerate(test_companies, 1):
        print(f"\n--- Prueba {i}/{len(test_companies)} ---")
        try:
            empresa, info = manager.classify_and_create_entities(company)
            print(f"✅ ÉXITO: {company}")
            print(f"   → Mercado: {info['market']}")
            print(f"   → Bolsa: {info['exchange']}")
            print(f"   → Empresa ID: {empresa.id}")
            print(f"   → Encontrada en BD: {'Sí' if info['found_in_db'] else 'No'}")
        except Exception as e:
            print(f"❌ ERROR con {company}: {e}")
            import traceback
            traceback.print_exc()

    # Mostrar estadísticas finales
    print(f"\n📊 Estadísticas finales:")
    stats = manager.get_statistics()
    print(f"Entidades creadas en esta sesión:")
    for entity_type, count in stats['created'].items():
        print(f"  - {entity_type}: {count}")

    print(f"\nTotal en base de datos:")
    for entity_type, count in stats['total_in_db'].items():
        print(f"  - {entity_type}: {count}")

if __name__ == "__main__":
    main()