from django.core.management.base import BaseCommand
from django.conf import settings
from appmodels.utils.entity_manager import FinancialEntityManager
from appmodels.utils.market_classifier import COMPANY_TO_MARKET, get_companies_by_market
from appmodels.models import Noticia
import requests
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone
import time


class Command(BaseCommand):
    help = 'Fetch real financial news from GNews API and create complete market structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--market',
            choices=['european', 'american', 'all'],
            default='european',
            help='Which market to fetch news for (default: european)'
        )
        parser.add_argument(
            '--max-companies',
            type=int,
            default=5,
            help='Maximum companies to process (default: 5 for testing)'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='How many days back to search (default: 7)'
        )

    def handle(self, *args, **options):
        self.stdout.write("=== FETCH REAL NEWS FROM GNEWS ===")

        # Verificar configuración
        if not self.check_configuration():
            return

        # Obtener parámetros
        market = options['market']
        max_companies = options['max_companies']
        days_back = options['days_back']

        # Inicializar entity manager
        self.entity_manager = FinancialEntityManager()

        # Obtener lista de empresas a procesar
        companies = self.get_companies_to_process(market, max_companies)

        self.stdout.write(f"\n🏢 Procesando {len(companies)} empresas del mercado {market}...")

        # Procesar cada empresa
        total_news_saved = 0
        for i, company in enumerate(companies, 1):
            self.stdout.write(f"\n--- Procesando {i}/{len(companies)}: {company} ---")

            news_saved = self.fetch_company_news(company, days_back)
            total_news_saved += news_saved

            # Rate limiting - pausa entre requests para no exceder límites
            if i < len(companies):
                self.stdout.write("⏳ Esperando 3 segundos...")
                time.sleep(3)

        # Mostrar resumen final
        self.show_final_summary(total_news_saved)

    def check_configuration(self):
        """Verificar que la configuración esté correcta"""
        api_key = settings.GNEWS_API_KEY

        if not api_key or api_key == 'demo_key_temporal':
            self.stdout.write(
                self.style.ERROR("❌ API Key de GNews no configurada correctamente")
            )
            return False

        self.stdout.write(f"✅ API Key configurada: {api_key[:10]}...")
        return True

    def get_companies_to_process(self, market, max_companies):
        """Obtener lista de empresas a procesar"""
        if market == 'all':
            european_companies = get_companies_by_market('european')
            american_companies = get_companies_by_market('american')
            all_companies = european_companies + american_companies
        else:
            all_companies = get_companies_by_market(market)

        # Limitar número y mezclar para variedad
        import random
        if len(all_companies) > max_companies:
            companies = random.sample(all_companies, max_companies)
        else:
            companies = all_companies

        return companies

    def fetch_company_news(self, company_name, days_back):
        """Buscar noticias de una empresa específica"""

        # Construir query de búsqueda
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Query optimizada para noticias financieras
        financial_query = f'"{company_name}" AND (cotización OR resultados OR beneficios OR bolsa OR dividendo OR acciones OR earnings)'

        params = {
            'q': financial_query,
            'lang': 'es',
            'country': 'es',
            'max': 5,  # Máximo 5 artículos por empresa
            'from': from_date,
            'token': settings.GNEWS_API_KEY,
            'sortby': 'relevance'
        }

        try:
            self.stdout.write(f"🔍 Buscando: {financial_query[:60]}...")

            response = requests.get(
                settings.GNEWS_CONFIG['base_url'],
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])

                self.stdout.write(f"📰 Encontrados {len(articles)} artículos")

                if articles:
                    return self.process_articles(articles, company_name)
                else:
                    self.stdout.write("⚪ No se encontraron noticias")
                    return 0

            elif response.status_code == 429:
                self.stdout.write(
                    self.style.WARNING("⚠️  Rate limit alcanzado, esperando...")
                )
                time.sleep(60)  # Esperar 1 minuto
                return 0

            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error {response.status_code}: {response.text}")
                )
                return 0

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error de conexión: {e}")
            )
            return 0

    def process_articles(self, articles, company_name):
        """Procesar artículos de una empresa"""

        # 1. Clasificar empresa y crear estructura si es necesaria
        try:
            empresa, info = self.entity_manager.classify_and_create_entities(company_name)

            self.stdout.write(f"🏢 {empresa.title} → {info['exchange']} ({info['market']})")

            if info.get('found_in_db'):
                self.stdout.write("✅ Empresa conocida")
            else:
                self.stdout.write("🆕 Empresa nueva clasificada automáticamente")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error clasificando empresa {company_name}: {e}")
            )
            return 0

        # 2. Procesar cada artículo
        saved_count = 0
        for i, article in enumerate(articles, 1):
            self.stdout.write(f"  📄 Artículo {i}: {article.get('title', 'Sin título')[:50]}...")

            if self.save_article(article, empresa):
                saved_count += 1
                self.stdout.write("    ✅ Guardado")
            else:
                self.stdout.write("    ⚪ Duplicado o error")

        return saved_count

    def save_article(self, article_data, empresa):
        """Guardar artículo con detección de duplicados"""

        # Generar ID único
        article_url = article_data.get('url', '')
        api_id = hashlib.md5(article_url.encode()).hexdigest()

        # Verificar duplicados
        if Noticia.objects.filter(api_id=api_id).exists():
            return False

        # Verificar similitud de títulos
        title = article_data.get('title', '')
        if self.is_duplicate_title(title, empresa):
            return False

        try:
            noticia = Noticia.objects.create(
                title=title[:500],
                summary=article_data.get('description', '')[:1000],
                content=article_data.get('content', ''),
                published_date=self.parse_date(article_data.get('publishedAt')),
                source=article_data.get('source', {}).get('name', '')[:200],
                source_url=article_url,
                empresa=empresa,
                api_id=api_id,
                api_source='gnews',
                public=True,
                is_premium=False
            )

            # Intentar descargar imagen
            self.download_image(noticia, article_data.get('image'))

            return True

        except Exception as e:
            self.stdout.write(f"    ❌ Error guardando: {e}")
            return False

    def is_duplicate_title(self, title, empresa, similarity_threshold=0.8):
        """Verificar duplicados por similitud de título"""
        from difflib import SequenceMatcher

        recent_titles = Noticia.objects.filter(
            empresa=empresa,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values_list('title', flat=True)

        for existing_title in recent_titles:
            similarity = SequenceMatcher(None, title.lower(), existing_title.lower()).ratio()
            if similarity > similarity_threshold:
                return True
        return False

    def parse_date(self, date_string):
        """Parsear fecha de GNews"""
        if not date_string:
            return timezone.now()

        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except:
            return timezone.now()

    def download_image(self, noticia, image_url):
        """Descargar imagen del artículo"""
        if not image_url:
            return

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            from django.core.files.base import ContentFile
            import uuid

            ext = image_url.split('.')[-1][:3]
            filename = f"{uuid.uuid4().hex}.{ext}"

            noticia.image.save(
                filename,
                ContentFile(response.content),
                save=True
            )

        except Exception as e:
            self.stdout.write(f"    ⚠️  Error descargando imagen: {e}")

    def show_final_summary(self, total_news_saved):
        """Mostrar resumen final"""
        self.stdout.write(f"\n📊 RESUMEN FINAL:")
        self.stdout.write(self.style.SUCCESS(f"✅ Total noticias guardadas: {total_news_saved}"))

        # Estadísticas del entity manager
        stats = self.entity_manager.get_statistics()

        self.stdout.write(f"\nEntidades creadas:")
        for entity_type, count in stats['created'].items():
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  - {entity_type}: {count}"))

        self.stdout.write(f"\nTotal en base de datos:")
        for entity_type, count in stats['total_in_db'].items():
            self.stdout.write(f"  - {entity_type}: {count}")

        # Mostrar noticias más recientes
        self.show_recent_news()

    def show_recent_news(self):
        """Mostrar las noticias más recientes creadas"""
        recent_news = Noticia.objects.filter(
            api_source='gnews'
        ).order_by('-created_at')[:5]

        if recent_news:
            self.stdout.write(f"\n📰 Últimas noticias agregadas:")
            for noticia in recent_news:
                self.stdout.write(f"  • {noticia.title[:60]}... ({noticia.empresa.title})")
        else:
            self.stdout.write(f"\n📰 No se agregaron noticias nuevas en esta ejecución")