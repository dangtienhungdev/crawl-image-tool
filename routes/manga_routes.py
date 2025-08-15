"""
FastAPI routes for manga crawling endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from models.schemas import MangaCrawlRequest, MangaCrawlResponse, ErrorResponse
from controllers.manga_controller import MangaController


# Create router instance
router = APIRouter(prefix="/api/v1/manga", tags=["Manga Crawler"])

# Create controller instance
manga_controller = MangaController()


@router.post(
    "/crawl",
    response_model=MangaCrawlResponse,
    summary="Crawl entire manga series",
    description="""
    Crawl and download an entire manga series with all chapters organized by folders.

    Features:
    - Downloads all chapters from a manga series
    - Organizes images in chapter folders (Chapter_1/, Chapter_2/, etc.)
    - Sequential image naming (001.jpg, 002.jpg, etc.)
    - Bypasses image hotlink protection using proper Referer headers
    - Supports chapter range selection (start/end chapters)
    - Configurable delay between chapter downloads
    - Handles JavaScript-rendered content with Selenium

    Example folder structure:
    ```
    hoc_cung_em_gai_khong_can_than_tro_thanh_vo_dich/
        Chapter_1/
            001.jpg
            002.jpg
            003.jpg
        Chapter_2/
            001.jpg
            002.jpg
            ...
    ```

    **Warning**: This operation can take a very long time for manga with many chapters.
    Consider using chapter limits or ranges for testing.
    """,
    responses={
        200: {"model": MangaCrawlResponse, "description": "Successful manga crawling operation"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def crawl_manga(request: MangaCrawlRequest) -> MangaCrawlResponse:
    """
    Crawl entire manga series with all chapters

    Args:
        request: MangaCrawlRequest object containing manga URL and crawling parameters

    Returns:
        MangaCrawlResponse object with crawling results
    """
    try:
        result = await manga_controller.crawl_manga(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during manga crawling: {str(e)}"
        )


@router.get(
    "/info",
    summary="Get manga series information",
    description="""
    Get basic information about a manga series without downloading.
    This includes the title, total chapter count, and a preview of the first 10 chapters.

    Use this endpoint to preview what will be downloaded before starting a full crawl.
    """,
    responses={
        200: {"description": "Manga information retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid URL"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_manga_info(url: str) -> Dict[str, Any]:
    """
    Get information about a manga series

    Args:
        url: Manga series URL

    Returns:
        Dictionary containing manga information
    """
    try:
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format. URL must start with http:// or https://"
            )

        result = await manga_controller.get_manga_info(url)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving manga information: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check for manga crawler",
    description="Check if the manga crawler service is running properly",
    responses={
        200: {"description": "Service is healthy"},
        500: {"model": ErrorResponse, "description": "Service is unhealthy"}
    }
)
async def manga_health_check() -> Dict[str, str]:
    """
    Health check endpoint for manga crawler

    Returns:
        Dictionary with health status information
    """
    try:
        result = await manga_controller.health_check()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Manga crawler health check failed: {str(e)}"
        )


# Example request bodies for documentation
@router.get(
    "/examples",
    summary="Example requests for manga crawling",
    description="Get example request bodies for different manga crawling scenarios"
)
async def get_examples():
    """Get example requests for manga crawling"""
    return {
        "full_manga_crawl": {
            "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
            "max_chapters": None,
            "start_chapter": 1,
            "end_chapter": None,
            "delay_between_chapters": 2.0
        },
        "limited_chapters": {
            "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
            "max_chapters": 10,
            "start_chapter": 1,
            "end_chapter": 10,
            "delay_between_chapters": 1.0
        },
        "chapter_range": {
            "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
            "max_chapters": None,
            "start_chapter": 5,
            "end_chapter": 15,
            "delay_between_chapters": 2.0
        },
        "with_custom_headers": {
            "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
            "max_chapters": 5,
            "custom_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9,vi;q=0.8"
            },
            "delay_between_chapters": 3.0
        }
    }
