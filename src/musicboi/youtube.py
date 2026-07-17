from typing import Any, Callable
import yt_dlp
from dataclasses import dataclass


@dataclass
class TrackInfo:
    title: str
    duration_secs: str
    uploader: str
    description: str
    thumbnails: list[dict[str, Any]]


class YoutubeDl:
    def __init__(self) -> None:
        self.opts: Any = {
            "skip_download": True,
            "quiet": True,
        }

    def get_info(self, url: str) -> TrackInfo:
        with yt_dlp.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(url)
            default_value = "N/A"
            return TrackInfo(
                title=info.get("title") or default_value,
                duration_secs=str(info.get("duration")) or default_value,
                uploader=info.get("uploader") or default_value,
                description=info.get("description") or default_value,
                thumbnails=info.get("thumbnails") or [],
            )


ydl = YoutubeDl()
