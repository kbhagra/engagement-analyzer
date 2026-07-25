"""Tests for services/channel_parser.py — run with:
    pytest tests/test_channel_parser.py
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.channel_parser import (  # noqa: E402
    ChannelParseError,
    parse_channel_url,
)

FAKE_ID = "UC" + "x" * 22  # 24 chars total


# ---------------------------------------------------------------- accepts

def test_handle_url():
    assert parse_channel_url("https://www.youtube.com/@Nike") == ("handle", "@Nike")


def test_handle_url_without_www_or_scheme():
    assert parse_channel_url("youtube.com/@Nike") == ("handle", "@Nike")


def test_mobile_host():
    assert parse_channel_url("https://m.youtube.com/@Nike") == ("handle", "@Nike")


def test_channel_id_url():
    kind, value = parse_channel_url(f"https://www.youtube.com/channel/{FAKE_ID}")
    assert (kind, value) == ("channel_id", FAKE_ID)


def test_bare_handle_with_at():
    assert parse_channel_url("@Nike") == ("handle", "@Nike")


def test_bare_handle_without_at():
    assert parse_channel_url("Nike") == ("handle", "@Nike")


def test_trailing_path_after_handle():
    assert parse_channel_url("https://www.youtube.com/@Nike/videos") == ("handle", "@Nike")


def test_surrounding_whitespace():
    assert parse_channel_url("  https://www.youtube.com/@Nike  ") == ("handle", "@Nike")


# ---------------------------------------------------------------- rejects

@pytest.mark.parametrize(
    "bad",
    [
        "",
        "   ",
        "https://vimeo.com/@Nike",
        "https://www.youtube.com/",
        "https://www.youtube.com/watch?v=abc123",
        "https://www.youtube.com/shorts/abc123",
        "https://www.youtube.com/user/OldStyleName",
        "https://www.youtube.com/channel/notAChannelId",
        "https://www.youtube.com/@x",  # handle too short
    ],
)
def test_rejects_bad_input(bad):
    with pytest.raises(ChannelParseError):
        parse_channel_url(bad)


def test_error_message_is_user_friendly():
    with pytest.raises(ChannelParseError) as exc:
        parse_channel_url("https://www.youtube.com/watch?v=abc123")
    assert "video" in str(exc.value)  # tells the user what went wrong