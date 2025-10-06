"""
Gestor de Entidades Financieras
==============================

Esta clase se encarga de crear automáticamente Mercados, Bolsas y Empresas
cuando procesamos noticias de GNews.

Flujo:
1. Recibe el nombre de una empresa de una noticia
2. Busca en nuestra base de datos de clasificación
3. Crea automáticamente: Mercado → Bolsa → Empresa
4. Devuelve la empresa lista para asociar la noticia
"""

from .market_classifier import MARKET_CLASSIFICATION, find_company_info


class FinancialEntityManager:
    """
    Gestor principal para crear automáticamente la estructura jerárquica
    """

    def __init__(self):
        print("📊 Inicializando FinancialEntityManager...")
        self.created_entities = {
            'mercados': 0,
            'bolsas': 0,
            'empresas': 0
        }

    def classify_and_create_entities(self, company_name):
        """
        Función principal: clasifica una empresa y crea toda la estructura necesaria

        Args:
            company_name (str): Nombre de la empresa de la noticia

        Returns:
            tuple: (empresa_instance, info_dict)
                - empresa_instance: Objeto Empresa listo para usar
                - info_dict: Información sobre qué se creó

        Ejemplo:
            empresa, info = manager.classify_and_create_entities("Banco Santander")
            # Resultado: empresa apunta a Santander en Bolsa Madrid en Mercado Europeo
        """
        print(f"\n🔍 Procesando empresa: {company_name}")

        # 1. Buscar en nuestra base de datos de clasificación
        company_info = find_company_info(company_name)

        if company_info:
            print(f"✅ Empresa conocida: {company_info['exchange_name']} ({company_info['market_name']})")
            # Empresa conocida - crear estructura completa
            return self._create_known_company_structure(company_name, company_info)
        else:
            print(f"❓ Empresa desconocida, usando clasificación por defecto")
            # Empresa desconocida - usar lógica por defecto
            return self._create_unknown_company_structure(company_name)

    def _create_known_company_structure(self, company_name, company_info):
        """
        Crea la estructura completa para una empresa conocida

        Pasos:
        1. Crear/obtener Mercado
        2. Crear/obtener Bolsa
        3. Crear/obtener Empresa
        4. Establecer relaciones
        """
        print(f"🏗️  Creando estructura para empresa conocida...")

        # 1. Crear o conseguir el Mercado
        mercado = self._get_or_create_mercado(company_info)

        # 2. Crear o conseguir la Bolsa
        bolsa = self._get_or_create_bolsa(company_info, mercado)

        # 3. Crear o conseguir la Empresa
        empresa = self._get_or_create_empresa(company_name, company_info, mercado, bolsa)

        info = {
            'found_in_db': True,
            'market': company_info['market_name'],
            'exchange': company_info['exchange_name'],
            'created_entities': self.created_entities.copy()
        }

        return empresa, info

    def _create_unknown_company_structure(self, company_name):
        """
        Crea estructura para empresa desconocida (por defecto: Europa/Madrid)

        ¿Por qué Madrid por defecto?
        - Asumimos que muchas noticias serán en español
        - Es más fácil clasificar manualmente después
        """
        print(f"🏗️  Creando estructura por defecto (Europa/Madrid)...")

        # Información por defecto
        default_info = {
            'market': 'european',
            'exchange': 'madrid',
            'market_name': 'Mercado Europeo',
            'exchange_name': 'Bolsa de Madrid',
            'country': 'España',
            'index': 'IBEX 35'
        }

        mercado = self._get_or_create_mercado(default_info)
        bolsa = self._get_or_create_bolsa(default_info, mercado)
        empresa = self._get_or_create_empresa(company_name, default_info, mercado, bolsa)

        info = {
            'found_in_db': False,
            'market': default_info['market_name'],
            'exchange': default_info['exchange_name'],
            'created_entities': self.created_entities.copy()
        }

        return empresa, info

    def _get_or_create_mercado(self, company_info):
        """
        Crear o conseguir un Mercado

        ¿Qué hace?
        - Busca si ya existe el mercado
        - Si no existe, lo crea con la información de nuestra base de datos
        """
        from appmodels.models import Mercado

        market_data = MARKET_CLASSIFICATION[company_info['market']]

        mercado, created = Mercado.objects.get_or_create(
            title=market_data['name'],
            defaults={
                'description': market_data['description']
            }
        )

        if created:
            self.created_entities['mercados'] += 1
            print(f"  ✨ Creado Mercado: {mercado.title}")
        else:
            print(f"  ♻️  Mercado existente: {mercado.title}")

        return mercado

    def _get_or_create_bolsa(self, company_info, mercado):
        """
        Crear o conseguir una Bolsa
        """
        from appmodels.models import Bolsa

        exchange_data = MARKET_CLASSIFICATION[company_info['market']]['exchanges'][company_info['exchange']]

        bolsa, created = Bolsa.objects.get_or_create(
            title=exchange_data['name'],
            mercado=mercado,
            defaults={
                'description': exchange_data['description']
            }
        )

        if created:
            self.created_entities['bolsas'] += 1
            print(f"  ✨ Creada Bolsa: {bolsa.title}")
        else:
            print(f"  ♻️  Bolsa existente: {bolsa.title}")

        return bolsa

    def _get_or_create_empresa(self, company_name, company_info, mercado, bolsa):
        """
        Crear o conseguir una Empresa
        """
        from appmodels.models import Empresa

        empresa, created = Empresa.objects.get_or_create(
            title=company_name,
            defaults={
                'description': f'Empresa cotizada en {bolsa.title} ({company_info["index"]})',
                'mercado': mercado,
                'public': True
            }
        )

        # Establecer relación con la bolsa (ManyToMany)
        if not empresa.bolsas.filter(id=bolsa.id).exists():
            empresa.bolsas.add(bolsa)
            print(f"  🔗 Asociada {empresa.title} con {bolsa.title}")

        if created:
            self.created_entities['empresas'] += 1
            print(f"  ✨ Creada Empresa: {empresa.title}")
        else:
            print(f"  ♻️  Empresa existente: {empresa.title}")

        return empresa

    def get_statistics(self):
        """
        Obtiene estadísticas de lo que se ha creado
        """
        return {
            'created': self.created_entities.copy(),
            'total_in_db': self._get_db_counts()
        }

    def _get_db_counts(self):
        """
        Cuenta total de entidades en la base de datos
        """
        from appmodels.models import Mercado, Bolsa, Empresa, Noticia

        return {
            'mercados': Mercado.objects.count(),
            'bolsas': Bolsa.objects.count(),
            'empresas': Empresa.objects.count(),
            'noticias': Noticia.objects.count()
        }


# Función de prueba
def test_entity_manager():
    """
    Prueba el gestor de entidades con empresas de ejemplo
    """
    print("=== PRUEBA DEL GESTOR DE ENTIDADES ===")

    manager = FinancialEntityManager()

    # Probar con empresas conocidas y desconocidas
    test_companies = [
        "Banco Santander",  # Conocida - Madrid
        "Apple",            # Conocida - NASDAQ
        "Tesla",            # Conocida - NASDAQ
        "Empresa Inventada" # Desconocida - por defecto Madrid
    ]

    for company in test_companies:
        try:
            empresa, info = manager.classify_and_create_entities(company)
            print(f"✅ {company} → {info['market']} / {info['exchange']}")
        except Exception as e:
            print(f"❌ Error con {company}: {e}")

    # Mostrar estadísticas finales
    stats = manager.get_statistics()
    print(f"\n📊 Estadísticas finales:")
    print(f"Creados en esta sesión: {stats['created']}")
    print(f"Total en BD: {stats['total_in_db']}")


if __name__ == "__main__":
    # Si ejecutamos este archivo directamente, hacer pruebas
    test_entity_manager()