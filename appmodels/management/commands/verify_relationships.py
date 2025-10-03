from django.core.management.base import BaseCommand
from appmodels.models import Mercado, Bolsa, Empresa, Noticia
from django.db.models import Count


class Command(BaseCommand):
    help = 'Verifies the relationships between Mercado, Bolsa, Empresa and Noticia models'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("VERIFICACIÓN DE RELACIONES EN LA BASE DE DATOS"))
        self.stdout.write("=" * 80)

        # 1. Verify Mercados
        self.stdout.write("\n1. MERCADOS:")
        self.stdout.write("-" * 40)
        mercados = Mercado.objects.all()
        for mercado in mercados:
            bolsa_count = Bolsa.objects.filter(mercado=mercado).count()
            empresa_count = Empresa.objects.filter(mercado=mercado).count()
            self.stdout.write(self.style.SUCCESS(f"✓ {mercado.title}"))
            self.stdout.write(f"  - Bolsas asociadas: {bolsa_count}")
            self.stdout.write(f"  - Empresas asociadas: {empresa_count}")

        # 2. Verify Bolsas
        self.stdout.write("\n2. BOLSAS:")
        self.stdout.write("-" * 40)
        bolsas = Bolsa.objects.all()
        for bolsa in bolsas:
            empresa_count = bolsa.empresas.count()
            self.stdout.write(self.style.SUCCESS(f"✓ {bolsa.title}"))
            self.stdout.write(f"  - Mercado: {bolsa.mercado.title}")
            self.stdout.write(f"  - Empresas asociadas: {empresa_count}")
            if empresa_count > 0:
                empresas = bolsa.empresas.all()[:3]  # Show first 3
                for empresa in empresas:
                    self.stdout.write(f"    • {empresa.title}")

        # 3. Verify Empresas
        self.stdout.write("\n3. EMPRESAS:")
        self.stdout.write("-" * 40)
        empresas = Empresa.objects.all()
        for empresa in empresas:
            noticias_count = empresa.noticias.count()
            bolsas_list = empresa.bolsas.all()
            self.stdout.write(self.style.SUCCESS(f"✓ {empresa.title}"))
            self.stdout.write(f"  - Mercado: {empresa.mercado.title if empresa.mercado else 'No asignado'}")
            self.stdout.write(f"  - Bolsas: {', '.join([b.title for b in bolsas_list]) if bolsas_list else 'No asignada'}")
            self.stdout.write(f"  - Noticias asociadas: {noticias_count}")
            self.stdout.write(f"  - Pública: {'Sí' if empresa.public else 'No'}")

        # 4. Verify Noticias
        self.stdout.write("\n4. NOTICIAS:")
        self.stdout.write("-" * 40)
        noticias = Noticia.objects.all()
        total_noticias = noticias.count()
        premium_count = noticias.filter(is_premium=True).count()
        public_count = noticias.filter(public=True).count()

        self.stdout.write(f"Total de noticias: {total_noticias}")
        self.stdout.write(f"  - Públicas: {public_count}")
        self.stdout.write(f"  - Premium: {premium_count}")
        self.stdout.write(f"  - Gratuitas: {total_noticias - premium_count}")

        # Show distribution by company
        self.stdout.write("\nDistribución por empresa:")
        empresa_noticias = Noticia.objects.values('empresa__title').annotate(count=Count('id')).order_by('-count')
        for item in empresa_noticias[:5]:  # Show top 5
            self.stdout.write(f"  • {item['empresa__title']}: {item['count']} noticias")

        # 5. Data integrity check
        self.stdout.write("\n5. VERIFICACIÓN DE INTEGRIDAD:")
        self.stdout.write("-" * 40)

        # Check for orphaned records
        empresas_sin_mercado = Empresa.objects.filter(mercado__isnull=True).count()
        empresas_sin_bolsa = Empresa.objects.filter(bolsas__isnull=True).count()
        noticias_sin_empresa = Noticia.objects.filter(empresa__isnull=True).count()

        if empresas_sin_mercado == 0:
            self.stdout.write(self.style.SUCCESS("✅ Todas las empresas tienen mercado asignado"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  {empresas_sin_mercado} empresas sin mercado asignado"))

        if empresas_sin_bolsa == 0:
            self.stdout.write(self.style.SUCCESS("✅ Todas las empresas tienen al menos una bolsa asignada"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  {empresas_sin_bolsa} empresas sin bolsa asignada"))

        if noticias_sin_empresa == 0:
            self.stdout.write(self.style.SUCCESS("✅ Todas las noticias tienen empresa asignada"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  {noticias_sin_empresa} noticias sin empresa asignada"))

        # Check ManyToMany relationships
        self.stdout.write("\n6. RELACIONES MANY-TO-MANY (Empresa-Bolsa):")
        self.stdout.write("-" * 40)
        for empresa in Empresa.objects.all()[:5]:  # Show first 5
            bolsas = empresa.bolsas.all()
            if bolsas.exists():
                self.stdout.write(self.style.SUCCESS(f"✓ {empresa.title} está en: {', '.join([b.title for b in bolsas])}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  {empresa.title} no está asociada a ninguna bolsa"))

        # 7. Check consistency between Empresa.mercado and Bolsa.mercado
        self.stdout.write("\n7. CONSISTENCIA MERCADO (Empresa-Bolsa):")
        self.stdout.write("-" * 40)
        inconsistent = False
        for empresa in Empresa.objects.all():
            if empresa.mercado:
                for bolsa in empresa.bolsas.all():
                    if bolsa.mercado != empresa.mercado:
                        self.stdout.write(self.style.ERROR(
                            f"❌ INCONSISTENCIA: {empresa.title} está en mercado {empresa.mercado.title} "
                            f"pero está listada en bolsa {bolsa.title} del mercado {bolsa.mercado.title}"
                        ))
                        inconsistent = True

        if not inconsistent:
            self.stdout.write(self.style.SUCCESS("✅ Todas las empresas están en bolsas del mismo mercado"))

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("VERIFICACIÓN COMPLETADA"))
        self.stdout.write("=" * 80)