"""
Controller for handling image crawling business logic
"""

import asyncio
from typing import Dict, Any
from fastapi import HTTPException
from services.image_crawler import ImageCrawlerService
from models.schemas import CrawlRequest, CrawlResponse, CrawlStatus, ErrorResponse


class ImageController:
    """Controller for image crawling operations"""

    def __init__(self):
        self.crawler_service = ImageCrawlerService()

    async def crawl_images(self, request: CrawlRequest) -> CrawlResponse:
        """
        Handle image crawling request

        Args:
            request: CrawlRequest object with crawling parameters

        Returns:
            CrawlResponse object with crawling results

        Raises:
            HTTPException: If crawling fails completely
        """
        try:
            # Validate URL
            url_str = str(request.url)
            if not url_str.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid URL format. URL must start with http:// or https://"
                )

            # Use async context manager for the crawler service
            async with ImageCrawlerService() as crawler:
                # Perform crawling
                (
                    status,
                    domain,
                    folder_path,
                    total_found,
                    images_info,
                    errors,
                    processing_time
                ) = await crawler.crawl_images(
                    url=url_str,
                    max_images=request.max_images,
                    include_base64=request.include_base64,
                    use_selenium=request.use_selenium,
                    custom_headers=request.custom_headers
                )

                # Create response
                response = CrawlResponse(
                    status=status,
                    url=url_str,
                    domain=domain,
                    folder_path=folder_path,
                    total_images_found=total_found,
                    images_downloaded=len(images_info),
                    images=images_info,
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
                detail=f"Internal server error during image crawling: {str(e)}"
            )

    async def get_crawl_status(self, url: str) -> Dict[str, Any]:
        """
        Get status information for a crawled URL

        Args:
            url: Website URL to check status for

        Returns:
            Dictionary with status information
        """
        try:
            # This is a placeholder for future implementation
            # Could track crawling history, cache results, etc.
            return {
                "url": url,
                "message": "Status checking not implemented yet",
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error checking crawl status: {str(e)}"
            )

    async def health_check(self) -> Dict[str, str]:
        """
        Health check endpoint

        Returns:
            Dictionary with health status
        """
        try:
            return {
                "status": "healthy",
                "service": "Image Crawler API",
                "version": "1.0.0"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Health check failed: {str(e)}"
            )
