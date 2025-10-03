from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from appmodels.models import Noticia
from PIL import Image, ImageDraw, ImageFont
import io
import random


class Command(BaseCommand):
    help = 'Adds test images to all news articles'

    def create_test_image(self, title, company_name):
        """
        Creates a test image with gradient background and text
        """
        # Image dimensions
        width = 1200
        height = 675

        # Create image with gradient background
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        # Random gradient colors for variety
        gradients = [
            [(102, 126, 234), (118, 75, 162)],   # Purple gradient
            [(255, 94, 77), (255, 157, 77)],     # Orange gradient
            [(24, 90, 157), (67, 206, 162)],     # Blue-green gradient
            [(255, 81, 47), (221, 36, 118)],     # Red-pink gradient
            [(0, 176, 155), (150, 201, 61)],     # Teal-green gradient
            [(67, 67, 67), (0, 0, 0)],           # Dark gradient
        ]

        # Select random gradient
        color1, color2 = random.choice(gradients)

        # Create gradient
        for i in range(height):
            r = int(color1[0] * (1 - i/height) + color2[0] * (i/height))
            g = int(color1[1] * (1 - i/height) + color2[1] * (i/height))
            b = int(color1[2] * (1 - i/height) + color2[2] * (i/height))
            draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))

        # Add semi-transparent overlay for text readability
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
        image.paste(overlay, (0, 0), overlay)

        # Try to use a font, fallback to default if not available
        try:
            # Try to use a larger font size
            from PIL import ImageFont
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None

        # Add company name at the top
        draw.text((60, 60), company_name.upper(), fill=(255, 255, 255, 180), font=font_small)

        # Add title (word wrap for long titles)
        title_words = title.split()
        title_lines = []
        current_line = []

        for word in title_words:
            current_line.append(word)
            if len(' '.join(current_line)) > 40:
                if len(current_line) > 1:
                    current_line.pop()
                    title_lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    title_lines.append(' '.join(current_line))
                    current_line = []
        if current_line:
            title_lines.append(' '.join(current_line))

        # Draw title lines
        y_position = height // 2 - (len(title_lines) * 30)
        for line in title_lines[:3]:  # Max 3 lines
            draw.text((60, y_position), line, fill=(255, 255, 255), font=font_large)
            y_position += 60

        # Add "NEWS" watermark
        draw.text((width - 150, height - 60), "FINANCIAL NEWS", fill=(255, 255, 255, 100), font=font_small)

        # Add decorative elements
        # Top line
        draw.rectangle([(60, 120), (200, 122)], fill=(255, 255, 255, 150))
        # Bottom line
        draw.rectangle([(60, height - 120), (200, height - 118)], fill=(255, 255, 255, 150))

        # Convert to bytes
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format='JPEG', quality=85)
        img_byte_array.seek(0)

        return img_byte_array

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("ADDING TEST IMAGES TO NEWS ARTICLES")
        self.stdout.write("=" * 80)

        # Get all news without images
        noticias = Noticia.objects.all()
        total = noticias.count()
        updated = 0

        self.stdout.write(f"\nFound {total} news articles")

        for noticia in noticias:
            try:
                # Create test image
                image_data = self.create_test_image(
                    noticia.title[:100],  # Limit title length
                    noticia.empresa.title if noticia.empresa else "News"
                )

                # Save image to model
                image_name = f"test_news_{noticia.id}.jpg"
                noticia.image.save(
                    image_name,
                    ContentFile(image_data.read()),
                    save=True
                )

                updated += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Added image to: {noticia.title[:50]}..."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error with '{noticia.title[:30]}...': {str(e)}"))

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS(f"COMPLETED: {updated}/{total} news articles now have images"))
        self.stdout.write("=" * 80)