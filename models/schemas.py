"""
Data models and schemas for the image crawler API
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from enum import Enum


class CrawlStatus(str, Enum):
    """Status of the crawling operation"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ImageInfo(BaseModel):
    """Information about a downloaded image"""
    original_url: str = Field(..., description="Original URL of the image")
    local_path: str = Field(..., description="Local path where image is saved")
    filename: str = Field(..., description="Name of the saved file")
    cloud_url: Optional[str] = Field(None, description="Cloud URL if uploaded to Wasabi S3")
    size_bytes: Optional[int] = Field(None, description="Size of the image in bytes")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    format: Optional[str] = Field(None, description="Image format (jpg, png, etc.)")


class CrawlRequest(BaseModel):
    """Request model for crawling images"""
    url: HttpUrl = Field(..., description="URL of the website to crawl")
    max_images: Optional[int] = Field(default=100, description="Maximum number of images to download")
    include_base64: bool = Field(default=True, description="Whether to include base64 encoded images")
    use_selenium: bool = Field(default=True, description="Whether to use Selenium for JavaScript rendering")
    custom_headers: Optional[dict] = Field(default=None, description="Custom HTTP headers")
    image_type: str = Field(default="local", description="Storage type: 'local' or 'cloud' (Wasabi S3)")


class CrawlResponse(BaseModel):
    """Response model for crawling operation"""
    status: CrawlStatus = Field(..., description="Status of the crawling operation")
    url: str = Field(..., description="URL that was crawled")
    domain: str = Field(..., description="Domain name extracted from URL")
    folder_path: str = Field(..., description="Local folder where images are saved")
    total_images_found: int = Field(..., description="Total number of images found on the page")
    images_downloaded: int = Field(..., description="Number of images successfully downloaded")
    images: List[ImageInfo] = Field(..., description="List of downloaded images")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    processing_time_seconds: float = Field(..., description="Time taken to process the request")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


# Manga/Chapter crawling models
class ChapterInfo(BaseModel):
    """Information about a manga chapter"""
    chapter_number: str = Field(..., description="Chapter number or identifier")
    chapter_title: Optional[str] = Field(None, description="Chapter title")
    chapter_url: str = Field(..., description="URL of the chapter")
    images_count: int = Field(0, description="Number of images in this chapter")
    images: List[ImageInfo] = Field(default_factory=list, description="List of images in this chapter")
    errors: List[str] = Field(default_factory=list, description="Errors encountered in this chapter")
    processing_time_seconds: float = Field(0, description="Time taken to process this chapter")


class MangaCrawlRequest(BaseModel):
    """Request model for crawling entire manga series"""
    url: HttpUrl = Field(..., description="URL of the manga series page")
    max_chapters: Optional[int] = Field(default=None, description="Maximum number of chapters to download (None for all)")
    start_chapter: Optional[int] = Field(default=None, description="Chapter to start from (None for first available)")
    end_chapter: Optional[int] = Field(default=None, description="Chapter to end at (None for last available)")
    custom_headers: Optional[dict] = Field(default=None, description="Custom HTTP headers")
    delay_between_chapters: float = Field(default=2.0, description="Delay between chapter downloads (seconds)")
    image_type: str = Field(default="local", description="Storage type: 'local' or 'cloud' (Wasabi S3)")


class MangaCrawlResponse(BaseModel):
    """Response model for manga crawling operation"""
    status: CrawlStatus = Field(..., description="Status of the crawling operation")
    manga_url: str = Field(..., description="URL of the manga series")
    manga_title: str = Field(..., description="Title of the manga series")
    manga_folder: str = Field(..., description="Local folder where manga is saved")
    total_chapters_found: int = Field(..., description="Total number of chapters found")
    chapters_downloaded: int = Field(..., description="Number of chapters successfully downloaded")
    total_images_downloaded: int = Field(..., description="Total number of images downloaded across all chapters")
    chapters: List[ChapterInfo] = Field(..., description="List of processed chapters")
    errors: List[str] = Field(default_factory=list, description="Global errors encountered")
    processing_time_seconds: float = Field(..., description="Total time taken to process the manga")


class MangaListCrawlRequest(BaseModel):
    """Request model for crawling manga list page"""
    url: HttpUrl = Field(..., description="URL of the manga list page (e.g., https://nettruyenvia.com/?page=637)")
    max_manga: Optional[int] = Field(default=None, description="Maximum number of manga to crawl (None for all)")
    max_chapters_per_manga: Optional[int] = Field(default=None, description="Maximum chapters per manga (None for all)")
    image_type: str = Field(default="local", description="Storage type: 'local' or 'cloud' (Wasabi S3)")
    delay_between_manga: float = Field(default=3.0, description="Delay between manga downloads (seconds)")
    delay_between_chapters: float = Field(default=2.0, description="Delay between chapter downloads (seconds)")
    custom_headers: Optional[dict] = Field(default=None, description="Custom HTTP headers")


class MangaListInfo(BaseModel):
    """Information about a manga from the list"""
    manga_url: str = Field(..., description="URL of the manga series page")
    manga_title: str = Field(..., description="Title of the manga series")
    manga_folder: str = Field(..., description="Folder path for the manga")
    total_chapters: int = Field(..., description="Total number of chapters found")
    chapters_downloaded: int = Field(..., description="Number of chapters successfully downloaded")
    total_images_downloaded: int = Field(..., description="Total number of images downloaded")
    status: str = Field(..., description="Status: 'success', 'partial', 'failed'")
    processing_time_seconds: float = Field(..., description="Time taken to process this manga")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")


class MangaListCrawlResponse(BaseModel):
    """Response model for manga list crawling"""
    status: CrawlStatus = Field(..., description="Overall status: 'success', 'partial', 'failed'")
    list_url: str = Field(..., description="URL of the manga list page")
    total_manga_found: int = Field(..., description="Total number of manga found on the page")
    manga_processed: int = Field(..., description="Number of manga successfully processed")
    total_images_downloaded: int = Field(..., description="Total images downloaded across all manga")
    manga_list: List[MangaListInfo] = Field(..., description="List of processed manga with details")
    errors: List[str] = Field(default_factory=list, description="List of general errors")
    processing_time_seconds: float = Field(..., description="Total processing time")
