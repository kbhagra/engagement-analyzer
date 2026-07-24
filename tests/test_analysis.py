"""Tests for analysis/metrics.py — run with: pytest tests/test_analysis.py"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.metrics import (  # noqa: E402
    add_derived_metrics,
    clean_videos,
    load_videos,
    summary_stats,
    title_length_correlation,
    top_videos,
)


def _sample_df():
    return pd.DataFrame(
        {
            "title": ["A normal video", "Hidden likes", "Zero views", "Big hit"],
            "title_length": [14, 12, 10, 7],
            "published_at": [
                "2026-06-01T10:00:00Z",
                "2026-05-01T10:00:00Z",
                "2026-07-23T10:00:00Z",
                "2025-08-01T10:00:00Z",
            ],
            "video_age_days": [52, 83, 0, 356],
            "duration_seconds": [300, 120, 60, 900],
            "view_count": [10_000, 50_000, 0, 2_000_000],
            "like_count": [400, "", 0, 90_000],       # "" = hidden by uploader
            "comment_count": [100, 500, 0, 4_000],
        }
    )


def _processed():
    return add_derived_metrics(clean_videos(_sample_df()))


def test_clean_coerces_empty_string_to_nan():
    df = clean_videos(_sample_df())
    assert np.isnan(df.loc[1, "like_count"])          # NOT converted to 0
    assert df.loc[0, "like_count"] == 400


def test_engagement_rate_normal_row():
    df = _processed()
    # (400 + 100) / 10_000 * 100 = 5.0
    assert df.loc[0, "visible_engagement_rate"] == pytest.approx(5.0)


def test_zero_views_gives_nan_rate_not_zero():
    df = _processed()
    assert np.isnan(df.loc[2, "visible_engagement_rate"])
    assert np.isnan(df.loc[2, "like_rate"])


def test_hidden_likes_uses_available_comments():
    df = _processed()
    # likes hidden, comments 500, views 50_000 -> lower-bound 1.0%
    assert df.loc[1, "visible_engagement_rate"] == pytest.approx(1.0)
    assert np.isnan(df.loc[1, "like_rate"])           # can't compute like rate


def test_views_per_day_clips_zero_age():
    df = _processed()
    assert df.loc[2, "views_per_day"] == 0            # 0 views / 1 day
    assert df.loc[3, "views_per_day"] == pytest.approx(2_000_000 / 356, rel=1e-3)


def test_summary_stats_keys_and_top_video():
    stats = summary_stats(_processed())
    assert stats["videos_analyzed"] == 4
    assert stats["highest_performing_video"] == "Big hit"
    assert stats["average_views"] == pytest.approx(515_000)


def test_top_videos_excludes_nan():
    df = _processed()
    ranked = top_videos(df, "like_rate", n=5)
    assert "Hidden likes" not in ranked["title"].values


def test_correlation_needs_three_rows():
    df = _processed().iloc[:2]
    assert title_length_correlation(df) is None


def test_load_videos_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_videos(tmp_path / "nope.csv")


def test_load_videos_empty_file(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("view_count,like_count\n")
    with pytest.raises(ValueError):
        load_videos(p)
