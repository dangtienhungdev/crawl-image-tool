"""
Manga List Crawler Service

This service handles crawling manga list pages (like https://nettruyenvia.com/?page=637)
and then crawls each individual manga found on that page.
"""

import asyncio
import aiohttp
import time
import os
from typing import List, Tuple, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path

from models.schemas import (
    CrawlStatus,
    MangaListCrawlRequest,
    MangaListCrawlResponse,
    MangaListInfo
)
from services.manga_crawler import MangaCrawlerService


class MangaListCrawler:
    """Service for crawling manga list pages and processing all manga found"""

    def __init__(self):
        self.session = None
        self.manga_crawler = MangaCrawlerService()

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize folder name by removing/replacing invalid characters"""
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')

        # Replace spaces with underscores
        name = name.replace(' ', '_')

        # Remove multiple consecutive underscores
        while '__' in name:
            name = name.replace('__', '_')

        # Remove leading/trailing underscores
        name = name.strip('_')

        return name

    async def _extract_manga_urls(self, list_url: str, custom_headers: Optional[dict] = None) -> List[Tuple[str, str]]:
        """
        Extract all manga URLs and titles from a manga list page

        Args:
            list_url: URL of the manga list page
            custom_headers: Custom HTTP headers

        Returns:
            List of tuples (manga_url, manga_title)
        """
        print(f"🔍 Extracting manga URLs from: {list_url}")

        # Default headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # Merge custom headers if provided
        if custom_headers:
            headers.update(custom_headers)

        try:
            async with self.session.get(list_url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to fetch manga list page: HTTP {response.status}")

                html_content = await response.text()

        except Exception as e:
            raise Exception(f"Error fetching manga list page: {str(e)}")

        # Parse HTML to extract manga links
        soup = BeautifulSoup(html_content, 'html.parser')
        manga_links = []

        # Find all links and filter for manga series (not chapters)
        all_links = soup.find_all('a', href=True)
        manga_links = []

        for link in all_links:
            href = link.get('href', '')
            title = link.get('title', '') or link.get_text(strip=True)

            # Only include manga series links (not chapter links)
            if '/truyen-tranh/' in href and '/chuong-' not in href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    manga_url = urljoin(list_url, href)
                elif href.startswith('http'):
                    manga_url = href
                else:
                    manga_url = urljoin(list_url, href)

                # Clean up title
                if title:
                    title = title.strip()
                    # Remove common prefixes
                    for prefix in ['Truyện tranh ', 'Comic ', 'Manga ']:
                        if title.startswith(prefix):
                            title = title[len(prefix):]

                # Skip empty titles or very short titles
                if title and len(title) > 2:
                    manga_links.append((manga_url, title))

        # Remove duplicates while preserving order
        seen_urls = set()
        unique_manga_links = []
        for manga_url, title in manga_links:
            if manga_url not in seen_urls:
                seen_urls.add(manga_url)
                unique_manga_links.append((manga_url, title))

        print(
            f"📚 Found {len(unique_manga_links)} unique manga on the list page")

        # Show first few manga for verification
        for i, (url, title) in enumerate(unique_manga_links[:5]):
            print(f"   {i+1}. {title} -> {url}")

        if len(unique_manga_links) > 5:
            print(f"   ... and {len(unique_manga_links) - 5} more")

        return unique_manga_links

    async def crawl_manga_list(
        self,
        list_url: str,
        max_manga: Optional[int] = None,
        max_chapters_per_manga: Optional[int] = None,
        image_type: str = "local",
        delay_between_manga: float = 3.0,
        delay_between_chapters: float = 2.0,
        custom_headers: Optional[dict] = None
    ) -> MangaListCrawlResponse:
        """
        Crawl a manga list page and process all manga found

        Args:
            list_url: URL of the manga list page
            max_manga: Maximum number of manga to process
            max_chapters_per_manga: Maximum chapters per manga
            image_type: Storage type ('local' or 'cloud')
            delay_between_manga: Delay between manga downloads
            delay_between_chapters: Delay between chapter downloads
            custom_headers: Custom HTTP headers

        Returns:
            MangaListCrawlResponse with results
        """
        start_time = time.time()
        errors = []
        manga_list_results = []

        try:
            print(f"🚀 Starting manga list crawl: {list_url}")

            # Extract all manga URLs from the list page
            manga_links = await self._extract_manga_urls(list_url, custom_headers)

            if not manga_links:
                raise Exception("No manga found on the list page")

            # Apply max_manga limit if specified
            if max_manga and max_manga > 0:
                manga_links = manga_links[:max_manga]
                print(f"📊 Limiting to {max_manga} manga")

            total_manga_found = len(manga_links)
            manga_processed = 0
            total_images_downloaded = 0

            print(f"📚 Processing {total_manga_found} manga...")

            # Process each manga
            for i, (manga_url, manga_title) in enumerate(manga_links, 1):
                try:
                    print(
                        f"\n📖 Processing manga {i}/{total_manga_found}: {manga_title}")
                    print(f"   🔗 URL: {manga_url}")

                    # Create manga crawler instance for this manga and use async context manager
                    async with MangaCrawlerService() as manga_crawler:
                        # Crawl this manga
                        status, title, folder, total_chapters, chapters_info, manga_errors, processing_time = (
                            await manga_crawler.crawl_manga(
                                manga_url=manga_url,
                                max_chapters=max_chapters_per_manga,
                                start_chapter=None,
                                end_chapter=None,
                                custom_headers=custom_headers,
                                delay_between_chapters=delay_between_chapters,
                                image_type=image_type
                            )
                        )

                    # Calculate total images for this manga
                    manga_total_images = sum(len(chapter.images)
                                             for chapter in chapters_info)

                    # Determine manga status
                    if status == CrawlStatus.SUCCESS:
                        manga_status = "success"
                    elif status == CrawlStatus.PARTIAL:
                        manga_status = "partial"
                    else:
                        manga_status = "failed"

                    # Create manga info
                    manga_info = MangaListInfo(
                        manga_url=manga_url,
                        manga_title=title or manga_title,
                        manga_folder=folder,
                        total_chapters=total_chapters,
                        chapters_downloaded=len(
                            [c for c in chapters_info if c.images_count > 0]),
                        total_images_downloaded=manga_total_images,
                        status=manga_status,
                        processing_time_seconds=processing_time,
                        errors=manga_errors
                    )

                    manga_list_results.append(manga_info)
                    manga_processed += 1
                    total_images_downloaded += manga_total_images

                    print(f"   ✅ Completed: {manga_status.upper()}")
                    print(
                        f"   📊 Chapters: {manga_info.chapters_downloaded}/{manga_info.total_chapters}")
                    print(
                        f"   🖼️ Images: {manga_info.total_images_downloaded}")
                    print(f"   ⏱️ Time: {processing_time:.2f}s")

                    # Add delay between manga (except for the last one)
                    if i < total_manga_found and delay_between_manga > 0:
                        print(
                            f"   ⏳ Waiting {delay_between_manga}s before next manga...")
                        await asyncio.sleep(delay_between_manga)

                except Exception as e:
                    error_msg = f"Error processing manga {i} ({manga_title}): {str(e)}"
                    errors.append(error_msg)
                    print(f"   ❌ {error_msg}")

                    # Create failed manga info
                    manga_info = MangaListInfo(
                        manga_url=manga_url,
                        manga_title=manga_title,
                        manga_folder="",
                        total_chapters=0,
                        chapters_downloaded=0,
                        total_images_downloaded=0,
                        status="failed",
                        processing_time_seconds=0,
                        errors=[error_msg]
                    )
                    manga_list_results.append(manga_info)

            # Determine overall status
            successful_manga = len(
                [m for m in manga_list_results if m.status == "success"])
            partial_manga = len(
                [m for m in manga_list_results if m.status == "partial"])

            if successful_manga == total_manga_found:
                overall_status = CrawlStatus.SUCCESS
            elif successful_manga > 0 or partial_manga > 0:
                overall_status = CrawlStatus.PARTIAL
            else:
                overall_status = CrawlStatus.FAILED

            processing_time = time.time() - start_time

            print(f"\n🎉 Manga list crawl completed!")
            print(f"   📊 Status: {overall_status}")
            print(
                f"   📚 Manga processed: {manga_processed}/{total_manga_found}")
            print(f"   🖼️ Total images: {total_images_downloaded}")
            print(f"   ⏱️ Total time: {processing_time:.2f}s")

            return MangaListCrawlResponse(
                status=overall_status,
                list_url=list_url,
                total_manga_found=total_manga_found,
                manga_processed=manga_processed,
                total_images_downloaded=total_images_downloaded,
                manga_list=manga_list_results,
                errors=errors,
                processing_time_seconds=processing_time
            )

        except Exception as e:
            error_msg = f"Critical error in manga list crawl: {str(e)}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")

            processing_time = time.time() - start_time

            return MangaListCrawlResponse(
                status=CrawlStatus.FAILED,
                list_url=list_url,
                total_manga_found=0,
                manga_processed=0,
                total_images_downloaded=0,
                manga_list=[],
                errors=errors,
                processing_time_seconds=processing_time
            )
