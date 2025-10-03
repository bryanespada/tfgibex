import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tfgibex.settings')
django.setup()

from appmodels.models import Mercado, Bolsa, Empresa, Noticia
from users.models import CustomUser

print("Creating test data...")

# Get or create a superuser for created_by fields
try:
    admin_user = CustomUser.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = CustomUser.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='admin123'
        )
        print(f"Created admin user: {admin_user.username}")
except Exception as e:
    print(f"Error with admin user: {e}")
    admin_user = None

# Create Mercados
mercados_data = [
    {
        'title': 'Mercado Europeo',
        'icon': 'fa-euro-sign',
        'subtitle': 'Principales bolsas europeas',
        'public': True,
        'created_by': admin_user
    },
    {
        'title': 'Mercado Americano',
        'icon': 'fa-dollar-sign',
        'subtitle': 'Bolsas de Estados Unidos',
        'public': True,
        'created_by': admin_user
    }
]

mercados = []
for mercado_data in mercados_data:
    mercado, created = Mercado.objects.get_or_create(
        title=mercado_data['title'],
        defaults=mercado_data
    )
    mercados.append(mercado)
    if created:
        print(f"Created Mercado: {mercado.title}")
    else:
        print(f"Mercado already exists: {mercado.title}")

# Create Bolsas (2 per mercado)
bolsas_data = [
    # European Market
    {
        'title': 'Bolsa de Madrid',
        'icon': 'fa-chart-line',
        'subtitle': 'IBEX 35',
        'mercado': mercados[0],
        'public': True,
        'created_by': admin_user
    },
    {
        'title': 'Bolsa de Frankfurt',
        'icon': 'fa-chart-area',
        'subtitle': 'DAX',
        'mercado': mercados[0],
        'public': True,
        'created_by': admin_user
    },
    # American Market
    {
        'title': 'NYSE',
        'icon': 'fa-building',
        'subtitle': 'New York Stock Exchange',
        'mercado': mercados[1],
        'public': True,
        'created_by': admin_user
    },
    {
        'title': 'NASDAQ',
        'icon': 'fa-microchip',
        'subtitle': 'Technology Companies',
        'mercado': mercados[1],
        'public': True,
        'created_by': admin_user
    }
]

bolsas = []
for bolsa_data in bolsas_data:
    bolsa, created = Bolsa.objects.get_or_create(
        title=bolsa_data['title'],
        mercado=bolsa_data['mercado'],
        defaults=bolsa_data
    )
    bolsas.append(bolsa)
    if created:
        print(f"Created Bolsa: {bolsa.title}")
    else:
        print(f"Bolsa already exists: {bolsa.title}")

# Create Empresas (2 per bolsa)
empresas_data = [
    # Madrid
    {
        'title': 'Banco Santander',
        'ticker': 'SAN',
        'subtitle': 'Servicios financieros',
        'description': 'Banco Santander es una entidad bancaria española con presencia global.',
        'mercado': mercados[0],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[0]]
    },
    {
        'title': 'Telefónica',
        'ticker': 'TEF',
        'subtitle': 'Telecomunicaciones',
        'description': 'Telefónica es una de las mayores compañías de telecomunicaciones del mundo.',
        'mercado': mercados[0],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[0]]
    },
    # Frankfurt
    {
        'title': 'Volkswagen',
        'ticker': 'VOW3',
        'subtitle': 'Automoción',
        'description': 'Volkswagen Group es uno de los fabricantes de automóviles más grandes del mundo.',
        'mercado': mercados[0],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[1]]
    },
    {
        'title': 'SAP',
        'ticker': 'SAP',
        'subtitle': 'Software empresarial',
        'description': 'SAP SE es una empresa multinacional alemana de software.',
        'mercado': mercados[0],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[1]]
    },
    # NYSE
    {
        'title': 'JPMorgan Chase',
        'ticker': 'JPM',
        'subtitle': 'Servicios financieros',
        'description': 'JPMorgan Chase & Co. es una de las instituciones financieras más grandes de Estados Unidos.',
        'mercado': mercados[1],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[2]]
    },
    {
        'title': 'Coca-Cola',
        'ticker': 'KO',
        'subtitle': 'Bebidas',
        'description': 'The Coca-Cola Company es una corporación multinacional de bebidas.',
        'mercado': mercados[1],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[2]]
    },
    # NASDAQ
    {
        'title': 'Apple',
        'ticker': 'AAPL',
        'subtitle': 'Tecnología',
        'description': 'Apple Inc. es una empresa tecnológica que diseña y desarrolla electrónica de consumo.',
        'mercado': mercados[1],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[3]]
    },
    {
        'title': 'Microsoft',
        'ticker': 'MSFT',
        'subtitle': 'Software y servicios',
        'description': 'Microsoft Corporation es una empresa tecnológica que desarrolla software y servicios.',
        'mercado': mercados[1],
        'public': True,
        'created_by': admin_user,
        'bolsas': [bolsas[3]]
    }
]

