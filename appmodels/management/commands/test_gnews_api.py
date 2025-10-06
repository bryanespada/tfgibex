from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Test GNews API connection and data retrieval'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company',
            type=str,
            default='Banco Santander',
            help='Company name to search for (default: Banco Santander)'
        )
        parser.add_argument(
            '--show-full',
            action='store_true',
            help='Show full article content'
        )

    def handle(self, *args, **options):
        self.stdout.write("=== PRUEBA DE GNEWS API ===")

        company_name = options['company']
        show_full = options['show_full']

        # Verificar configuración
        self.check_configuration()

        # Realizar búsqueda
        self.search_company_news(company_name, show_full)

    def check_configuration(self):
        """Verificar que la configuración de GNews esté correcta"""
        self.stdout.write("\n🔧 Verificando configuración...")

        api_key = settings.GNEWS_API_KEY
        base_url = settings.GNEWS_CONFIG['base_url']

        self.stdout.write(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else f"API Key: {api_key}")
        self.stdout.write(f"Base URL: {base_url}")

        if api_key == 'demo_key_temporal':
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Usando demo key temporal. Para pruebas reales necesitas registrarte en: https://gnews.io/"
                )
            )

    def search_company_news(self, company_name, show_full=False):
        """Buscar noticias de una empresa específica"""
        self.stdout.write(f"\n🔍 Buscando noticias de: {company_name}")

        # Preparar parámetros de búsqueda
        params = self.build_search_params(company_name)

        self.stdout.write(f"Parámetros de búsqueda: {json.dumps(params, indent=2, ensure_ascii=False)}")

        try:
            # Realizar petición a GNews API
            response = requests.get(
                settings.GNEWS_CONFIG['base_url'],
                params=params,
                timeout=10
            )

            self.stdout.write(f"\n📡 Status Code: {response.status_code}")
            self.stdout.write(f"Headers: {dict(response.headers)}")

            if response.status_code == 200:
                self.process_successful_response(response.json(), show_full)
            elif response.status_code == 401:
                self.stdout.write(
                    self.style.ERROR("❌ Error 401: API Key inválida o expirada")
                )
                self.stdout.write("Necesitas registrarte en https://gnews.io/ para obtener una API key válida")
            elif response.status_code == 429:
                self.stdout.write(
                    self.style.ERROR("❌ Error 429: Rate limit excedido")
                )
                self.stdout.write("Has excedido el límite de requests. Espera un tiempo antes de probar de nuevo.")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error {response.status_code}: {response.text}")
                )

        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error de conexión: {e}")
            )

    def build_search_params(self, company_name):
        """Construir parámetros de búsqueda optimizados para noticias financieras"""

        # Calcular fecha desde (últimos 7 días)
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Construir query financiera
        financial_query = f'"{company_name}" AND (cotización OR resultados OR beneficios OR bolsa OR dividendo)'

        params = {
            'q': financial_query,
            'lang': settings.GNEWS_CONFIG['default_language'],
            'country': settings.GNEWS_CONFIG['default_country'],
            'max': settings.GNEWS_CONFIG['max_articles_per_request'],
            'from': from_date,
            'token': settings.GNEWS_API_KEY,
            'sortby': 'relevance'
        }

        return params

    def process_successful_response(self, data, show_full=False):
        """Procesar respuesta exitosa de GNews"""
        self.stdout.write(self.style.SUCCESS("\n✅ Respuesta exitosa de GNews API"))

        total_articles = data.get('totalArticles', 0)
        articles = data.get('articles', [])

        self.stdout.write(f"Total de artículos disponibles: {total_articles}")
        self.stdout.write(f"Artículos devueltos: {len(articles)}")

        if not articles:
            self.stdout.write(self.style.WARNING("⚠️  No se encontraron artículos"))
            return

        self.stdout.write(f"\n📰 Artículos encontrados:")

        for i, article in enumerate(articles, 1):
            self.display_article(i, article, show_full)

        # Análisis de calidad de los datos
        self.analyze_data_quality(articles)

    def display_article(self, index, article, show_full=False):
        """Mostrar información de un artículo"""
        self.stdout.write(f"\n--- Artículo {index} ---")
        self.stdout.write(f"📋 Título: {article.get('title', 'Sin título')}")
        self.stdout.write(f"📅 Fecha: {article.get('publishedAt', 'Sin fecha')}")
        self.stdout.write(f"🏢 Fuente: {article.get('source', {}).get('name', 'Sin fuente')}")
        self.stdout.write(f"🔗 URL: {article.get('url', 'Sin URL')}")

        description = article.get('description', 'Sin descripción')
        self.stdout.write(f"📝 Descripción: {description[:200]}{'...' if len(description) > 200 else ''}")

        if article.get('image'):
            self.stdout.write(f"🖼️  Imagen disponible: Sí")
        else:
            self.stdout.write(f"🖼️  Imagen disponible: No")

        if show_full and article.get('content'):
            content = article.get('content', 'Sin contenido')
            self.stdout.write(f"📄 Contenido completo: {content[:500]}{'...' if len(content) > 500 else ''}")

    def analyze_data_quality(self, articles):
        """Analizar la calidad de los datos recibidos"""
        self.stdout.write(f"\n📊 Análisis de calidad de datos:")

        # Contar artículos con diferentes campos
        with_title = sum(1 for a in articles if a.get('title'))
        with_description = sum(1 for a in articles if a.get('description'))
        with_content = sum(1 for a in articles if a.get('content'))
        with_image = sum(1 for a in articles if a.get('image'))
        with_source = sum(1 for a in articles if a.get('source', {}).get('name'))

        total = len(articles)

        self.stdout.write(f"  - Artículos con título: {with_title}/{total} ({with_title/total*100:.1f}%)")
        self.stdout.write(f"  - Artículos con descripción: {with_description}/{total} ({with_description/total*100:.1f}%)")
        self.stdout.write(f"  - Artículos con contenido: {with_content}/{total} ({with_content/total*100:.1f}%)")
        self.stdout.write(f"  - Artículos con imagen: {with_image}/{total} ({with_image/total*100:.1f}%)")
        self.stdout.write(f"  - Artículos con fuente: {with_source}/{total} ({with_source/total*100:.1f}%)")

        # Verificar relevancia financiera
        financial_keywords = ['cotización', 'bolsa', 'beneficios', 'resultados', 'dividendo', 'acciones']
        relevant_articles = 0

        for article in articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = title + ' ' + description

            if any(keyword in content for keyword in financial_keywords):
                relevant_articles += 1

        self.stdout.write(f"  - Artículos con contenido financiero: {relevant_articles}/{total} ({relevant_articles/total*100:.1f}%)")

        # Recomendaciones
        self.stdout.write(f"\n💡 Recomendaciones:")
        if relevant_articles < total * 0.5:
            self.stdout.write("  - Considera mejorar el query de búsqueda para obtener contenido más financiero")
        if with_image < total * 0.3:
            self.stdout.write("  - Pocas imágenes disponibles, considera fuentes alternativas para imágenes")
        if with_content < total * 0.1:
            self.stdout.write("  - GNews free tier no incluye contenido completo, solo título y descripción")