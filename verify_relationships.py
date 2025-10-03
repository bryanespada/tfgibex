#!/usr/bin/env python
"""
Script to verify the relationships between Mercado, Bolsa, Empresa and Noticia models
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from appmodels.models import Mercado, Bolsa, Empresa, Noticia
from django.db.models import Count

print("=" * 80)
print("VERIFICACIÓN DE RELACIONES EN LA BASE DE DATOS")
print("=" * 80)

# 1. Verify Mercados
print("\n1. MERCADOS:")
print("-" * 40)
mercados = Mercado.objects.all()
for mercado in mercados:
    bolsa_count = Bolsa.objects.filter(mercado=mercado).count()
    empresa_count = Empresa.objects.filter(mercado=mercado).count()
    print(f"✓ {mercado.title}")
    print(f"  - Bolsas asociadas: {bolsa_count}")
    print(f"  - Empresas asociadas: {empresa_count}")

# 2. Verify Bolsas
print("\n2. BOLSAS:")
print("-" * 40)
bolsas = Bolsa.objects.all()
for bolsa in bolsas:
    empresa_count = bolsa.empresas.count()
    print(f"✓ {bolsa.title}")
    print(f"  - Mercado: {bolsa.mercado.title}")
    print(f"  - Empresas asociadas: {empresa_count}")
    if empresa_count > 0:
        empresas = bolsa.empresas.all()[:3]  # Show first 3
        for empresa in empresas:
            print(f"    • {empresa.title}")

# 3. Verify Empresas
print("\n3. EMPRESAS:")
print("-" * 40)
empresas = Empresa.objects.all()
for empresa in empresas:
    noticias_count = empresa.noticias.count()
    bolsas_list = empresa.bolsas.all()
    print(f"✓ {empresa.title}")
    print(f"  - Mercado: {empresa.mercado.title if empresa.mercado else 'No asignado'}")
    print(f"  - Bolsas: {', '.join([b.title for b in bolsas_list]) if bolsas_list else 'No asignada'}")
    print(f"  - Noticias asociadas: {noticias_count}")
    print(f"  - Pública: {'Sí' if empresa.public else 'No'}")

# 4. Verify Noticias
print("\n4. NOTICIAS:")
print("-" * 40)
noticias = Noticia.objects.all()
total_noticias = noticias.count()
premium_count = noticias.filter(is_premium=True).count()
public_count = noticias.filter(public=True).count()

print(f"Total de noticias: {total_noticias}")
print(f"  - Públicas: {public_count}")
print(f"  - Premium: {premium_count}")
print(f"  - Gratuitas: {total_noticias - premium_count}")

# Show distribution by company
print("\nDistribución por empresa:")
empresa_noticias = Noticia.objects.values('empresa__title').annotate(count=Count('id')).order_by('-count')
for item in empresa_noticias[:5]:  # Show top 5
    print(f"  • {item['empresa__title']}: {item['count']} noticias")

# 5. Data integrity check
print("\n5. VERIFICACIÓN DE INTEGRIDAD:")
print("-" * 40)

# Check for orphaned records
empresas_sin_mercado = Empresa.objects.filter(mercado__isnull=True).count()
empresas_sin_bolsa = Empresa.objects.filter(bolsas__isnull=True).count()
noticias_sin_empresa = Noticia.objects.filter(empresa__isnull=True).count()

if empresas_sin_mercado == 0:
    print("✅ Todas las empresas tienen mercado asignado")
else:
    print(f"⚠️  {empresas_sin_mercado} empresas sin mercado asignado")

if empresas_sin_bolsa == 0:
    print("✅ Todas las empresas tienen al menos una bolsa asignada")
else:
    print(f"⚠️  {empresas_sin_bolsa} empresas sin bolsa asignada")

if noticias_sin_empresa == 0:
    print("✅ Todas las noticias tienen empresa asignada")
else:
    print(f"⚠️  {noticias_sin_empresa} noticias sin empresa asignada")

# Check ManyToMany relationships
print("\n6. RELACIONES MANY-TO-MANY (Empresa-Bolsa):")
print("-" * 40)
for empresa in Empresa.objects.all()[:5]:  # Show first 5
    bolsas = empresa.bolsas.all()
    if bolsas.exists():
        print(f"✓ {empresa.title} está en: {', '.join([b.title for b in bolsas])}")
    else:
        print(f"⚠️  {empresa.title} no está asociada a ninguna bolsa")

print("\n" + "=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)