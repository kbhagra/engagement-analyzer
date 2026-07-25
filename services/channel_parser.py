"""CampaignLens — YouTube channel URL parsing.

Turns a user-pasted channel link into something the YouTube Data API can
resolve. Two identifier types are supported (matching the project scope):

  https://www.youtube.com/@Nike            -> ("handle", "@Nike")
  https://www.youtube.com/channel/UC...    -> ("channel_id", "UC...")

The API resolves handles via channels.list(forHandle=...) and channel
IDs via channels.list(id=...), so the parser's job is only to classify
and extract — not to verify the channel exists (that's the API's job).
"""

from __future__ import annotations

from urllib.parse import urlparse

VALID_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com"}


class ChannelParseError(ValueError):
    """Raised when a link cannot be interpreted as a channel URL.

    The message is written to be shown directly to the user.
    """


def parse_channel_url(raw: str) -> tuple[str, str]:
    """Classify a channel link.

    Returns:
        ("handle", "@name") or ("channel_id", "UC...")

    Raises:
        ChannelParseError: with a user-facing message explaining the issue.
    """
    if not raw or not raw.strip():
        raise ChannelParseError("Please enter a YouTube channel link.")

    text = raw.strip()

    # Allow pasting a bare handle like "@Nike" or "Nike".
    if not text.lower().startswith(("http://", "https://", "youtube.com",
                                    "www.youtube.com", "m.youtube.com")):
        handle = text if text.startswith("@") else f"@{text}"
        if _looks_like_handle(handle):
            return ("handle", handle)
        raise ChannelParseError(
            "That doesn't look like a channel link or handle. "
            "Try a link like https://www.youtube.com/@ChannelName."
        )

    # Normalize scheme so urlparse fills in netloc.
    if not text.lower().startswith(("http://", "https://")):
        text = "https://" + text

    parsed = urlparse(text)
    host = parsed.netloc.lower()
    if host not in VALID_HOSTS:
        raise ChannelParseError(
            "Please use a youtube.com channel link, such as "
            "https://www.youtube.com/@ChannelName."
        )

    parts = [p for p in parsed.path.split("/") if p]
    if not parts:
        raise ChannelParseError(
            "That link points to YouTube's homepage, not a channel. "
            "Open the channel page and copy its link."
        )

    first = parts[0]

    # https://www.youtube.com/@Handle
    if first.startswith("@"):
        if _looks_like_handle(first):
            return ("handle", first)
        raise ChannelParseError("That channel handle looks invalid.")

    # https://www.youtube.com/channel/UCxxxxxxxx
    if first == "channel" and len(parts) >= 2:
        channel_id = parts[1]
        if _looks_like_channel_id(channel_id):
            return ("channel_id", channel_id)
        raise ChannelParseError(
            "That channel ID looks invalid. Channel IDs start with 'UC'."
        )

    # Video links, shorts, legacy /user/ URLs, etc.
    if first in {"watch", "shorts", "playlist"}:
        raise ChannelParseError(
            "That's a link to a video, not a channel. Open the channel "
            "page (click the channel name under a video) and copy that link."
        )
    if first in {"user", "c"}:
        raise ChannelParseError(
            "Legacy /user/ and /c/ links aren't supported. Open the channel "
            "page and copy its @handle link instead."
        )

    raise ChannelParseError(
        "Couldn't find a channel in that link. Try a link like "
        "https://www.youtube.com/@ChannelName."
    )


def _looks_like_handle(handle: str) -> bool:
    """YouTube handles: @ + 3-30 chars of letters, digits, '.', '_', '-'."""
    body = handle[1:]
    if not (3 <= len(body) <= 30):
        return False
    return all(c.isalnum() or c in "._-" for c in body)


def _looks_like_channel_id(cid: str) -> bool:
    """Channel IDs are 24 chars and start with 'UC'."""
    if not cid.startswith("UC") or len(cid) != 24:
        return False
    return all(c.isalnum() or c in "_-" for c in cid)