"""
Manga List Controller

Handles business logic for manga list crawling operations.
"""

from typing import Optional
from models.schemas import MangaListCrawlRequest, MangaListCrawlResponse
from services.manga_list_crawler import MangaListCrawler


class MangaListController:
    """Controller for manga list crawling operations"""

    @staticmethod
    async def crawl_manga_list(request: MangaListCrawlRequest) -> MangaListCrawlResponse:
        """
        Crawl a manga list page and process all manga found

        Args:
            request: MangaListCrawlRequest containing crawl parameters

        Returns:
            MangaListCrawlResponse with results
        """
        # Validate max_manga parameter
        if request.max_manga is not None and request.max_manga < 0:
            raise ValueError("max_manga must be >= 0")

        # Validate max_chapters_per_manga parameter
        if request.max_chapters_per_manga is not None and request.max_chapters_per_manga < 0:
            raise ValueError("max_chapters_per_manga must be >= 0")

        # Validate image_type parameter
        if request.image_type not in ["local", "cloud"]:
            raise ValueError("image_type must be 'local' or 'cloud'")

        # Validate delay parameters
        if request.delay_between_manga < 0:
            raise ValueError("delay_between_manga must be >= 0")

        if request.delay_between_chapters < 0:
            raise ValueError("delay_between_chapters must be >= 0")

        # Use the manga list crawler service
        async with MangaListCrawler() as crawler:
            return await crawler.crawl_manga_list(
                list_url=str(request.url),
                max_manga=request.max_manga,
                max_chapters_per_manga=request.max_chapters_per_manga,
                image_type=request.image_type,
                delay_between_manga=request.delay_between_manga,
                delay_between_chapters=request.delay_between_chapters,
                custom_headers=request.custom_headers
            )
