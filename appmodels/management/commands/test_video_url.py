from django.core.management.base import BaseCommand
from appmodels.models import Noticia
from appmodels.templatetags.video_filters import get_embed_url

class Command(BaseCommand):
    help = 'Test video URL conversion for news'

    def handle(self, *args, **kwargs):
        # Get news with video links
        noticias = Noticia.objects.filter(video_link__isnull=False).exclude(video_link='')

        if not noticias:
            self.stdout.write(self.style.WARNING('No news with video links found'))
            return

        for noticia in noticias:
            self.stdout.write(f"\n{self.style.SUCCESS(f'News ID {noticia.id}:')} {noticia.title}")
            self.stdout.write(f"  Original URL: {noticia.video_link}")
            embed_url = get_embed_url(noticia.video_link)
            self.stdout.write(f"  Embed URL: {embed_url}")

            if embed_url == noticia.video_link:
                self.stdout.write(self.style.WARNING("  ⚠ URL was not converted (might already be embed format or unsupported)"))
            else:
                self.stdout.write(self.style.SUCCESS("  ✓ URL converted successfully"))