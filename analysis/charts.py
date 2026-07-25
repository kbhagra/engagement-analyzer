"""CampaignLens — chart generation for the results dashboard.

Owned by Partner 2 (Khushi). Reads the cleaned/derived DataFrame from
analysis.metrics and writes PNG charts into static/charts/ so the Flask
results page can display them with <img> tags.

Run standalone to test against the current data/videos.csv:
    python -m analysis.charts
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display window needed; we only save PNGs
import matplotlib.pyplot as plt
import pandas as pd

CHARTS_DIR = Path(__file__).resolve().parent.parent / "static" / "charts"

# One shared look for all charts so the dashboard feels intentional.
ACCENT = "#1f6f8b"
ACCENT_2 = "#e07a5f"
GRID = "#e3e3e3"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#cccccc",
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "font.size": 10,
    }
)


def _shorten(title: str, limit: int = 32) -> str:
    return title if len(title) <= limit else title[: limit - 1] + "…"


def _fmt_views(x, _pos=None) -> str:
    """Tick formatter: 1500000 -> 1.5M, 12000 -> 12K."""
    if x >= 1_000_000:
        return f"{x / 1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x / 1_000:.0f}K"
    return f"{x:.0f}"


def _save(fig, name: str) -> Path:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHARTS_DIR / name
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ------------------------------------------------------------------ charts

def chart_top_videos(df: pd.DataFrame, n: int = 10) -> Path:
    """Horizontal bar chart: top-n videos by view count."""
    data = df.dropna(subset=["view_count"]).nlargest(n, "view_count")
    data = data.iloc[::-1]  # largest bar on top

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(
        [_shorten(t) for t in data["title"]],
        data["view_count"],
        color=ACCENT,
    )
    ax.xaxis.set_major_formatter(_fmt_views)
    ax.set_xlabel("Views")
    ax.set_title(f"Top {len(data)} Videos by Views")
    return _save(fig, "views_chart.png")


def chart_views_vs_engagement(df: pd.DataFrame) -> Path:
    """Scatter plot: view count vs visible engagement rate."""
    data = df.dropna(subset=["view_count", "visible_engagement_rate"])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(
        data["view_count"],
        data["visible_engagement_rate"],
        color=ACCENT,
        alpha=0.75,
        edgecolors="white",
        s=70,
    )
    ax.xaxis.set_major_formatter(_fmt_views)
    ax.set_xlabel("Views")
    ax.set_ylabel("Visible Engagement Rate (%)")
    ax.set_title("Views vs Engagement Rate")
    return _save(fig, "engagement_chart.png")


def chart_performance_over_time(df: pd.DataFrame) -> Path:
    """Scatter over publication date: views per day (pacing)."""
    data = df.dropna(subset=["published_at", "views_per_day"]).sort_values(
        "published_at"
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(
        data["published_at"],
        data["views_per_day"],
        color=ACCENT_2,
        alpha=0.8,
        edgecolors="white",
        s=70,
    )
    ax.yaxis.set_major_formatter(_fmt_views)
    ax.set_xlabel("Publication Date")
    ax.set_ylabel("Views per Day")
    ax.set_title("Video Performance Over Time (Views per Day)")
    fig.autofmt_xdate(rotation=30)
    return _save(fig, "time_chart.png")


def generate_all_charts(df: pd.DataFrame) -> dict[str, str]:
    """Generate every chart; returns {chart_key: filename} for templates.

    Skips a chart (instead of crashing) if the data for it is entirely
    missing — e.g. a channel where every video has hidden stats.
    """
    charts: dict[str, str] = {}
    builders = {
        "top_videos": chart_top_videos,
        "views_vs_engagement": chart_views_vs_engagement,
        "over_time": chart_performance_over_time,
    }
    for key, builder in builders.items():
        try:
            path = builder(df)
            charts[key] = path.name
        except (ValueError, KeyError) as exc:
            print(f"Skipping chart '{key}': {exc}")
    return charts


if __name__ == "__main__":
    from analysis.metrics import load_videos

    frame = load_videos()
    results = generate_all_charts(frame)
    for chart_key, filename in results.items():
        print(f"{chart_key}: static/charts/{filename}")