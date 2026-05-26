"""TikTok downloader placeholder.

This module is intentionally small for phase 1. A future implementation can
wrap yt-dlp or a dedicated TikTok provider without changing the CLI facade.
"""


class TikTokDownloader:
    """Reserved adapter for future TikTok support."""

    def download(self, url: str) -> None:
        raise NotImplementedError("TikTok support is planned for a future MediaFlux release.")
