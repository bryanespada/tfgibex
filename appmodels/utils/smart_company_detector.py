"""
Detector Inteligente de Empresas en Noticias
===========================================

Este módulo mejora la detección de qué empresa es realmente la protagonista
de una noticia, no solo si aparece mencionada.
"""

from .market_classifier import COMPANY_TO_MARKET, find_company_info
import re


class SmartCompanyDetector:
    """
    Detector inteligente que analiza el contenido completo para identificar
    la empresa principal de una noticia
    """

    def __init__(self):
        # Crear mapeos para búsqueda eficiente
        self.company_patterns = self._build_company_patterns()

    def _build_company_patterns(self):
        """
        Construir patrones de búsqueda para todas las empresas conocidas
        Incluye variaciones y nombres alternativos
        """
        patterns = {}

        # Empresas con nombres alternativos comunes
        company_variations = {
            'Apple': ['Apple', 'Apple Inc', 'AAPL'],
            'Microsoft': ['Microsoft', 'Microsoft Corp', 'MSFT'],
            'Google': ['Google', 'Alphabet', 'Alphabet Inc', 'GOOGL', 'GOOG'],
            'Amazon': ['Amazon', 'Amazon.com', 'AMZN'],
            'Tesla': ['Tesla', 'Tesla Inc', 'Tesla Motors', 'TSLA'],
            'NVIDIA': ['NVIDIA', 'Nvidia', 'NVDA'],
            'Meta': ['Meta', 'Facebook', 'Meta Platforms', 'META'],
            'Netflix': ['Netflix', 'NFLX'],
            'Banco Santander': ['Banco Santander', 'Santander', 'SAN'],
            'BBVA': ['BBVA', 'Banco Bilbao Vizcaya Argentaria'],
            'Telefónica': ['Telefónica', 'Telefonica', 'TEF'],
            'CaixaBank': ['CaixaBank', 'Caixa Bank', 'La Caixa'],
            'Volkswagen': ['Volkswagen', 'VW', 'VOW'],
            'SAP': ['SAP', 'SAP SE'],
            'Iberdrola': ['Iberdrola', 'IBE'],
            'Repsol': ['Repsol', 'REP']
        }

        # Para cada empresa conocida en nuestra base de datos
        for company_key in COMPANY_TO_MARKET.keys():
            # Nombre principal (título)
            main_name = company_key.title()

            # Obtener variaciones si existen
            variations = company_variations.get(main_name, [main_name])

            # Crear patrones regex para cada variación
            company_patterns = []
            for variation in variations:
                # Patrón que busca la palabra completa (no parte de otra palabra)
                pattern = r'\b' + re.escape(variation) + r'\b'
                company_patterns.append(pattern)

            patterns[main_name] = {
                'patterns': company_patterns,
                'variations': variations,
                'original_key': company_key
            }

        return patterns

    def detect_main_company(self, title, description, content=""):
        """
        Detectar la empresa principal de una noticia

        Args:
            title (str): Título de la noticia
            description (str): Descripción/summary
            content (str): Contenido completo (opcional)

        Returns:
            tuple: (empresa_detectada, score_confidence, analysis)
        """

        # Combinar todo el texto para análisis
        full_text = f"{title} {description} {content}".lower()

        # Buscar todas las empresas mencionadas con sus scores
        company_scores = {}

        for company_name, company_data in self.company_patterns.items():
            score = self._calculate_company_score(
                full_text, title.lower(), description.lower(),
                company_data['patterns'], company_data['variations']
            )

            if score > 0:
                company_scores[company_name] = {
                    'score': score,
                    'original_key': company_data['original_key'],
                    'variations_found': self._find_variations_in_text(
                        full_text, company_data['variations']
                    )
                }

        # Determinar empresa principal
        if not company_scores:
            return None, 0, "No se encontraron empresas conocidas"

        # Ordenar por score
        sorted_companies = sorted(
            company_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )

        main_company = sorted_companies[0]
        company_name = main_company[0]
        score_data = main_company[1]

        analysis = {
            'all_companies_found': sorted_companies,
            'main_company': company_name,
            'confidence_score': score_data['score'],
            'variations_found': score_data['variations_found']
        }

        return company_name, score_data['score'], analysis

    def _calculate_company_score(self, full_text, title, description, patterns, variations):
        """
        Calcular score de relevancia de una empresa en la noticia

        Criterios de scoring:
        - Aparición en título: +10 puntos
        - Aparición en descripción: +5 puntos
        - Aparición en contenido: +2 puntos
        - Múltiples menciones: +1 punto por mención adicional
        - Aparición al inicio del título: +5 puntos bonus
        """
        score = 0

        for pattern in patterns:
            # Buscar en título (mayor peso)
            title_matches = len(re.findall(pattern, title, re.IGNORECASE))
            if title_matches > 0:
                score += 10 * title_matches

                # Bonus si aparece al inicio del título
                if re.match(pattern, title, re.IGNORECASE):
                    score += 5

            # Buscar en descripción
            desc_matches = len(re.findall(pattern, description, re.IGNORECASE))
            if desc_matches > 0:
                score += 5 * desc_matches

            # Buscar en contenido completo
            content_matches = len(re.findall(pattern, full_text, re.IGNORECASE))
            if content_matches > 0:
                score += 2 * content_matches

        return score

    def _find_variations_in_text(self, text, variations):
        """Encontrar qué variaciones del nombre aparecen en el texto"""
        found_variations = []

        for variation in variations:
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_variations.append(variation)

        return found_variations


# Función de utilidad para usar fácilmente
def detect_article_company(title, description, content=""):
    """
    Función de conveniencia para detectar la empresa principal de un artículo

    Returns:
        str or None: Nombre de la empresa detectada
    """
    detector = SmartCompanyDetector()
    company_name, score, analysis = detector.detect_main_company(title, description, content)

    return company_name if score > 5 else None  # Requiere score mínimo


# Función de prueba
def test_smart_detector():
    """Función de prueba para el detector inteligente"""
    print("=== PRUEBA DEL DETECTOR INTELIGENTE ===")

    test_cases = [
        {
            'title': 'Nvidia, primera compañía en llegar a 4,5 billones de dólares en Bolsa',
            'description': 'La compañía de chips de IA sube un 40,79% en el año. Amplía la ventaja sobre Microsoft, Apple y Alphabet',
            'expected': 'NVIDIA'
        },
        {
            'title': 'Banco Santander eleva un 15% el dividendo',
            'description': 'La entidad presidida por Ana Botín abonará 11,5 céntimos por acción',
            'expected': 'Banco Santander'
        },
        {
            'title': 'Apple presenta nuevos iPhone con tecnología avanzada',
            'description': 'Apple Inc. ha unveilado su nueva línea de iPhone con chips más potentes',
            'expected': 'Apple'
        },
        {
            'title': 'Tesla supera expectativas de ventas en Europa',
            'description': 'Tesla Motors ha reportado un aumento del 25% en las ventas europeas',
            'expected': 'Tesla'
        }
    ]

    detector = SmartCompanyDetector()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Prueba {i} ---")
        print(f"Título: {test_case['title']}")
        print(f"Descripción: {test_case['description']}")
        print(f"Empresa esperada: {test_case['expected']}")

        company, score, analysis = detector.detect_main_company(
            test_case['title'],
            test_case['description']
        )

        print(f"Empresa detectada: {company}")
        print(f"Score de confianza: {score}")

        if company == test_case['expected']:
            print("✅ CORRECTO")
        else:
            print("❌ INCORRECTO")
            print(f"Análisis: {analysis}")


if __name__ == "__main__":
    test_smart_detector()