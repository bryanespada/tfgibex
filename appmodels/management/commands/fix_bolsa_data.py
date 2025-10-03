from django.core.management.base import BaseCommand
from appmodels.models import Bolsa


class Command(BaseCommand):
    help = 'Fixes bolsa titles and descriptions to use index names as titles'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("FIXING BOLSA DATA")
        self.stdout.write("=" * 80)

        # Define the corrections
        corrections = [
            {
                'old_title': 'Bolsa de Madrid',
                'new_title': 'IBEX 35',
                'new_description': 'Bolsa de Madrid - Principal índice bursátil de España'
            },
            {
                'old_title': 'Bolsa de Frankfurt',
                'new_title': 'DAX',
                'new_description': 'Bolsa de Frankfurt - Principal índice bursátil de Alemania'
            },
            {
                'old_title': 'NYSE',
                'new_title': 'NYSE',
                'new_description': 'New York Stock Exchange - La bolsa de valores más grande del mundo'
            },
            {
                'old_title': 'NASDAQ',
                'new_title': 'NASDAQ',
                'new_description': 'National Association of Securities Dealers Automated Quotations - Bolsa electrónica especializada en empresas tecnológicas'
            }
        ]

        for correction in corrections:
            try:
                bolsa = Bolsa.objects.get(title=correction['old_title'])
                old_title = bolsa.title
                old_description = bolsa.description

                bolsa.title = correction['new_title']
                bolsa.description = correction['new_description']
                bolsa.save()

                self.stdout.write(self.style.SUCCESS(
                    f"✓ Updated: '{old_title}' → '{correction['new_title']}'"
                ))
                self.stdout.write(f"  Description: {correction['new_description'][:50]}...")

            except Bolsa.DoesNotExist:
                # Try with the new title in case it was already updated
                try:
                    bolsa = Bolsa.objects.get(title=correction['new_title'])
                    bolsa.description = correction['new_description']
                    bolsa.save()
                    self.stdout.write(self.style.WARNING(
                        f"⚠ Already had correct title: '{correction['new_title']}', updated description only"
                    ))
                except Bolsa.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f"✗ Not found: '{correction['old_title']}' or '{correction['new_title']}'"
                    ))

        # Display final results
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("FINAL BOLSA LIST:")
        self.stdout.write("-" * 40)

        for bolsa in Bolsa.objects.all():
            self.stdout.write(f"• {bolsa.title}: {bolsa.description[:60]}...")

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("BOLSA DATA FIX COMPLETED"))
        self.stdout.write("=" * 80)