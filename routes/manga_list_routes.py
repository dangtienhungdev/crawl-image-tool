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
    - **NEW**: Smart duplicate detection - automatically skips existing manga and chapters
    - **NEW**: Progress tracking - monitor download status across sessions

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


@manga_list_router.get("/progress")
async def get_manga_list_progress(list_url: str, image_type: str = "local"):
    """
    Get progress information for manga list crawling

    This endpoint shows which manga from a list page have already been downloaded
    and their current progress status.

    Args:
        list_url: URL of the manga list page (e.g., https://nettruyenvia.com/?page=637)
        image_type: Storage type ("local" or "cloud")

    Returns:
        Dictionary containing progress information for all manga in the list
    """
    try:
        if not list_url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format. URL must start with http:// or https://"
            )

        if image_type not in ["local", "cloud"]:
            raise HTTPException(
                status_code=400,
                detail="image_type must be 'local' or 'cloud'"
            )

        result = await MangaListController.get_manga_list_progress(list_url, image_type)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving manga list progress: {str(e)}")


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
            "POST /api/v1/manga-list/crawl - Crawl manga list page",
            "GET /api/v1/manga-list/progress - Get manga list progress"
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
