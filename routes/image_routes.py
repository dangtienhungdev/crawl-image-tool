"""
FastAPI routes for image crawling endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from models.schemas import CrawlRequest, CrawlResponse, ErrorResponse
from controllers.image_controller import ImageController


# Create router instance
router = APIRouter(prefix="/api/v1", tags=["Image Crawler"])

# Create controller instance
image_controller = ImageController()


@router.post(
    "/crawl",
    response_model=CrawlResponse,
    summary="Crawl images from a website",
    description="""
    Crawl and download all images from a given website URL.

    Features:
    - Downloads regular images from img tags
    - Handles lazy-loaded images using Selenium
    - Extracts base64 encoded images
    - Processes JavaScript-rendered content
    - Saves images to domain-named folders

    The system will create a folder named after the website domain
    and download all found images into that folder.
    """,
    responses={
        200: {"model": CrawlResponse, "description": "Successful crawling operation"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def crawl_images(request: CrawlRequest) -> CrawlResponse:
    """
    Crawl images from a website

    Args:
        request: CrawlRequest object containing URL and crawling parameters

    Returns:
        CrawlResponse object with crawling results
    """
    try:
        result = await image_controller.crawl_images(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during image crawling: {str(e)}"
        )


@router.get(
    "/status/{url:path}",
    summary="Get crawling status for a URL",
    description="Get the current status and information for a previously crawled URL",
    responses={
        200: {"description": "Status information retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_crawl_status(url: str) -> Dict[str, Any]:
    """
    Get crawling status for a specific URL

    Args:
        url: Website URL to check status for

    Returns:
        Dictionary containing status information
    """
    try:
        result = await image_controller.get_crawl_status(url)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving crawl status: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Check if the image crawler service is running properly",
    responses={
        200: {"description": "Service is healthy"},
        500: {"model": ErrorResponse, "description": "Service is unhealthy"}
    }
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint

    Returns:
        Dictionary with health status information
    """
    try:
        result = await image_controller.health_check()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


# Note: Exception handlers are defined in main.py since APIRouter doesn't support them
