import urllib.request
import urllib.parse
import re
import json
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def search_youtube_videos(query: str) -> str:
    """
    Search YouTube for videos related to the query and return them as a list of title/URL pairs.
    Use this tool whenever you need to find relevant YouTube videos for a topic.
    """
    logger.info("search_youtube_videos tool called with query: %s", query)
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # 1. Attempt to parse ytInitialData
            pattern = re.compile(r'var ytInitialData = ({.*?});')
            match = pattern.search(html)
            
            videos = []
            if match:
                try:
                    data = json.loads(match.group(1))
                    contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
                    for content in contents:
                        if 'itemSectionRenderer' in content:
                            items = content['itemSectionRenderer']['contents']
                            for item in items:
                                if 'videoRenderer' in item:
                                    video = item['videoRenderer']
                                    video_id = video.get('videoId')
                                    title_text = video.get('title', {}).get('runs', [{}])[0].get('text', 'No Title')
                                    if video_id:
                                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                                        videos.append((title_text, video_url))
                except Exception as e:
                    logger.warning("Failed to parse ytInitialData JSON structure: %s", e)
            
            # 2. Fallback to simple regex if JSON parsing yielded nothing
            if not videos:
                # Find watch IDs
                video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
                seen = set()
                deduped_ids = []
                for vid in video_ids:
                    if vid not in seen:
                        seen.add(vid)
                        deduped_ids.append(vid)
                for vid in deduped_ids[:10]:
                    videos.append((f"YouTube Video ({vid})", f"https://www.youtube.com/watch?v={vid}"))
            
            if not videos:
                return "No YouTube videos found."
                
            res_lines = []
            for idx, (title, link) in enumerate(videos[:10], 1):
                res_lines.append(f"{idx}. Title: {title} | URL: {link}")
            return "\n".join(res_lines)
            
    except Exception as e:
        logger.error("Error searching YouTube: %s", e)
        return f"Error occurred while searching YouTube: {str(e)}"
