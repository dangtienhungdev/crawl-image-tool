"""
Manga List Routes

FastAPI routes for manga list crawling operations.
"""

from fastapi import APIRouter, HTTPException
from models.schemas import (
    MangaListCrawlRequest,
    MangaListCrawlResponse,
    ErrorResponse
)
from controllers.manga_list_controller import MangaListController

# Create router
manga_list_router = APIRouter(
    prefix="/api/v1/manga-list", tags=["Manga List Crawling"])


@manga_list_router.post("/crawl", response_model=MangaListCrawlResponse)
async def crawl_manga_list(request: MangaListCrawlRequest):
    """
    Crawl a manga list page and download all manga found

    This endpoint crawls a manga list page (like https://nettruyenvia.com/?page=637)
    and then processes each individual manga found on that page.

    **Features:**
    - Extract all manga URLs from the list page
    - Download each manga with configurable chapter limits
    - Support for both local and cloud storage
    - Configurable delays between operations
    - Comprehensive error reporting

    **Example Request:**
    ```json
    {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 5,
        "max_chapters_per_manga": 3,
        "image_type": "cloud",
        "delay_between_manga": 3.0,
        "delay_between_chapters": 2.0
    }
    ```

    **Response includes:**
    - Overall status and statistics
    - Detailed information for each manga processed
    - Total images downloaded across all manga
    - Processing time and error details
    """
    try:
        return await MangaListController.crawl_manga_list(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@manga_list_router.get("/health")
async def health_check():
    """
    Health check endpoint for manga list crawling service
    """
    return {
        "status": "healthy",
        "service": "Manga List Crawler API",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/v1/manga-list/crawl - Crawl manga list page"
        ]
    }


@manga_list_router.get("/examples")
async def get_examples():
    """
    Get example requests for manga list crawling
    """
    return {
        "examples": {
            "basic_local": {
                "description": "Basic manga list crawl with local storage",
                "request": {
                    "url": "https://nettruyenvia.com/?page=637",
                    "max_manga": 3,
                    "max_chapters_per_manga": 2,
                    "image_type": "local",
                    "delay_between_manga": 3.0,
                    "delay_between_chapters": 2.0
                }
            },
            "cloud_storage": {
                "description": "Manga list crawl with cloud storage",
                "request": {
                    "url": "https://nettruyenvia.com/?page=637",
                    "max_manga": 5,
                    "max_chapters_per_manga": 3,
                    "image_type": "cloud",
                    "delay_between_manga": 5.0,
                    "delay_between_chapters": 3.0
                }
            },
            "full_page": {
                "description": "Crawl all manga on a page (no limits)",
                "request": {
                    "url": "https://nettruyenvia.com/?page=637",
                    "image_type": "local",
                    "delay_between_manga": 2.0,
                    "delay_between_chapters": 1.0
                }
            }
        },
        "notes": [
            "Set max_manga to limit the number of manga processed",
            "Set max_chapters_per_manga to limit chapters per manga",
            "Use 'cloud' image_type to upload to Wasabi S3",
            "Adjust delays to avoid overwhelming the server"
        ]
    }
