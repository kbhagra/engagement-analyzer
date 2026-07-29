from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from services.channel_parser import ChannelParseError, parse_channel_url
from services.data_storage import save_videos
from services.youtube_api import YouTubeAPIError, fetch_channel_videos

search_bp = Blueprint("search", __name__)


@search_bp.route("/")
def search():
    return render_template("search.html")


@search_bp.route("/analyze", methods=["POST"])
def analyze():
    channel_url = request.form.get("channel_url", "")
    max_videos = request.form.get("max_videos", "20")
    try:
        kind, identifier = parse_channel_url(channel_url)
        rows = fetch_channel_videos(kind, identifier, int(max_videos))
    except (ChannelParseError, YouTubeAPIError) as error:
        return render_template(
            "search.html", error=str(error),
            channel_url=channel_url, max_videos=max_videos,
        ), 400
    save_videos(rows)
    return redirect(url_for("results.results"))
