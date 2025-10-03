from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from appmodels.models import Empresa, Image
from PIL import Image as PILImage, ImageDraw, ImageFont
import io


class Command(BaseCommand):
    help = 'Adds test image to Telefónica empresa'

    def create_test_image(self, empresa_name):
        """
        Creates a test corporate image for the empresa
        """
        # Image dimensions
        width = 800
        height = 600

        # Create image with gradient background
        image = PILImage.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        # Blue corporate gradient for Telefónica
        color1 = (0, 102, 164)  # Telefónica blue
        color2 = (0, 176, 240)  # Light blue

        # Create gradient
        for i in range(height):
            r = int(color1[0] * (1 - i/height) + color2[0] * (i/height))
            g = int(color1[1] * (1 - i/height) + color2[1] * (i/height))
            b = int(color1[2] * (1 - i/height) + color2[2] * (i/height))
            draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))

        # Add overlay for text
        overlay = PILImage.new('RGBA', (width, height), (255, 255, 255, 30))
        image.paste(overlay, (0, 0), overlay)

        # Try to use font
        try:
            from PIL import ImageFont
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None

        # Add company name
        draw.text((width//2 - 100, height//2 - 50), empresa_name, fill=(255, 255, 255), font=font_large)
        draw.text((width//2 - 100, height//2 + 20), "Corporate Headquarters", fill=(255, 255, 255, 200), font=font_small)
        draw.text((width//2 - 100, height//2 + 50), "Madrid, Spain", fill=(255, 255, 255, 180), font=font_small)

        # Add decorative elements
        # Circle decoration
        draw.ellipse([(50, 50), (150, 150)], outline=(255, 255, 255, 100), width=3)
        draw.ellipse([(width-150, height-150), (width-50, height-50)], outline=(255, 255, 255, 100), width=3)

        # Lines
        draw.rectangle([(50, height//2), (200, height//2 + 2)], fill=(255, 255, 255, 150))
        draw.rectangle([(width-200, height//2), (width-50, height//2 + 2)], fill=(255, 255, 255, 150))

        # Convert to bytes
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format='JPEG', quality=90)
        img_byte_array.seek(0)

        return img_byte_array

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("ADDING TEST IMAGE TO TELEFÓNICA")
        self.stdout.write("=" * 80)

        try:
            # Find Telefónica empresa
            empresa = Empresa.objects.get(title='Telefónica')
            self.stdout.write(f"Found empresa: {empresa.title}")

            # Check if already has images
            existing_images = empresa.images.count()
            self.stdout.write(f"Existing images: {existing_images}")

            # Create test image
            image_data = self.create_test_image('TELEFÓNICA')

            # Create Image object
            image_obj = Image(
                title='Sede Central Telefónica',
                description='Imagen de la sede central de Telefónica en Madrid, España. El edificio emblemático representa la presencia global de la compañía en el sector de telecomunicaciones.',
                empresa=empresa
            )

            # Save image file
            image_name = f"telefonica_headquarters.jpg"
            image_obj.image.save(
                image_name,
                ContentFile(image_data.read()),
                save=True
            )

            self.stdout.write(self.style.SUCCESS(f"✓ Image created and saved: {image_obj.title}"))
            self.stdout.write(f"  - File: {image_obj.image.name}")
            self.stdout.write(f"  - Description: {image_obj.description[:50]}...")

            # Add a second image
            self.stdout.write("\nCreating second image...")

            image_data2 = self.create_test_image('TELEFÓNICA TECH')

            image_obj2 = Image(
                title='Centro de Innovación',
                description='Centro de innovación y desarrollo tecnológico de Telefónica, donde se desarrollan las últimas tecnologías en telecomunicaciones y servicios digitales.',
                empresa=empresa
            )

            image_obj2.image.save(
                f"telefonica_innovation.jpg",
                ContentFile(image_data2.read()),
                save=True
            )

            self.stdout.write(self.style.SUCCESS(f"✓ Second image created: {image_obj2.title}"))

            # Final count
            total_images = empresa.images.count()
            self.stdout.write(f"\nTotal images for Telefónica: {total_images}")

        except Empresa.DoesNotExist:
            self.stdout.write(self.style.ERROR("✗ Telefónica empresa not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {str(e)}"))

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("PROCESS COMPLETED"))
        self.stdout.write("=" * 80)