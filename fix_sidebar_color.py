#!/usr/bin/env python
"""
Script para restaurar el color del sidebar al valor original
Ejecutar con: python manage.py shell < fix_sidebar_color.py
"""

from appmodels.models import GeneralConfig

# Obtener la configuración
config = GeneralConfig.objects.first()

if config:
    print(f"Color actual: {config.app_primary}")

    # Restaurar al color original (azul oscuro/gris)
    config.app_primary = '#2A3F54'
    config.save()

    print("✅ Color restaurado a: #2A3F54")
    print("El menú lateral ahora debería verse correctamente")
else:
    # Crear configuración con valores por defecto si no existe
    config = GeneralConfig.objects.create(
        app_name='TFG IBEX',
        app_primary='#2A3F54'
    )
    print("✅ Configuración creada con color por defecto: #2A3F54")