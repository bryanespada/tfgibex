from django.core.management.base import BaseCommand
from appmodels.utils.entity_manager import FinancialEntityManager
from appmodels.models import Noticia
from django.utils import timezone
import hashlib


class Command(BaseCommand):
    help = 'Test complete news flow with simulated GNews data'

    def handle(self, *args, **options):
        self.stdout.write("=== PRUEBA DE FLUJO COMPLETO CON DATOS SIMULADOS ===")

        # Datos simulados como si vinieran de GNews API
        simulated_gnews_response = {
            "totalArticles": 3,
            "articles": [
                {
                    "title": "Banco Santander reporta beneficios récord en el tercer trimestre",
                    "description": "El banco español Banco Santander ha anunciado beneficios récord de 2.500 millones de euros en el tercer trimestre, superando las expectativas de los analistas.",
                    "content": "El Banco Santander ha presentado hoy sus resultados del tercer trimestre...",
                    "url": "https://ejemplo.com/santander-resultados-q3",
                    "image": "https://ejemplo.com/santander-image.jpg",
                    "publishedAt": "2024-10-06T08:30:00Z",
                    "source": {
                        "name": "Financial Times España",
                        "url": "https://ejemplo.com"
                    }
                },
                {
                    "title": "Apple presenta nuevos iPhone con tecnología avanzada",
                    "description": "Apple Inc. ha unveilado su nueva línea de iPhone con chips más potentes y mejoras significativas en la cámara.",
                    "content": "Durante el evento especial de Apple...",
                    "url": "https://ejemplo.com/apple-new-iphone",
                    "image": "https://ejemplo.com/apple-image.jpg",
                    "publishedAt": "2024-10-06T10:00:00Z",
                    "source": {
                        "name": "TechCrunch",
                        "url": "https://techcrunch.com"
                    }
                },
                {
                    "title": "Tesla supera expectativas de ventas en Europa",
                    "description": "Tesla Motors ha reportado un aumento del 25% en las ventas europeas durante el último trimestre, impulsado por la demanda del Model 3.",
                    "content": "Las ventas de Tesla en Europa han mostrado un crecimiento robusto...",
                    "url": "https://ejemplo.com/tesla-ventas-europa",
                    "image": "https://ejemplo.com/tesla-image.jpg",
                    "publishedAt": "2024-10-06T12:15:00Z",
                    "source": {
                        "name": "Reuters",
                        "url": "https://reuters.com"
                    }
                }
            ]
        }

        # Procesar artículos simulados
        self.process_simulated_articles(simulated_gnews_response['articles'])

    def process_simulated_articles(self, articles):
        """Procesar artículos simulados como si vinieran de GNews"""

        entity_manager = FinancialEntityManager()
        total_saved = 0

        self.stdout.write(f"\n🧪 Procesando {len(articles)} artículos simulados...")

        for i, article in enumerate(articles, 1):
            self.stdout.write(f"\n--- Procesando artículo {i}/{len(articles)} ---")

            # Extraer nombre de empresa del título
            company_name = self.extract_company_name(article['title'])

            if company_name:
                try:
                    # 1. Clasificar y crear entidades automáticamente
                    empresa, info = entity_manager.classify_and_create_entities(company_name)

                    self.stdout.write(f"🏢 Empresa: {empresa.title}")
                    self.stdout.write(f"📊 Mercado: {info['market']}")
                    self.stdout.write(f"🏛️  Bolsa: {info['exchange']}")

                    # 2. Crear noticia
                    if self.save_article(article, empresa):
                        total_saved += 1
                        self.stdout.write(self.style.SUCCESS("✅ Noticia guardada"))
                    else:
                        self.stdout.write(self.style.WARNING("⚠️  Noticia duplicada o error"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  No se pudo extraer nombre de empresa"))

        # Mostrar resumen final
        self.show_final_summary(total_saved, entity_manager)

    def extract_company_name(self, title):
        """Extraer nombre de empresa del título de la noticia"""

        # Lista de empresas conocidas que podríamos encontrar en títulos
        known_companies = {
            'santander': 'Banco Santander',
            'banco santander': 'Banco Santander',
            'apple': 'Apple',
            'tesla': 'Tesla',
            'microsoft': 'Microsoft',
            'google': 'Google',
            'telefonica': 'Telefónica',
            'telefónica': 'Telefónica',
            'bbva': 'BBVA',
            'iberdrola': 'Iberdrola'
        }

        title_lower = title.lower()

        for key, company_name in known_companies.items():
            if key in title_lower:
                self.stdout.write(f"🔍 Detectada empresa: {company_name}")
                return company_name

        return None

    def save_article(self, article_data, empresa):
        """Guardar artículo con detección de duplicados"""

        # Generar ID único basado en URL
        article_url = article_data.get('url', '')
        api_id = hashlib.md5(article_url.encode()).hexdigest()

        # Verificar si ya existe
        if Noticia.objects.filter(api_id=api_id).exists():
            return False

        try:
            noticia = Noticia.objects.create(
                title=article_data.get('title', '')[:500],
                summary=article_data.get('description', '')[:1000],
                content=article_data.get('content', ''),
                published_date=self.parse_date(article_data.get('publishedAt')),
                source=article_data.get('source', {}).get('name', '')[:200],
                source_url=article_url,
                empresa=empresa,
                api_id=api_id,
                api_source='gnews_simulado',
                public=True,
                is_premium=False
            )

            self.stdout.write(f"📝 Título: {noticia.title[:50]}...")
            return True

        except Exception as e:
            self.stdout.write(f"❌ Error guardando: {e}")
            return False

    def parse_date(self, date_string):
        """Parsear fecha de GNews"""
        if not date_string:
            return timezone.now()

        try:
            from datetime import datetime
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except:
            return timezone.now()

    def show_final_summary(self, total_saved, entity_manager):
        """Mostrar resumen final del procesamiento"""

        self.stdout.write(f"\n📊 RESUMEN FINAL:")
        self.stdout.write(f"✅ Noticias guardadas: {total_saved}")

        # Estadísticas del entity manager
        stats = entity_manager.get_statistics()
        self.stdout.write(f"\nEntidades creadas:")
        for entity_type, count in stats['created'].items():
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  - {entity_type}: {count}"))

        self.stdout.write(f"\nTotal en base de datos:")
        for entity_type, count in stats['total_in_db'].items():
            self.stdout.write(f"  - {entity_type}: {count}")

        # Mostrar jerarquía actualizada
        self.show_updated_hierarchy()

    def show_updated_hierarchy(self):
        """Mostrar jerarquía actualizada después del procesamiento"""
        from appmodels.models import Mercado, Bolsa, Empresa, Noticia

        self.stdout.write(f"\n🌳 Jerarquía actualizada:")

        for mercado in Mercado.objects.all():
            self.stdout.write(f"\n📈 {mercado.title}")

            for bolsa in Bolsa.objects.filter(mercado=mercado):
                self.stdout.write(f"  └── 🏢 {bolsa.title}")

                for empresa in Empresa.objects.filter(mercado=mercado, bolsas=bolsa):
                    noticias_count = Noticia.objects.filter(empresa=empresa).count()
                    recent_news = Noticia.objects.filter(empresa=empresa).order_by('-created_at')[:1]

                    if recent_news:
                        last_news_date = recent_news[0].created_at.strftime('%Y-%m-%d %H:%M')
                        self.stdout.write(f"      └── 🏭 {empresa.title} ({noticias_count} noticias, última: {last_news_date})")
                    else:
                        self.stdout.write(f"      └── 🏭 {empresa.title} ({noticias_count} noticias)")