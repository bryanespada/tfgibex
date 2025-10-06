from django.core.management.base import BaseCommand
from appmodels.utils.entity_manager import FinancialEntityManager
from appmodels.models import Mercado, Bolsa, Empresa, Noticia


class Command(BaseCommand):
    help = 'Test the FinancialEntityManager system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all entities before testing',
        )

    def handle(self, *args, **options):
        self.stdout.write("=== PRUEBA DEL GESTOR DE ENTIDADES ===")

        # Mostrar estado inicial
        self.show_initial_state()

        if options['reset']:
            self.reset_entities()

        # Crear el gestor
        manager = FinancialEntityManager()

        # Probar con empresas conocidas y desconocidas
        test_companies = [
            "Banco Santander",  # Conocida - Madrid
            "Apple",            # Conocida - NASDAQ
            "Volkswagen",       # Conocida - Frankfurt
            "Empresa Inventada" # Desconocida - por defecto Madrid
        ]

        self.stdout.write(f"\n🧪 Probando con {len(test_companies)} empresas...")

        for i, company in enumerate(test_companies, 1):
            self.stdout.write(f"\n--- Prueba {i}/{len(test_companies)} ---")
            try:
                empresa, info = manager.classify_and_create_entities(company)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ ÉXITO: {company}")
                )
                self.stdout.write(f"   → Mercado: {info['market']}")
                self.stdout.write(f"   → Bolsa: {info['exchange']}")
                self.stdout.write(f"   → Empresa ID: {empresa.id}")
                self.stdout.write(f"   → Encontrada en BD: {'Sí' if info['found_in_db'] else 'No'}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ ERROR con {company}: {e}")
                )
                import traceback
                traceback.print_exc()

        # Mostrar estadísticas finales
        self.show_final_statistics(manager)

    def show_initial_state(self):
        """Muestra el estado inicial de la base de datos"""
        self.stdout.write("\n📊 Estado inicial de la base de datos:")
        self.stdout.write(f"  - Mercados: {Mercado.objects.count()}")
        self.stdout.write(f"  - Bolsas: {Bolsa.objects.count()}")
        self.stdout.write(f"  - Empresas: {Empresa.objects.count()}")
        self.stdout.write(f"  - Noticias: {Noticia.objects.count()}")

    def reset_entities(self):
        """Resetea todas las entidades (solo para testing)"""
        self.stdout.write(self.style.WARNING("\n🗑️  Reseteando entidades..."))

        # Eliminar en orden para respetar foreign keys
        Noticia.objects.all().delete()
        Empresa.objects.all().delete()
        Bolsa.objects.all().delete()
        Mercado.objects.all().delete()

        self.stdout.write("✅ Entidades eliminadas")

    def show_final_statistics(self, manager):
        """Muestra estadísticas finales"""
        self.stdout.write(f"\n📊 Estadísticas finales:")
        stats = manager.get_statistics()

        self.stdout.write("Entidades creadas en esta sesión:")
        for entity_type, count in stats['created'].items():
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"  - {entity_type}: {count}"))
            else:
                self.stdout.write(f"  - {entity_type}: {count}")

        self.stdout.write("\nTotal en base de datos:")
        for entity_type, count in stats['total_in_db'].items():
            self.stdout.write(f"  - {entity_type}: {count}")

        # Mostrar jerarquía creada
        self.show_hierarchy()

    def show_hierarchy(self):
        """Muestra la jerarquía de mercados, bolsas y empresas"""
        self.stdout.write(f"\n🌳 Jerarquía creada:")

        for mercado in Mercado.objects.all():
            self.stdout.write(f"\n📈 {mercado.title}")

            for bolsa in Bolsa.objects.filter(mercado=mercado):
                self.stdout.write(f"  └── 🏢 {bolsa.title}")

                for empresa in Empresa.objects.filter(mercado=mercado, bolsas=bolsa):
                    noticias_count = Noticia.objects.filter(empresa=empresa).count()
                    self.stdout.write(f"      └── 🏭 {empresa.title} ({noticias_count} noticias)")