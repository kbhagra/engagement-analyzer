from __future__ import annotations

from pathlib import Path

import pandas as pd

from analysis.metrics import DATA_PATH

COLUMNS = [
    "channel_id",
    "channel_name",
    "channel_subscriber_count",
    "channel_thumbnail_url",
    "video_id",
    "video_url",
    "title",
    "title_length",
    "description",
    "published_at",
    "video_age_days",
    "duration",
    "duration_seconds",
    "view_count",
    "like_count",
    "comment_count",
    "thumbnail_url",
]


def save_videos(rows: list[dict], path: Path = DATA_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=COLUMNS).to_csv(path, index=False)
    return path
