"""CampaignLens — results dashboard routes (owned by Partner 2, Khushi).

Routes:
    GET /results   — load CSV, compute metrics, regenerate charts, render page
    GET /download  — download the current dataset as CSV
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from flask import Blueprint, render_template, send_file, url_for

from analysis.charts import generate_all_charts
from analysis.metrics import DATA_PATH, load_videos, summary_stats, top_videos

results_bp = Blueprint("results", __name__)


def _table_rows(df: pd.DataFrame) -> list[dict]:
    """Rows for the video table. NaN becomes None so the template can
    show 'Not available' instead of 'nan'."""
    cols = [
        "thumbnail_url", "title", "video_url", "published_at",
        "view_count", "like_count", "comment_count",
        "visible_engagement_rate", "views_per_day",
    ]
    view = df[cols].sort_values("view_count", ascending=False)
    rows = []
    for record in view.to_dict(orient="records"):
        row = {k: (None if pd.isna(v) else v) for k, v in record.items()}
        if row["published_at"] is not None:
            row["published_at"] = row["published_at"].strftime("%b %d, %Y")
        rows.append(row)
    return rows


@results_bp.route("/results")
def results():
    try:
        df = load_videos()
    except FileNotFoundError:
        return render_template(
            "error.html",
            message="No channel data yet. Analyze a channel first.",
        ), 404
    except ValueError:
        return render_template(
            "error.html",
            message="The collected data file is empty. Try analyzing again.",
        ), 422

    charts = generate_all_charts(df)

    channel = {
        "name": df["channel_name"].iloc[0],
        "subscribers": int(df["channel_subscriber_count"].iloc[0]),
        "thumbnail": df.get("channel_thumbnail_url", pd.Series([None])).iloc[0],
    }

    return render_template(
        "results.html",
        channel=channel,
        stats=summary_stats(df),
        charts=charts,
        most_engaging=top_videos(df, "visible_engagement_rate", 3)
        .to_dict(orient="records"),
        rows=_table_rows(df),
    )


@results_bp.route("/download")
def download():
    path = Path(DATA_PATH)
    if not path.exists():
        return render_template(
            "error.html", message="No dataset available to download yet."
        ), 404
    return send_file(path, as_attachment=True, download_name="videos.csv")