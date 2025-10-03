from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.utils import timezone
from appmodels.models import Mercado, Bolsa, Empresa, Noticia
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Creates test data for markets, exchanges, companies and news'

    def handle(self, *args, **options):
        self.stdout.write("Creating test data...")

        # Get or create a superuser for created_by fields
        try:
            admin_user = CustomUser.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = CustomUser.objects.create_superuser(
                    username='admin_test',
                    email='admin@test.com',
                    password='admin123'
                )
                self.stdout.write(f"Created admin user: {admin_user.username}")
        except Exception as e:
            self.stdout.write(f"Error with admin user: {e}")
            admin_user = None

        # Create Mercados
        mercados_data = [
            {
                'title': 'Mercado Europeo',
                'description': 'Principales bolsas europeas incluyendo IBEX 35, DAX y más'
            },
            {
                'title': 'Mercado Americano',
                'description': 'Bolsas de Estados Unidos - NYSE y NASDAQ'
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
                self.stdout.write(self.style.SUCCESS(f"Created Mercado: {mercado.title}"))
            else:
                self.stdout.write(f"Mercado already exists: {mercado.title}")

        # Create Bolsas (2 per mercado)
        bolsas_data = [
            # European Market
            {
                'title': 'Bolsa de Madrid',
                'description': 'IBEX 35 - Principal índice bursátil de España',
                'mercado': mercados[0]
            },
            {
                'title': 'Bolsa de Frankfurt',
                'description': 'DAX - Índice bursátil alemán',
                'mercado': mercados[0]
            },
            # American Market
            {
                'title': 'NYSE',
                'description': 'New York Stock Exchange - La bolsa más grande del mundo',
                'mercado': mercados[1]
            },
            {
                'title': 'NASDAQ',
                'description': 'Bolsa especializada en empresas tecnológicas',
                'mercado': mercados[1]
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
                self.stdout.write(self.style.SUCCESS(f"Created Bolsa: {bolsa.title}"))
            else:
                self.stdout.write(f"Bolsa already exists: {bolsa.title}")

        # Create Empresas (2 per bolsa)
        empresas_data = [
            # Madrid
            {
                'title': 'Banco Santander',
                'description': 'Banco Santander es una entidad bancaria española con presencia global, líder en servicios financieros.',
                'mercado': mercados[0],
                'public': True,
                'bolsas': [bolsas[0]]
            },
            {
                'title': 'Telefónica',
                'description': 'Telefónica es una de las mayores compañías de telecomunicaciones del mundo con presencia en Europa y Latinoamérica.',
                'mercado': mercados[0],
                'public': True,
                'bolsas': [bolsas[0]]
            },
            # Frankfurt
            {
                'title': 'Volkswagen',
                'description': 'Volkswagen Group es uno de los fabricantes de automóviles más grandes del mundo, con marcas como VW, Audi, Porsche.',
                'mercado': mercados[0],
                'public': True,
                'bolsas': [bolsas[1]]
            },
            {
                'title': 'SAP',
                'description': 'SAP SE es una empresa multinacional alemana de software empresarial, líder en soluciones ERP.',
                'mercado': mercados[0],
                'public': True,
                'bolsas': [bolsas[1]]
            },
            # NYSE
            {
                'title': 'JPMorgan Chase',
                'description': 'JPMorgan Chase & Co. es una de las instituciones financieras más grandes de Estados Unidos con servicios bancarios globales.',
                'mercado': mercados[1],
                'public': True,
                'bolsas': [bolsas[2]]
            },
            {
                'title': 'Coca-Cola',
                'description': 'The Coca-Cola Company es una corporación multinacional de bebidas con presencia en más de 200 países.',
                'mercado': mercados[1],
                'public': True,
                'bolsas': [bolsas[2]]
            },
            # NASDAQ
            {
                'title': 'Apple',
                'description': 'Apple Inc. es una empresa tecnológica que diseña y desarrolla electrónica de consumo, software y servicios en línea.',
                'mercado': mercados[1],
                'public': True,
                'bolsas': [bolsas[3]]
            },
            {
                'title': 'Microsoft',
                'description': 'Microsoft Corporation es una empresa tecnológica que desarrolla software, servicios cloud y dispositivos.',
                'mercado': mercados[1],
                'public': True,
                'bolsas': [bolsas[3]]
            }
        ]

        empresas = []
        for empresa_data in empresas_data:
            bolsas_list = empresa_data.pop('bolsas')
            empresa, created = Empresa.objects.get_or_create(
                title=empresa_data['title'],
                defaults=empresa_data
            )

            # Add bolsas relationship
            for bolsa in bolsas_list:
                empresa.bolsas.add(bolsa)

            empresas.append(empresa)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Empresa: {empresa.title}"))
            else:
                self.stdout.write(f"Empresa already exists: {empresa.title}")

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
                    'source_url': f'https://example.com/news/{empresa.title.lower().replace(" ", "-")}-{i+1}',
                    'published_date': base_date - timedelta(days=i*7),
                    'is_premium': template['is_premium'],
                    'tags': template['tags'],
                    'public': True
                }

                noticia, created = Noticia.objects.get_or_create(
                    title=noticia_data['title'],
                    empresa=noticia_data['empresa'],
                    defaults=noticia_data
                )

                if created:
                    noticias_created += 1
                    self.stdout.write(self.style.SUCCESS(f"Created Noticia: {noticia.title[:50]}..."))
                else:
                    self.stdout.write(f"Noticia already exists: {noticia.title[:50]}...")

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("=== Summary ==="))
        self.stdout.write(f"Mercados: {Mercado.objects.count()}")
        self.stdout.write(f"Bolsas: {Bolsa.objects.count()}")
        self.stdout.write(f"Empresas: {Empresa.objects.count()}")
        self.stdout.write(f"Noticias: {Noticia.objects.count()}")
        self.stdout.write(f"New Noticias created: {noticias_created}")
        self.stdout.write(self.style.SUCCESS("\nTest data creation completed!"))