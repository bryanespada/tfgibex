"""
Sistema de Clasificación de Mercados y Empresas
==============================================

Este archivo contiene la base de datos que nos permite clasificar automáticamente
las empresas en su mercado y bolsa correspondiente.

Estructura:
- MARKET_CLASSIFICATION: Base de datos principal
- COMPANY_TO_MARKET: Mapeo inverso para búsqueda rápida
"""

# Base de datos principal de mercados, bolsas y empresas
MARKET_CLASSIFICATION = {
    'european': {
        'name': 'Mercado Europeo',
        'description': 'Principales bolsas europeas incluyendo IBEX 35, DAX y más',
        'exchanges': {
            'madrid': {
                'name': 'Bolsa de Madrid',
                'description': 'IBEX 35 - Principal índice bursátil de España',
                'index': 'IBEX 35',
                'country': 'España',
                'companies': [
                    # Empresas principales del IBEX 35
                    'Banco Santander', 'BBVA', 'Telefónica', 'Iberdrola', 'Repsol',
                    'Inditex', 'Ferrovial', 'CaixaBank', 'Aena', 'Endesa',
                    'Red Eléctrica', 'Naturgy', 'IAG', 'Mapfre', 'ACS',
                    'Acerinox', 'Amadeus', 'ArcelorMittal', 'Bankinter', 'Cellnex'
                ]
            },
            'frankfurt': {
                'name': 'Bolsa de Frankfurt',
                'description': 'DAX - Índice bursátil alemán',
                'index': 'DAX',
                'country': 'Alemania',
                'companies': [
                    # Empresas principales del DAX
                    'SAP', 'Volkswagen', 'Siemens', 'Allianz', 'BMW',
                    'Deutsche Bank', 'Bayer', 'Adidas', 'Mercedes-Benz', 'BASF',
                    'Deutsche Post', 'Infineon', 'Henkel', 'Continental'
                ]
            }
        }
    },
    'american': {
        'name': 'Mercado Americano',
        'description': 'Bolsas de Estados Unidos - NYSE y NASDAQ',
        'exchanges': {
            'nyse': {
                'name': 'NYSE',
                'description': 'New York Stock Exchange - La bolsa más grande del mundo',
                'index': 'S&P 500',
                'country': 'Estados Unidos',
                'companies': [
                    # Empresas principales de NYSE
                    'JPMorgan Chase', 'Johnson & Johnson', 'Procter & Gamble',
                    'Coca-Cola', 'Mastercard', 'Visa', 'Home Depot', 'Disney',
                    'McDonald\'s', 'Nike', 'Walmart', 'Berkshire Hathaway',
                    'Exxon Mobil', 'Bank of America', 'Wells Fargo'
                ]
            },
            'nasdaq': {
                'name': 'NASDAQ',
                'description': 'Bolsa especializada en empresas tecnológicas',
                'index': 'NASDAQ 100',
                'country': 'Estados Unidos',
                'companies': [
                    # Empresas tecnológicas principales
                    'Apple', 'Microsoft', 'Amazon', 'Google', 'Tesla',
                    'Meta', 'Netflix', 'Adobe', 'Intel', 'Oracle',
                    'Salesforce', 'PayPal', 'Zoom', 'Moderna', 'NVIDIA'
                ]
            }
        }
    }
}


def generate_company_lookup():
    """
    Genera un mapeo inverso para búsqueda rápida de empresas

    ¿Qué hace?
    - Convierte la estructura jerárquica en un diccionario plano
    - Permite buscar rápidamente: empresa → mercado/bolsa

    Ejemplo de salida:
    {
        'banco santander': {
            'market': 'european',
            'exchange': 'madrid',
            'market_name': 'Mercado Europeo',
            'exchange_name': 'Bolsa de Madrid'
        }
    }
    """
    company_lookup = {}

    for market_key, market_data in MARKET_CLASSIFICATION.items():
        for exchange_key, exchange_data in market_data['exchanges'].items():
            for company in exchange_data['companies']:
                company_lookup[company.lower()] = {
                    'market': market_key,
                    'exchange': exchange_key,
                    'market_name': market_data['name'],
                    'exchange_name': exchange_data['name'],
                    'country': exchange_data['country'],
                    'index': exchange_data['index']
                }

    return company_lookup


# Generar el mapeo al importar el módulo
COMPANY_TO_MARKET = generate_company_lookup()


def find_company_info(company_name):
    """
    Busca información de una empresa en nuestra base de datos

    Args:
        company_name (str): Nombre de la empresa a buscar

    Returns:
        dict or None: Información de la empresa si se encuentra

    Ejemplo:
        info = find_company_info("Banco Santander")
        print(info['market_name'])  # "Mercado Europeo"
    """
    company_lower = company_name.lower()

    # Búsqueda exacta
    if company_lower in COMPANY_TO_MARKET:
        return COMPANY_TO_MARKET[company_lower]

    # Búsqueda parcial (para variaciones como "Apple Inc." vs "Apple")
    for known_company, info in COMPANY_TO_MARKET.items():
        if known_company in company_lower or company_lower in known_company:
            return info

    return None


def get_companies_by_market(market_name):
    """
    Obtiene todas las empresas de un mercado específico

    Args:
        market_name (str): 'european' o 'american'

    Returns:
        list: Lista de nombres de empresas
    """
    companies = []

    if market_name in MARKET_CLASSIFICATION:
        market_data = MARKET_CLASSIFICATION[market_name]
        for exchange_data in market_data['exchanges'].values():
            companies.extend(exchange_data['companies'])

    return companies


def get_companies_by_exchange(market_name, exchange_name):
    """
    Obtiene todas las empresas de una bolsa específica

    Args:
        market_name (str): 'european' o 'american'
        exchange_name (str): 'madrid', 'frankfurt', 'nyse', 'nasdaq'

    Returns:
        list: Lista de nombres de empresas
    """
    try:
        return MARKET_CLASSIFICATION[market_name]['exchanges'][exchange_name]['companies']
    except KeyError:
        return []


# Función de prueba para verificar que todo funciona
def test_classification_system():
    """
    Función de prueba para verificar que el sistema de clasificación funciona
    """
    print("=== PRUEBA DEL SISTEMA DE CLASIFICACIÓN ===")

    # Probar búsquedas
    test_companies = ["Banco Santander", "Apple", "SAP", "tesla", "unknown company"]

    for company in test_companies:
        info = find_company_info(company)
        if info:
            print(f"✅ {company}: {info['exchange_name']} ({info['market_name']})")
        else:
            print(f"❌ {company}: No encontrada")

    # Mostrar estadísticas
    total_companies = len(COMPANY_TO_MARKET)
    european_companies = len(get_companies_by_market('european'))
    american_companies = len(get_companies_by_market('american'))

    print(f"\n📊 Estadísticas:")
    print(f"Total empresas: {total_companies}")
    print(f"Empresas europeas: {european_companies}")
    print(f"Empresas americanas: {american_companies}")


if __name__ == "__main__":
    # Si ejecutamos este archivo directamente, hacer pruebas
    test_classification_system()