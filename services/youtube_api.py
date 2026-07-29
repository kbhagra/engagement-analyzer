from __future__ import annotations

import os
import re
from datetime import datetime, timezone

import requests

API_BASE = "https://www.googleapis.com/youtube/v3"
MAX_VIDEOS = 20


class YouTubeAPIError(RuntimeError):
    pass


def fetch_channel_videos(kind: str, identifier: str, max_videos: int = MAX_VIDEOS) -> list[dict]:
    key = _api_key()
    channel = _resolve_channel(kind, identifier, key)
    video_ids = _recent_video_ids(channel["uploads_playlist"], key, max_videos)
    if not video_ids:
        raise YouTubeAPIError("This channel has no public videos to analyze.")
    return [_video_row(channel, video) for video in _video_details(video_ids, key)]


def _api_key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise YouTubeAPIError(
            "Set the YOUTUBE_API_KEY environment variable to analyze a channel."
        )
    return key


def _get(endpoint: str, params: dict) -> dict:
    response = requests.get(f"{API_BASE}/{endpoint}", params=params, timeout=15)
    if response.status_code != 200:
        raise YouTubeAPIError(
            "The YouTube API request failed. Check your API key and quota."
        )
    return response.json()


def _resolve_channel(kind: str, identifier: str, key: str) -> dict:
    params = {"part": "snippet,statistics,contentDetails", "key": key}
    params["forHandle" if kind == "handle" else "id"] = identifier

    items = _get("channels", params).get("items", [])
    if not items:
        raise YouTubeAPIError("No channel found for that link.")

    channel = items[0]
    return {
        "id": channel["id"],
        "name": channel["snippet"]["title"],
        "thumbnail": channel["snippet"]["thumbnails"]["default"]["url"],
        "subscribers": channel["statistics"].get("subscriberCount"),
        "uploads_playlist": channel["contentDetails"]["relatedPlaylists"]["uploads"],
    }


def _recent_video_ids(playlist_id: str, key: str, max_videos: int) -> list[str]:
    data = _get(
        "playlistItems",
        {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": max_videos,
            "key": key,
        },
    )
    return [item["contentDetails"]["videoId"] for item in data.get("items", [])]


def _video_details(video_ids: list[str], key: str) -> list[dict]:
    data = _get(
        "videos",
        {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(video_ids),
            "key": key,
        },
    )
    return data.get("items", [])


def _video_row(channel: dict, video: dict) -> dict:
    snippet = video["snippet"]
    stats = video["statistics"]
    title = snippet["title"]
    published_at = snippet["publishedAt"]
    duration = video["contentDetails"]["duration"]

    return {
        "channel_id": channel["id"],
        "channel_name": channel["name"],
        "channel_subscriber_count": channel["subscribers"],
        "channel_thumbnail_url": channel["thumbnail"],
        "video_id": video["id"],
        "video_url": f"https://www.youtube.com/watch?v={video['id']}",
        "title": title,
        "title_length": len(title),
        "description": snippet.get("description", ""),
        "published_at": published_at,
        "video_age_days": _age_days(published_at),
        "duration": duration,
        "duration_seconds": _duration_seconds(duration),
        "view_count": stats.get("viewCount"),
        "like_count": stats.get("likeCount"),
        "comment_count": stats.get("commentCount"),
        "thumbnail_url": snippet["thumbnails"]["high"]["url"],
    }


def _age_days(published_at: str) -> int:
    published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - published).days


def _duration_seconds(duration: str) -> int:
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return 0
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds
