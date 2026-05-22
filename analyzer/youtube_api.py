import requests
from django.conf import settings


def get_youtube_videos(query, max_results=3):
    """
    Fetch YouTube videos for a search query.
    Returns list of video dicts: {title, url, thumbnail}
    Falls back to constructed YouTube search link if no API key.
    """
    api_key = getattr(settings, 'YOUTUBE_API_KEY', '')

    if not api_key:
        # Fallback: return YouTube search links without API
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return [{'title': f'Search YouTube: {query}', 'url': search_url, 'thumbnail': '', 'channel': 'YouTube'}]

    try:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': query,
            'maxResults': max_results,
            'type': 'video',
            'key': api_key,
        }
        response = requests.get(url, params=params, timeout=5)
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
        return videos
    except Exception:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return [{'title': f'Search YouTube: {query}', 'url': search_url, 'thumbnail': '', 'channel': 'YouTube'}]
