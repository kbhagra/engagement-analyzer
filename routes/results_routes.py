"""CampaignLens — results dashboard routes (owned by Partner 2, Khushi).

Routes:
    GET /results   — load CSV, compute metrics, regenerate charts, render page
    GET /download  — download the current dataset as CSV
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from flask import Blueprint, render_template, request, send_file, url_for

from analysis.charts import generate_all_charts
from analysis.metrics import DATA_PATH, load_videos, summary_stats, top_videos

results_bp = Blueprint("results", __name__)

# Sort options for the table widget: key -> (label, column, ascending)
SORT_OPTIONS = {
    "most_viewed": ("Most viewed", "view_count", False),
    "newest": ("Newest", "published_at", False),
    "most_liked": ("Most liked", "like_count", False),
    "most_engaging": ("Most engaging", "visible_engagement_rate", False),
}
DEFAULT_SORT = "most_viewed"

# Chart selector options: key -> (label, charts-dict key)
CHART_OPTIONS = {
    "all": ("All charts", None),
    "top_videos": ("Top videos by views", "top_videos"),
    "engagement": ("Views vs engagement", "views_vs_engagement"),
    "over_time": ("Performance over time", "over_time"),
}
DEFAULT_CHART = "all"


def _table_rows(df: pd.DataFrame, sort_key: str) -> list[dict]:
    """Rows for the video table. NaN becomes None so the template can
    show 'Not available' instead of 'nan'."""
    cols = [
        "thumbnail_url", "title", "video_url", "published_at",
        "view_count", "like_count", "comment_count",
        "visible_engagement_rate", "views_per_day",
    ]
    _, sort_col, ascending = SORT_OPTIONS[sort_key]
    view = df[cols].sort_values(sort_col, ascending=ascending, na_position="last")
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

    # Widget state from query params; unknown values fall back to defaults.
    sort_key = request.args.get("sort", DEFAULT_SORT)
    if sort_key not in SORT_OPTIONS:
        sort_key = DEFAULT_SORT
    chart_key = request.args.get("chart", DEFAULT_CHART)
    if chart_key not in CHART_OPTIONS:
        chart_key = DEFAULT_CHART

    charts = generate_all_charts(df)

    # Narrow to one chart if the selector asked for it.
    selected = CHART_OPTIONS[chart_key][1]
    if selected is not None:
        charts = {k: v for k, v in charts.items() if k == selected}

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
        rows=_table_rows(df, sort_key),
        sort_options=SORT_OPTIONS,
        chart_options=CHART_OPTIONS,
        current_sort=sort_key,
        current_chart=chart_key,
    )


@results_bp.route("/download")
def download():
    path = Path(DATA_PATH)
    if not path.exists():
        return render_template(
            "error.html", message="No dataset available to download yet."
        ), 404
    return send_file(path, as_attachment=True, download_name="videos.csv")