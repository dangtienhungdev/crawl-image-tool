"""
Controller for handling manga crawling business logic
"""

import asyncio
from typing import Dict, Any
from fastapi import HTTPException

from services.manga_crawler import MangaCrawlerService
from models.schemas import MangaCrawlRequest, MangaCrawlResponse, CrawlStatus


class MangaController:
    """Controller for manga crawling operations"""

    def __init__(self):
        pass

    async def crawl_manga(self, request: MangaCrawlRequest) -> MangaCrawlResponse:
        """
        Handle manga crawling request

        Args:
            request: MangaCrawlRequest object with crawling parameters

        Returns:
            MangaCrawlResponse object with crawling results

        Raises:
            HTTPException: If crawling fails completely
        """
        try:
            # Validate URL
            url_str = str(request.url)
            print(url_str)
            if not url_str.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid URL format. URL must start with http:// or https://"
                )

            # Validate chapter range (allow None or >= 1)
            if request.start_chapter is not None and request.start_chapter < 1:
                raise HTTPException(
                    status_code=400,
                    detail="start_chapter must be >= 1"
                )

            if request.end_chapter and request.start_chapter and request.end_chapter < request.start_chapter:
                raise HTTPException(
                    status_code=400,
                    detail="end_chapter must be >= start_chapter"
                )

            if request.max_chapters is not None and request.max_chapters < 0:
                raise HTTPException(
                    status_code=400,
                    detail="max_chapters must be >= 0 (0 means no limit)"
                )

            # Use async context manager for the manga crawler service
            async with MangaCrawlerService() as crawler:
                # Perform crawling
                (
                    status,
                    manga_title,
                    manga_folder,
                    total_chapters_found,
                    chapters_info,
                    errors,
                    processing_time
                ) = await crawler.crawl_manga(
                    manga_url=url_str,
                    max_chapters=request.max_chapters,
                    start_chapter=request.start_chapter,
                    end_chapter=request.end_chapter,
                    custom_headers=request.custom_headers,
                    delay_between_chapters=request.delay_between_chapters,
                    image_type=request.image_type
                )

                # Calculate total images downloaded
                total_images_downloaded = sum(len(ch.images) for ch in chapters_info)

                # Create response
                response = MangaCrawlResponse(
                    status=status,
                    manga_url=url_str,
                    manga_title=manga_title,
                    manga_folder=manga_folder,
                    total_chapters_found=total_chapters_found,
                    chapters_downloaded=len([ch for ch in chapters_info if ch.images_count > 0]),
                    total_images_downloaded=total_images_downloaded,
                    chapters=chapters_info,
                    errors=errors,
                    processing_time_seconds=round(processing_time, 2)
                )

                return response

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error during manga crawling: {str(e)}"
            )

    async def get_manga_info(self, url: str) -> Dict[str, Any]:
        """
        Get basic information about a manga series (title, chapter count)

        Args:
            url: Manga series URL

        Returns:
            Dictionary with manga information
        """
        try:
            # This is a preview function to get manga info without downloading
            async with MangaCrawlerService() as crawler:
                # Get chapter list only
                chapters = await crawler._get_chapter_list(url)

                # Get manga title
                import aiohttp
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            manga_title = crawler._extract_manga_title(html_content)
                        else:
                            manga_title = "Unknown"

                return {
                    "manga_url": url,
                    "manga_title": manga_title,
                    "total_chapters": len(chapters),
                    "chapters": [
                        {
                            "chapter_number": ch[0],
                            "chapter_title": ch[1],
                            "chapter_url": ch[2]
                        } for ch in chapters[:10]  # Show first 10 chapters as preview
                    ],
                    "preview_note": f"Showing first 10 chapters out of {len(chapters)} total"
                }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting manga info: {str(e)}"
            )

    async def health_check(self) -> Dict[str, str]:
        """
        Health check endpoint for manga crawler

        Returns:
            Dictionary with health status
        """
        try:
            return {
                "status": "healthy",
                "service": "Manga Crawler API",
                "version": "1.0.0",
                "features": "Full manga series crawling with chapter organization"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Manga crawler health check failed: {str(e)}"
            )

    async def get_manga_progress(self, manga_title: str, image_type: str = "local") -> Dict[str, Any]:
        """
        Get download progress for a specific manga

        Args:
            manga_title: Title of the manga (sanitized folder name)
            image_type: Storage type ("local" or "cloud")

        Returns:
            Dictionary containing manga progress information
        """
        try:
            # Validate manga title
            if not manga_title or len(manga_title.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Manga title cannot be empty"
                )

            # Create manga folder path
            manga_folder = os.path.join('downloads', manga_title.strip())

            # Use async context manager for the manga crawler service
            async with MangaCrawlerService() as crawler:
                # Get progress from existence checker
                progress = await crawler.existence_checker.get_manga_progress(manga_folder, image_type)

                # Add manga title and folder info
                progress.update({
                    "manga_title": manga_title,
                    "manga_folder": manga_folder,
                    "image_type": image_type
                })

                return progress

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving manga progress: {str(e)}"
            )