empresas = []
for empresa_data in empresas_data:
    bolsas_list = empresa_data.pop('bolsas')
    empresa, created = Empresa.objects.get_or_create(
        title=empresa_data['title'],
        ticker=empresa_data['ticker'],
        defaults=empresa_data
    )

    # Add bolsas relationship
    for bolsa in bolsas_list:
        empresa.bolsas.add(bolsa)

    empresas.append(empresa)
    if created:
        print(f"Created Empresa: {empresa.title}")
    else:
        print(f"Empresa already exists: {empresa.title}")

# Create Noticias (3 per empresa)
base_date = timezone.now()

news_templates = [
    {
        'title_template': '{company} reporta resultados del Q4 2024',
        'summary_template': '{company} ha publicado sus resultados financieros del último trimestre de 2024.',
        'content_template': 'La compañía {company} ha anunciado hoy sus resultados correspondientes al cuarto trimestre de 2024, mostrando un crecimiento significativo en sus principales líneas de negocio. Los ingresos totales alcanzaron nuevos máximos históricos, superando las expectativas de los analistas.',
        'is_premium': False,
        'tags': 'resultados,financiero,trimestral'
    },
    {
        'title_template': '{company} anuncia nueva estrategia de expansión',
        'summary_template': 'La empresa {company} presenta su plan estratégico para los próximos años.',
        'content_template': '{company} ha presentado su nuevo plan estratégico que incluye la expansión hacia nuevos mercados emergentes. La compañía planea invertir significativamente en investigación y desarrollo, así como en la adquisición de empresas complementarias para fortalecer su posición en el mercado.',
        'is_premium': True,
        'tags': 'estrategia,expansión,inversión'
    },
    {
        'title_template': 'Análisis técnico de {company}: perspectivas para 2025',
        'summary_template': 'Análisis detallado del comportamiento bursátil de {company} y proyecciones.',
        'content_template': 'El análisis técnico de las acciones de {company} muestra señales positivas para el año 2025. Los indicadores técnicos sugieren una tendencia alcista sostenida, con niveles de soporte bien definidos. Los expertos recomiendan mantener posiciones a largo plazo.',
        'is_premium': True,
        'tags': 'análisis,técnico,proyección,inversión'
    }
]

noticias_created = 0
for empresa in empresas:
    for i, template in enumerate(news_templates):
        noticia_data = {
            'title': template['title_template'].format(company=empresa.title),
            'summary': template['summary_template'].format(company=empresa.title),
            'content': template['content_template'].format(company=empresa.title),
            'empresa': empresa,
            'author': 'Redacción Financiera',
            'source': 'Financial News Network',
            'source_url': f'https://example.com/news/{empresa.ticker.lower()}-{i+1}',
            'published_date': base_date - timedelta(days=i*7),
            'is_premium': template['is_premium'],
            'tags': template['tags'],
            'public': True,
            'created_by': admin_user
        }

        noticia, created = Noticia.objects.get_or_create(
            title=noticia_data['title'],
            empresa=noticia_data['empresa'],
            defaults=noticia_data
        )

        if created:
            noticias_created += 1
            print(f"Created Noticia: {noticia.title[:50]}...")
        else:
            print(f"Noticia already exists: {noticia.title[:50]}...")

print(f"\n=== Summary ===")
print(f"Mercados: {Mercado.objects.count()}")
print(f"Bolsas: {Bolsa.objects.count()}")
print(f"Empresas: {Empresa.objects.count()}")
print(f"Noticias: {Noticia.objects.count()}")
print(f"New Noticias created: {noticias_created}")
print("\nTest data creation completed!")