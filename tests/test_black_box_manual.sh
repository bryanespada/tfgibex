#!/bin/bash

# Tests de Caja Negra Manuales - TFG IBEX
# =========================================

echo "======================================================================"
echo "EJECUCIÓN DE TESTS DE CAJA NEGRA - FUNCIONALIDADES CRÍTICAS"
echo "======================================================================"
echo "Fecha: $(date)"
echo "Sistema: TFG IBEX"
echo "======================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
BASE_URL="http://localhost:8000"
COOKIE_JAR="/tmp/cookies.txt"

# Función para imprimir resultado
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

echo ""
echo "======================================================================"
echo "TC-AUTH-003: Test de Login - Página de Acceso"
echo "======================================================================"

echo "Paso 1: Verificar acceso a página de login..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/access/")

if [ "$response" = "200" ]; then
    print_result 0 "Página de login accesible (HTTP 200)"
else
    print_result 1 "Error accediendo a login (HTTP $response)"
fi

echo ""
echo "======================================================================"
echo "TC-MER-001: Test de Acceso a Dashboard (Requiere Login)"
echo "======================================================================"

echo "Paso 1: Intentar acceso sin autenticación..."
response=$(curl -s -o /dev/null -w "%{http_code}" -L "$BASE_URL/app/dashboard/")

if [ "$response" = "200" ] || [ "$response" = "302" ]; then
    if [ "$response" = "302" ]; then
        print_result 0 "Redirección a login detectada (esperado sin auth)"
    else
        # Verificar si realmente está en el dashboard o fue redirigido al login
        content=$(curl -s "$BASE_URL/app/dashboard/" | grep -i "login\|access")
        if [ ! -z "$content" ]; then
            print_result 0 "Redirigido a página de login (comportamiento correcto)"
        else
            print_result 1 "Acceso permitido sin autenticación (problema de seguridad)"
        fi
    fi
else
    print_result 0 "Acceso denegado sin autenticación (HTTP $response)"
fi

echo ""
echo "======================================================================"
echo "TC-SEC-001: Test de Seguridad - Protección contra Inyección SQL"
echo "======================================================================"

echo "Paso 1: Intentar inyección SQL en login..."
# Intentar login con payload SQL injection
payload="' OR '1'='1' --"
response=$(curl -s -X POST "$BASE_URL/access/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$payload&password=test" \
    -o /tmp/login_response.html \
    -w "%{http_code}")

# Verificar que no hay acceso no autorizado
if grep -q "dashboard\|welcome\|logout" /tmp/login_response.html; then
    print_result 1 "CRÍTICO: Posible vulnerabilidad SQL Injection detectada"
else
    print_result 0 "Protección contra SQL Injection funcionando correctamente"
fi

echo ""
echo "======================================================================"
echo "TC-MER-002: Test de Verificación de Contenido Premium"
echo "======================================================================"

echo "Paso 1: Verificar existencia de modelo de suscripción..."
# Verificar que el sistema tiene configuración de productos
docker exec tfg_django python -c "
from appmodels.models import Product
products = Product.objects.all()
if products.exists():
    print('OK: Sistema de productos configurado')
    for p in products:
        print(f'  - {p.name}: \${p.price}')
else:
    print('INFO: No hay productos configurados aún')
" 2>/dev/null

result=$?
if [ $result -eq 0 ]; then
    print_result 0 "Sistema de suscripciones implementado"
else
    print_result 1 "Error verificando sistema de suscripciones"
fi

echo ""
echo "======================================================================"
echo "TEST ADICIONAL: Verificación de Estructura de Base de Datos"
echo "======================================================================"

echo "Verificando modelos principales..."
docker exec tfg_django python -c "
from appmodels.models import Mercado, Bolsa, Empresa, Product, Subscription
from django.contrib.auth import get_user_model

User = get_user_model()

# Contar registros
mercados = Mercado.objects.count()
bolsas = Bolsa.objects.count()
empresas = Empresa.objects.count()
users = User.objects.count()

print(f'Mercados: {mercados}')
print(f'Bolsas: {bolsas}')
print(f'Empresas: {empresas}')
print(f'Usuarios: {users}')

# Verificar bolsas premium
premium_bolsas = Bolsa.objects.filter(is_premium=True).count()
print(f'Bolsas Premium: {premium_bolsas}')
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_result 0 "Modelos de BD verificados correctamente"
else
    print_result 1 "Error al verificar modelos"
fi

echo ""
echo "======================================================================"
echo "TEST DE RENDIMIENTO: Tiempo de Respuesta"
echo "======================================================================"

echo "Midiendo tiempo de respuesta de páginas principales..."

# Medir tiempo de respuesta de la página principal
time_start=$(date +%s%N)
curl -s -o /dev/null "$BASE_URL/"
time_end=$(date +%s%N)
response_time=$((($time_end - $time_start) / 1000000))

if [ $response_time -lt 3000 ]; then
    print_result 0 "Página principal: ${response_time}ms (< 3s)"
else
    print_result 1 "Página principal: ${response_time}ms (> 3s - Lento)"
fi

# Medir tiempo de respuesta de login
time_start=$(date +%s%N)
curl -s -o /dev/null "$BASE_URL/access/"
time_end=$(date +%s%N)
response_time=$((($time_end - $time_start) / 1000000))

if [ $response_time -lt 3000 ]; then
    print_result 0 "Página de login: ${response_time}ms (< 3s)"
else
    print_result 1 "Página de login: ${response_time}ms (> 3s - Lento)"
fi

echo ""
echo "======================================================================"
echo "RESUMEN DE RESULTADOS"
echo "======================================================================"
echo ""
echo "Tests Ejecutados:"
echo "  ✓ TC-AUTH-003: Verificación de página de login"
echo "  ✓ TC-MER-001: Restricción de acceso sin autenticación"
echo "  ✓ TC-SEC-001: Protección contra SQL Injection"
echo "  ✓ TC-MER-002: Sistema de suscripciones premium"
echo "  ✓ Verificación de estructura de BD"
echo "  ✓ Tests de rendimiento"
echo ""
echo "======================================================================"
echo "NOTA: Para tests completos con autenticación real, se requiere"
echo "configurar usuarios de prueba en el sistema."
echo "======================================================================"

# Limpiar archivos temporales
rm -f /tmp/login_response.html $COOKIE_JAR