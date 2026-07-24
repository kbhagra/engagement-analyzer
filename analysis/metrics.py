"""CampaignLens — data loading, cleaning, and metric calculations.

Owned by Partner 2 (Khushi). Reads the CSV produced by the data-collection
pipeline (services/data_storage.py) and derives all analysis columns.

Key design decisions:
- Missing likes/comments (hidden or disabled on YouTube) are kept as NaN,
  NOT converted to 0. A confirmed zero and "not available" mean different
  things, and the dashboard displays NaN as "Not available".
- Derived metrics guard against division by zero (0 views, 0-day-old video).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "videos.csv"

NUMERIC_COLUMNS = [
    "channel_subscriber_count",
    "title_length",
    "video_age_days",
    "duration_seconds",
    "view_count",
    "like_count",
    "comment_count",
]


# ---------------------------------------------------------------- loading

def load_videos(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Load the video CSV into a cleaned DataFrame.

    Raises FileNotFoundError if no data has been collected yet, and
    ValueError if the file exists but contains no rows.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"No video data found at {path}. Run a channel analysis first."
        )

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("The video data file is empty.")

    df = clean_videos(df)
    df = add_derived_metrics(df)
    return df


def clean_videos(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce types. Empty strings / bad values become NaN (not 0)."""
    df = df.copy()

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(
            df["published_at"], errors="coerce", utc=True
        )

    # Recompute title_length if absent or unusable.
    if "title" in df.columns:
        if "title_length" not in df.columns or df["title_length"].isna().all():
            df["title_length"] = df["title"].astype(str).str.len()

    return df


# ---------------------------------------------------------- derived metrics

def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add engagement and pacing metrics.

    visible_engagement_rate = (likes + comments) / views * 100
    like_rate               = likes / views * 100
    comment_rate            = comments / views * 100
    views_per_day           = views / max(age_days, 1)

    Rows with 0 views get NaN rates (a rate of an unviewed video is
    undefined, not zero). Rows with missing likes AND comments get NaN
    engagement. If exactly one of likes/comments is missing, engagement
    uses the available one — this is a lower-bound estimate.
    """
    df = df.copy()
    views = df["view_count"]
    likes = df["like_count"]
    comments = df["comment_count"]

    # Engagement count: sum what we can see; NaN only if both are missing.
    df["visible_engagement_count"] = likes.fillna(0) + comments.fillna(0)
    both_missing = likes.isna() & comments.isna()
    df.loc[both_missing, "visible_engagement_count"] = np.nan

    safe_views = views.where(views > 0)  # 0 -> NaN so division yields NaN

    df["visible_engagement_rate"] = (
        df["visible_engagement_count"] / safe_views * 100
    ).round(3)
    df["like_rate"] = (likes / safe_views * 100).round(3)
    df["comment_rate"] = (comments / safe_views * 100).round(3)

    age = df["video_age_days"].clip(lower=1)
    df["views_per_day"] = (views / age).round(1)

    return df


# ---------------------------------------------------------- summary stats

def summary_stats(df: pd.DataFrame) -> dict:
    """Channel-level summary for the dashboard cards."""
    def _clean(x):
        return None if pd.isna(x) else float(x)

    top_idx = df["view_count"].idxmax() if df["view_count"].notna().any() else None
    top_video = df.loc[top_idx, "title"] if top_idx is not None else None

    return {
        "videos_analyzed": int(len(df)),
        "total_views": _clean(df["view_count"].sum()),
        "average_views": _clean(df["view_count"].mean()),
        "median_views": _clean(df["view_count"].median()),
        "average_likes": _clean(df["like_count"].mean()),
        "average_comments": _clean(df["comment_count"].mean()),
        "average_engagement_rate": _clean(df["visible_engagement_rate"].mean()),
        "average_views_per_day": _clean(df["views_per_day"].mean()),
        "highest_performing_video": top_video,
    }


def top_videos(df: pd.DataFrame, by: str, n: int = 5) -> pd.DataFrame:
    """Top-n ranking by a metric column; NaN rows are excluded."""
    if by not in df.columns:
        raise KeyError(f"Unknown ranking column: {by}")
    return df.dropna(subset=[by]).nlargest(n, by)


def title_length_correlation(df: pd.DataFrame) -> float | None:
    """Pearson correlation between title length and engagement rate.

    Returns None when there are fewer than 3 usable rows. Remember to
    present this as correlation, not causation.
    """
    usable = df.dropna(subset=["title_length", "visible_engagement_rate"])
    if len(usable) < 3:
        return None
    r = usable["title_length"].corr(usable["visible_engagement_rate"])
    return None if pd.isna(r) else round(float(r), 3)
