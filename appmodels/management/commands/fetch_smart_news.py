from django.core.management.base import BaseCommand
from django.conf import settings
from appmodels.utils.entity_manager import FinancialEntityManager
from appmodels.utils.smart_company_detector import SmartCompanyDetector
from appmodels.utils.market_classifier import get_companies_by_market
from appmodels.models import Noticia
import requests
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone
import time


class Command(BaseCommand):
    help = 'Fetch financial news with smart company detection (improved version)'

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
            help='Maximum companies to process (default: 5)'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='How many days back to search (default: 7)'
        )
        parser.add_argument(
            '--general-search',
            action='store_true',
            help='Use general financial search instead of company-specific searches'
        )

    def handle(self, *args, **options):
        self.stdout.write("=== FETCH SMART NEWS (IMPROVED DETECTION) ===")

        # Verificar configuración
        if not self.check_configuration():
            return

        # Inicializar componentes
        self.entity_manager = FinancialEntityManager()
        self.company_detector = SmartCompanyDetector()

        # Obtener parámetros
        market = options['market']
        max_companies = options['max_companies']
        days_back = options['days_back']
        general_search = options['general_search']

        if general_search:
            # Búsqueda general de noticias financieras
            total_news = self.fetch_general_financial_news(market, days_back, max_companies * 2)
        else:
            # Búsqueda específica por empresa (método original mejorado)
            total_news = self.fetch_company_specific_news(market, max_companies, days_back)

        # Mostrar resumen final
        self.show_final_summary(total_news)

    def check_configuration(self):
        """Verificar configuración"""
        api_key = settings.GNEWS_API_KEY
        if not api_key or api_key == 'demo_key_temporal':
            self.stdout.write(self.style.ERROR("❌ API Key no configurada"))
            return False
        return True

    def fetch_general_financial_news(self, market, days_back, max_articles):
        """
        Búsqueda general de noticias financieras sin empresa específica

        Esta es la nueva funcionalidad que resuelve el problema:
        1. Busca noticias financieras generales
        2. Usa el detector inteligente para identificar las empresas
        3. Asocia correctamente cada noticia a su empresa principal
        """
        self.stdout.write(f"\n🔍 Búsqueda general de noticias financieras ({market})...")

        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Queries generales por mercado (más amplias para mejor cobertura)
        if market == 'european' or market == 'all':
            eu_query = 'bolsa OR acciones OR empresas OR mercado OR dividendo'
            eu_articles = self._search_gnews(eu_query, from_date, max_articles // 2)
            self.stdout.write(f"📰 Noticias europeas encontradas: {len(eu_articles)}")
        else:
            eu_articles = []

        if market == 'american' or market == 'all':
            us_query = 'stock OR market OR shares OR earnings OR business'
            us_articles = self._search_gnews(us_query, from_date, max_articles // 2, lang='en')
            self.stdout.write(f"📰 Noticias americanas encontradas: {len(us_articles)}")
        else:
            us_articles = []

        all_articles = eu_articles + us_articles
        self.stdout.write(f"📰 Total de artículos para procesar: {len(all_articles)}")

        # Procesar cada artículo con detección inteligente
        return self.process_articles_with_smart_detection(all_articles)

    def fetch_company_specific_news(self, market, max_companies, days_back):
        """Método original mejorado con detección inteligente"""
        companies = self.get_companies_to_process(market, max_companies)
        self.stdout.write(f"\n🏢 Procesando {len(companies)} empresas específicas...")

        total_news_saved = 0
        for i, company in enumerate(companies, 1):
            self.stdout.write(f"\n--- Procesando {i}/{len(companies)}: {company} ---")
            news_saved = self.fetch_and_process_company_news(company, days_back)
            total_news_saved += news_saved

            if i < len(companies):
                time.sleep(3)  # Rate limiting

        return total_news_saved

    def _search_gnews(self, query, from_date, max_articles, lang='es', country='es'):
        """Realizar búsqueda en GNews"""
        params = {
            'q': query,
            'lang': lang,
            'country': country,
            'max': max_articles,
            'from': from_date,
            'token': settings.GNEWS_API_KEY,
            'sortby': 'relevance'
        }

        try:
            response = requests.get(settings.GNEWS_CONFIG['base_url'], params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                self.stdout.write(f"⚠️  Error {response.status_code} en búsqueda")
                return []
        except Exception as e:
            self.stdout.write(f"❌ Error de conexión: {e}")
            return []

    def process_articles_with_smart_detection(self, articles):
        """
        Procesar artículos usando detección inteligente de empresas

        Esta es la función clave que resuelve el problema:
        """
        total_saved = 0

        for i, article in enumerate(articles, 1):
            self.stdout.write(f"\n--- Artículo {i}/{len(articles)} ---")

            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')

            self.stdout.write(f"📋 Título: {title[:60]}...")

            # 🧠 DETECCIÓN INTELIGENTE DE EMPRESA
            detected_company = self.company_detector.detect_main_company(title, description, content)
            company_name, confidence_score, analysis = detected_company

            if company_name and confidence_score > 8:  # Score mínimo de confianza
                self.stdout.write(f"🎯 Empresa detectada: {company_name} (score: {confidence_score})")

                try:
                    # Crear estructura de mercado/bolsa/empresa
                    empresa, info = self.entity_manager.classify_and_create_entities(company_name)

                    self.stdout.write(f"🏢 {empresa.title} → {info['exchange']} ({info['market']})")

                    # Guardar artículo
                    if self.save_article(article, empresa):
                        total_saved += 1
                        self.stdout.write("✅ Guardado exitosamente")
                    else:
                        self.stdout.write("⚪ Duplicado o error al guardar")

                except Exception as e:
                    self.stdout.write(f"❌ Error procesando {company_name}: {e}")

            else:
                self.stdout.write("⚪ No se detectó empresa relevante o score muy bajo")
                if analysis and isinstance(analysis, dict):
                    companies_found = analysis.get('all_companies_found', [])
                    if companies_found:
                        top_companies = companies_found[:3]  # Top 3
                        companies_str = ', '.join([f"{name}({data['score']})" for name, data in top_companies])
                        self.stdout.write(f"   Encontradas: {companies_str}")
                elif analysis:
                    self.stdout.write(f"   Mensaje: {analysis}")

            # Rate limiting entre artículos
            if i < len(articles):
                time.sleep(1)

        return total_saved

    def fetch_and_process_company_news(self, company_name, days_back):
        """Versión mejorada del fetch por empresa específica"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')

        financial_query = f'"{company_name}" AND (cotización OR resultados OR beneficios OR bolsa OR dividendo OR earnings)'

        params = {
            'q': financial_query,
            'lang': 'es',
            'country': 'es',
            'max': 5,
            'from': from_date,
            'token': settings.GNEWS_API_KEY,
            'sortby': 'relevance'
        }

        try:
            response = requests.get(settings.GNEWS_CONFIG['base_url'], params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])

                if articles:
                    # Usar detección inteligente en lugar de asumir la empresa
                    return self.process_articles_with_smart_detection(articles)
                else:
                    self.stdout.write("⚪ No se encontraron noticias")
                    return 0
            else:
                self.stdout.write(f"❌ Error {response.status_code}")
                return 0

        except Exception as e:
            self.stdout.write(f"❌ Error de conexión: {e}")
            return 0

    def get_companies_to_process(self, market, max_companies):
        """Obtener lista de empresas a procesar"""
        if market == 'all':
            european_companies = get_companies_by_market('european')
            american_companies = get_companies_by_market('american')
            all_companies = european_companies + american_companies
        else:
            all_companies = get_companies_by_market(market)

        import random
        if len(all_companies) > max_companies:
            companies = random.sample(all_companies, max_companies)
        else:
            companies = all_companies

        return companies

    def save_article(self, article_data, empresa):
        """Guardar artículo con detección de duplicados"""
        article_url = article_data.get('url', '')
        api_id = hashlib.md5(article_url.encode()).hexdigest()

        if Noticia.objects.filter(api_id=api_id).exists():
            return False

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
                api_source='gnews_smart',
                public=True,
                is_premium=False
            )
            return True
        except Exception as e:
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

    def show_final_summary(self, total_news_saved):
        """Mostrar resumen final"""
        self.stdout.write(f"\n📊 RESUMEN FINAL:")
        self.stdout.write(self.style.SUCCESS(f"✅ Total noticias guardadas: {total_news_saved}"))

        stats = self.entity_manager.get_statistics()
        self.stdout.write(f"\nEntidades creadas:")
        for entity_type, count in stats['created'].items():
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  - {entity_type}: {count}"))

        self.stdout.write(f"\nTotal en base de datos:")
        for entity_type, count in stats['total_in_db'].items():
            self.stdout.write(f"  - {entity_type}: {count}")

        # Mostrar noticias más recientes
        recent_news = Noticia.objects.filter(
            api_source='gnews_smart'
        ).order_by('-created_at')[:5]

        if recent_news:
            self.stdout.write(f"\n📰 Últimas noticias agregadas:")
            for noticia in recent_news:
                self.stdout.write(f"  • {noticia.title[:60]}... ({noticia.empresa.title})")
        else:
            self.stdout.write(f"\n📰 No se agregaron noticias nuevas")