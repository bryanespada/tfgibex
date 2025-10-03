from django import template
import re
from urllib.parse import urlparse, parse_qs

register = template.Library()

@register.filter
def get_embed_url(video_url):
    """
    Convert video URLs to their embed versions for iframe usage.
    Supports YouTube, Vimeo, and other platforms.
    """
    if not video_url:
        return ''

    # Clean the URL
    video_url = video_url.strip()

    # YouTube regular URL: https://www.youtube.com/watch?v=VIDEO_ID
    if 'youtube.com/watch' in video_url:
        try:
            parsed_url = urlparse(video_url)
            video_id = parse_qs(parsed_url.query).get('v', [None])[0]
            if video_id:
                # Add rel=0 to prevent showing related videos from other channels
                return f'https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1'
        except:
            pass

    # YouTube short URL: https://youtu.be/VIDEO_ID
    youtube_short = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', video_url)
    if youtube_short:
        video_id = youtube_short.group(1)
        return f'https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1'

    # YouTube already embed URL - add parameters if missing
    if 'youtube.com/embed/' in video_url:
        if '?' not in video_url:
            return f'{video_url}?rel=0&modestbranding=1'
        return video_url

    # YouTube mobile URL: https://m.youtube.com/watch?v=VIDEO_ID
    if 'm.youtube.com/watch' in video_url:
        try:
            parsed_url = urlparse(video_url)
            video_id = parse_qs(parsed_url.query).get('v', [None])[0]
            if video_id:
                return f'https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1'
        except:
            pass

    # Vimeo regular URL: https://vimeo.com/VIDEO_ID
    vimeo_match = re.search(r'vimeo\.com/([0-9]+)', video_url)
    if vimeo_match:
        video_id = vimeo_match.group(1)
        return f'https://player.vimeo.com/video/{video_id}'

    # Vimeo already player URL
    if 'player.vimeo.com' in video_url:
        return video_url

    # Return original URL if no conversion needed
    return video_url