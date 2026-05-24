import requests
from django.conf import settings
from django.core.cache import cache


def get_youtube_videos(query, max_results=3):
    """
    Fetch YouTube videos for a search query.
    Results are cached for 6 hours to prevent a live HTTP request on every page load.
    Falls back to a constructed YouTube search link if no API key is configured.
    """
    cache_key = f'youtube_{query.lower().replace(" ", "_")}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_key = getattr(settings, 'YOUTUBE_API_KEY', '')

    if not api_key:
        # No API key — return a direct YouTube search link instantly
        result = [{
            'title': f'Search YouTube: {query}',
            'url': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            'thumbnail': '',
            'channel': 'YouTube',
        }]
        cache.set(cache_key, result, 60 * 60 * 6)
        return result

    try:
        params = {
            'part': 'snippet',
            'q': query,
            'maxResults': max_results,
            'type': 'video',
            'key': api_key,
        }
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/search',
            params=params,
            timeout=5,
        )
        data = response.json()

        videos = []
        for item in data.get('items', []):
            vid_id = item['id']['videoId']
            snippet = item['snippet']
            videos.append({
                'title': snippet.get('title', ''),
                'url': f'https://www.youtube.com/watch?v={vid_id}',
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'channel': snippet.get('channelTitle', ''),
            })

        cache.set(cache_key, videos, 60 * 60 * 6)  # cache 6 hours
        return videos

    except Exception:
        result = [{
            'title': f'Search YouTube: {query}',
            'url': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            'thumbnail': '',
            'channel': 'YouTube',
        }]
        cache.set(cache_key, result, 60 * 60 * 1)  # cache 1 hour on error
        return result
