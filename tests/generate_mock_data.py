"""Generate a realistic mock videos.csv for developing the results dashboard.

Run from the project root:
    python tests/generate_mock_data.py

This lets Partner 2 (analysis/dashboard) work before Partner 1's
YouTube API pipeline is finished. Column names match the agreed schema.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)  # reproducible mock data

CHANNEL_ID = "UCmockchannel0001"
CHANNEL_NAME = "Nike"
SUBSCRIBERS = 2_140_000

TITLES = [
    "Just Do It: Behind the Campaign",
    "Air Max Day 2026 Recap",
    "How Pros Train | Episode 4",
    "Unboxing the New Pegasus 42",
    "5 Drills to Improve Your Sprint Speed",
    "Marathon Prep: Week 1",
    "The Story of the Waffle Sole",
    "Athlete Spotlight: Rising Stars",
    "Trail Running Essentials",
    "Design Lab: Making a Jersey",
    "Game Day Routine",
    "Recovery Tips from the Pros",
    "Sneaker Culture: A Short Documentary About the History and Future of Basketball Shoes",
    "Behind the Scenes: World Cup Kit Launch",
    "Yoga for Runners",
    "Speed vs Endurance: What Matters More?",
    "City Runs: Tokyo",
    "The Perfect Warm Up",
    "Ask a Coach: Your Questions Answered",
    "Season Highlights 2025",
]

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "videos.csv"

FIELDNAMES = [
    "channel_id", "channel_name", "channel_subscriber_count",
    "video_id", "video_url", "title", "title_length", "description",
    "published_at", "video_age_days", "duration", "duration_seconds",
    "view_count", "like_count", "comment_count",
    "thumbnail_url",
]
# Note: derived columns (engagement rate, views_per_day, etc.) are
# intentionally NOT in the CSV — analysis/metrics.py computes them.


def iso_duration(seconds: int) -> str:
    """Format seconds as a YouTube-style ISO 8601 duration, e.g. PT4M13S."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    out = "PT"
    if h:
        out += f"{h}H"
    if m:
        out += f"{m}M"
    if s or (not h and not m):
        out += f"{s}S"
    return out


def make_rows(n: int = 20) -> list[dict]:
    rows = []
    now = datetime(2026, 7, 23)
    for i, title in enumerate(TITLES[:n]):
        age_days = random.randint(3, 400)
        published = now - timedelta(days=age_days,
                                    hours=random.randint(0, 23))
        views = random.randint(8_000, 3_500_000)
        like_rate = random.uniform(0.01, 0.06)
        comment_rate = random.uniform(0.0005, 0.004)
        likes = int(views * like_rate)
        comments = int(views * comment_rate)
        dur = random.randint(35, 1500)
        vid = f"mockvid{i:04d}"

        row = {
            "channel_id": CHANNEL_ID,
            "channel_name": CHANNEL_NAME,
            "channel_subscriber_count": SUBSCRIBERS,
            "video_id": vid,
            "video_url": f"https://www.youtube.com/watch?v={vid}",
            "title": title,
            "title_length": len(title),
            "description": f"Mock description for '{title}'.",
            "published_at": published.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "video_age_days": age_days,
            "duration": iso_duration(dur),
            "duration_seconds": dur,
            "view_count": views,
            "like_count": likes,
            "comment_count": comments,
            "thumbnail_url": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
        }
        rows.append(row)

    # Edge cases the real API produces — the dashboard must handle these:
    rows[4]["like_count"] = ""       # likes hidden by uploader -> missing
    rows[7]["comment_count"] = ""    # comments disabled -> missing
    rows[11]["view_count"] = 0       # brand-new video, zero views
    rows[11]["like_count"] = 0
    rows[11]["comment_count"] = 0
    rows[11]["video_age_days"] = 0   # published today
    return rows


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(make_rows())
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
