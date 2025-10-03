from django.core.management.base import BaseCommand
from appmodels.models import Mercado, Bolsa, Empresa, Noticia


class Command(BaseCommand):
    help = 'Removes old test data that is not properly configured'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("LIMPIEZA DE DATOS DE PRUEBA ANTIGUOS")
        self.stdout.write("=" * 80)

        # 1. Delete old test Mercado
        self.stdout.write("\n1. Eliminando Mercados de prueba antiguos...")
        old_mercado = Mercado.objects.filter(title="The title of Surgical Area 1")
        if old_mercado.exists():
            # First get related objects count
            for mercado in old_mercado:
                bolsa_count = Bolsa.objects.filter(mercado=mercado).count()
                empresa_count = Empresa.objects.filter(mercado=mercado).count()
                self.stdout.write(f"  - Eliminando: {mercado.title}")
                self.stdout.write(f"    • {bolsa_count} bolsas relacionadas")
                self.stdout.write(f"    • {empresa_count} empresas relacionadas")

            # Delete (cascade will handle related objects)
            deleted_count = old_mercado.delete()[0]
            self.stdout.write(self.style.SUCCESS(f"  ✓ Eliminado {deleted_count} registros en total (con cascada)"))
        else:
            self.stdout.write("  - No se encontraron mercados antiguos")

        # 2. Delete orphaned test Bolsas (those not linked to current test markets)
        self.stdout.write("\n2. Eliminando Bolsas de prueba huérfanas...")
        valid_mercados = Mercado.objects.filter(title__in=["Mercado Europeo", "Mercado Americano"])
        orphaned_bolsas = Bolsa.objects.exclude(mercado__in=valid_mercados)

        if orphaned_bolsas.exists():
            for bolsa in orphaned_bolsas:
                self.stdout.write(f"  - Eliminando: {bolsa.title}")
            deleted_count = orphaned_bolsas.delete()[0]
            self.stdout.write(self.style.SUCCESS(f"  ✓ Eliminadas {deleted_count} bolsas huérfanas"))
        else:
            self.stdout.write("  - No se encontraron bolsas huérfanas")

        # 3. Delete test Empresa without proper relationships
        self.stdout.write("\n3. Eliminando Empresas de prueba mal configuradas...")

        # Delete "peripheral block 1"
        peripheral_block = Empresa.objects.filter(title="peripheral block 1")
        if peripheral_block.exists():
            self.stdout.write(f"  - Eliminando: peripheral block 1")
            peripheral_block.delete()
            self.stdout.write(self.style.SUCCESS("  ✓ Eliminado"))

        # Delete "empresa prueba"
        empresa_prueba = Empresa.objects.filter(title="empresa prueba")
        if empresa_prueba.exists():
            # First delete related noticias
            noticias_count = Noticia.objects.filter(empresa__in=empresa_prueba).count()
            if noticias_count > 0:
                Noticia.objects.filter(empresa__in=empresa_prueba).delete()
                self.stdout.write(f"  - Eliminando: empresa prueba (y {noticias_count} noticias relacionadas)")
            else:
                self.stdout.write(f"  - Eliminando: empresa prueba")
            empresa_prueba.delete()
            self.stdout.write(self.style.SUCCESS("  ✓ Eliminado"))

        # 4. Clean up any orphaned noticias (without empresa)
        self.stdout.write("\n4. Verificando noticias huérfanas...")
        orphaned_noticias = Noticia.objects.filter(empresa__isnull=True)
        if orphaned_noticias.exists():
            count = orphaned_noticias.count()
            orphaned_noticias.delete()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Eliminadas {count} noticias huérfanas"))
        else:
            self.stdout.write("  - No se encontraron noticias huérfanas")

        # 5. Final summary
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("RESUMEN FINAL:")
        self.stdout.write("-" * 40)

        # Count remaining valid test data
        mercados = Mercado.objects.all()
        bolsas = Bolsa.objects.all()
        empresas = Empresa.objects.all()
        noticias = Noticia.objects.all()

        self.stdout.write(f"Datos restantes en la base de datos:")
        self.stdout.write(f"  • Mercados: {mercados.count()}")
        for mercado in mercados:
            self.stdout.write(f"    - {mercado.title}")

        self.stdout.write(f"  • Bolsas: {bolsas.count()}")
        self.stdout.write(f"  • Empresas: {empresas.count()}")
        self.stdout.write(f"  • Noticias: {noticias.count()}")

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("LIMPIEZA COMPLETADA"))
        self.stdout.write("=" * 80)