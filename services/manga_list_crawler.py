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
from services.existence_checker import ExistenceChecker


class MangaListCrawler:
    """Service for crawling manga list pages and processing all manga found"""

    def __init__(self):
        self.session = None
        self.manga_crawler = MangaCrawlerService()
        self.existence_checker = ExistenceChecker()

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.existence_checker.initialize_wasabi()
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

            print(f"📚 Processing {total_manga_found} manga concurrently...")

            # Create tasks for all manga to process concurrently
            async def process_single_manga(manga_data: Tuple[str, str, int]) -> MangaListInfo:
                """Process a single manga and return its info"""
                manga_url, manga_title, manga_index = manga_data

                try:
                    print(
                        f"🚀 Starting manga {manga_index}/{total_manga_found}: {manga_title}")
                    print(f"   🔗 URL: {manga_url}")

                    # Create manga crawler instance for this manga and use async context manager
                    async with MangaCrawlerService() as manga_crawler:
                        # Crawl this manga
                        # If max_chapters_per_manga is None, crawl all chapters
                        # If it's specified, use it as limit but ensure we start from the beginning
                        if max_chapters_per_manga is None:
                            # Crawl all chapters from beginning to end
                            crawl_max_chapters = None
                            start_chapter = None
                            end_chapter = None
                            print(f"   📚 Crawling ALL chapters (no limit)")
                        else:
                            # Crawl specified number of chapters from the beginning
                            crawl_max_chapters = max_chapters_per_manga
                            start_chapter = None  # Start from first chapter
                            end_chapter = None    # Let the max_chapters limit handle the end
                            print(
                                f"   📚 Crawling first {max_chapters_per_manga} chapters from beginning")

                        status, title, folder, total_chapters, chapters_info, manga_errors, processing_time = (
                            await manga_crawler.crawl_manga(
                                manga_url=manga_url,
                                max_chapters=crawl_max_chapters,
                                start_chapter=start_chapter,
                                end_chapter=end_chapter,
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

                    print(
                        f"   ✅ Completed manga {manga_index}: {manga_status.upper()}")
                    print(
                        f"   📊 Chapters: {manga_info.chapters_downloaded}/{manga_info.total_chapters}")
                    print(
                        f"   🖼️ Images: {manga_info.total_images_downloaded}")
                    print(f"   ⏱️ Time: {processing_time:.2f}s")

                    return manga_info

                except Exception as e:
                    error_msg = f"Error processing manga {manga_index} ({manga_title}): {str(e)}"
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
                    return manga_info

            # Prepare manga data with indices
            manga_data_list = [(url, title, i+1)
                               for i, (url, title) in enumerate(manga_links)]

            # Process all manga concurrently
            manga_tasks = [process_single_manga(
                manga_data) for manga_data in manga_data_list]

            # Wait for all tasks to complete
            print(
                f"🔄 Starting concurrent processing of {len(manga_tasks)} manga...")
            manga_results = await asyncio.gather(*manga_tasks, return_exceptions=True)

            # Process results
            for result in manga_results:
                if isinstance(result, Exception):
                    # Handle any exceptions that weren't caught
                    error_msg = f"Unhandled exception in manga processing: {str(result)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
                else:
                    # Add successful result
                    manga_list_results.append(result)
                    manga_processed += 1
                    total_images_downloaded += result.total_images_downloaded

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

    async def get_manga_list_progress(self, list_url: str, image_type: str = "local") -> dict:
        """
        Get progress information for manga list crawling

        Args:
            list_url: URL of the manga list page
            image_type: Storage type ("local" or "cloud")

        Returns:
            Dictionary containing progress information
        """
        try:
            print(f"🔍 Getting progress for manga list: {list_url}")

            # Extract manga URLs from the list page
            manga_links = await self._extract_manga_urls(list_url)

            if not manga_links:
                return {
                    "list_url": list_url,
                    "image_type": image_type,
                    "total_manga_found": 0,
                    "manga_progress": [],
                    "overall_progress": {
                        "total_manga": 0,
                        "completed_manga": 0,
                        "total_chapters": 0,
                        "total_images": 0
                    }
                }

            # Get progress for each manga
            manga_progress = []
            total_chapters = 0
            total_images = 0
            completed_manga = 0

            for manga_url, manga_title in manga_links:
                try:
                    # Create manga folder path
                    sanitized_title = self._sanitize_folder_name(manga_title)
                    manga_folder = os.path.join('downloads', sanitized_title)

                    # Get progress for this manga
                    progress = await self.existence_checker.get_manga_progress(manga_folder, image_type)

                    manga_info = {
                        "manga_url": manga_url,
                        "manga_title": manga_title,
                        "manga_folder": manga_folder,
                        "progress": progress
                    }

                    manga_progress.append(manga_info)

                    # Update totals
                    total_chapters += progress.get("total_chapters", 0)
                    total_images += progress.get("total_images", 0)
                    if progress.get("total_chapters", 0) > 0:
                        completed_manga += 1

                except Exception as e:
                    print(f"⚠️ Error getting progress for {manga_title}: {str(e)}")
                    manga_progress.append({
                        "manga_url": manga_url,
                        "manga_title": manga_title,
                        "manga_folder": "",
                        "progress": {"error": str(e)}
                    })

            overall_progress = {
                "total_manga": len(manga_links),
                "completed_manga": completed_manga,
                "total_chapters": total_chapters,
                "total_images": total_images
            }

            return {
                "list_url": list_url,
                "image_type": image_type,
                "total_manga_found": len(manga_links),
                "manga_progress": manga_progress,
                "overall_progress": overall_progress
            }

        except Exception as e:
            print(f"❌ Error getting manga list progress: {str(e)}")
            return {
                "list_url": list_url,
                "image_type": image_type,
                "error": str(e),
                "total_manga_found": 0,
                "manga_progress": [],
                "overall_progress": {
                    "total_manga": 0,
                    "completed_manga": 0,
                    "total_chapters": 0,
                    "total_images": 0
                }
            }

    async def get_all_crawled_manga(self, image_type: str = "local") -> dict:
        """
        Get all manga that have been crawled and stored

        Args:
            image_type: Storage type ("local" or "cloud")

        Returns:
            Dictionary containing all crawled manga information
        """
        try:
            print(f"🔍 Getting all crawled manga for image_type: {image_type}")

            if image_type == "local":
                return await self._get_all_local_manga()
            else:
                return await self._get_all_cloud_manga()

        except Exception as e:
            print(f"❌ Error getting all crawled manga: {str(e)}")
            return {
                "image_type": image_type,
                "error": str(e),
                "total_manga": 0,
                "manga_list": []
            }

    async def _get_all_local_manga(self) -> dict:
        """Get all manga stored locally"""
        try:
            downloads_folder = "downloads"
            if not os.path.exists(downloads_folder):
                return {
                    "image_type": "local",
                    "total_manga": 0,
                    "manga_list": []
                }

            manga_list = []

            # Scan downloads folder for manga directories
            for item in os.listdir(downloads_folder):
                manga_folder = os.path.join(downloads_folder, item)

                if os.path.isdir(manga_folder):
                    # Check if this is a manga folder (has chapters or metadata)
                    metadata_file = os.path.join(manga_folder, "manga_metadata.json")
                    has_chapters = any(
                        os.path.isdir(os.path.join(manga_folder, d))
                        for d in os.listdir(manga_folder)
                        if d.startswith("Chapter_")
                    )

                    if os.path.exists(metadata_file) or has_chapters:
                        # Get progress for this manga
                        progress = await self.existence_checker.get_manga_progress(manga_folder, "local")

                        manga_info = {
                            "manga_title": item,
                            "manga_folder": manga_folder,
                            "progress": progress,
                            "has_metadata": os.path.exists(metadata_file),
                            "has_chapters": has_chapters
                        }

                        manga_list.append(manga_info)

            # Sort by manga title
            manga_list.sort(key=lambda x: x["manga_title"])

            # Calculate totals
            total_chapters = sum(m.get("progress", {}).get("total_chapters", 0) for m in manga_list)
            total_images = sum(m.get("progress", {}).get("total_images", 0) for m in manga_list)

            return {
                "image_type": "local",
                "total_manga": len(manga_list),
                "total_chapters": total_chapters,
                "total_images": total_images,
                "manga_list": manga_list
            }

        except Exception as e:
            print(f"❌ Error getting local manga: {str(e)}")
            return {
                "image_type": "local",
                "error": str(e),
                "total_manga": 0,
                "manga_list": []
            }

    async def _get_all_cloud_manga(self) -> dict:
        """Get all manga stored in cloud storage"""
        try:
            if not self.existence_checker.wasabi_service:
                success = await self.existence_checker.initialize_wasabi()
                if not success:
                    return {
                        "image_type": "cloud",
                        "error": "Wasabi service not available",
                        "total_manga": 0,
                        "manga_list": []
                    }

            print(f"🔍 Scanning cloud storage for all manga...")

            # Get all objects with pagination to ensure we get everything
            all_objects = []
            continuation_token = None
            max_keys_per_request = 1000  # Maximum allowed by S3

            while True:
                try:
                    # List objects with pagination
                    if continuation_token:
                        response = self.existence_checker.wasabi_service.s3_client.list_objects_v2(
                            Bucket=self.existence_checker.wasabi_service.bucket_name,
                            MaxKeys=max_keys_per_request,
                            ContinuationToken=continuation_token
                        )
                    else:
                        response = self.existence_checker.wasabi_service.s3_client.list_objects_v2(
                            Bucket=self.existence_checker.wasabi_service.bucket_name,
                            MaxKeys=max_keys_per_request
                        )

                    if 'Contents' in response:
                        batch_objects = [obj['Key'] for obj in response['Contents']]
                        all_objects.extend(batch_objects)
                        print(f"   📦 Retrieved {len(batch_objects)} objects (total: {len(all_objects)})")

                    # Check if there are more objects to retrieve
                    if response.get('IsTruncated', False) and 'NextContinuationToken' in response:
                        continuation_token = response['NextContinuationToken']
                    else:
                        break

                except Exception as e:
                    print(f"⚠️ Error during pagination: {str(e)}")
                    break

            print(f"✅ Total objects retrieved: {len(all_objects)}")

            # Group objects by manga
            manga_groups = {}
            for obj in all_objects:
                # Parse object key: manga_title/Chapter_X/image.jpg
                parts = obj.split('/')
                if len(parts) >= 3 and parts[1].startswith("Chapter_"):
                    manga_title = parts[0]
                    chapter_num = parts[1].replace("Chapter_", "")

                    if manga_title not in manga_groups:
                        manga_groups[manga_title] = {}

                    if chapter_num not in manga_groups[manga_title]:
                        manga_groups[manga_title][chapter_num] = []

                    manga_groups[manga_title][chapter_num].append(parts[2])

            print(f"📚 Found {len(manga_groups)} manga in cloud storage")

            # Convert to manga list format
            manga_list = []
            total_chapters = 0
            total_images = 0

            for manga_title, chapters in manga_groups.items():
                chapter_list = []
                manga_total_images = 0

                # Sort chapters by number
                sorted_chapters = sorted(chapters.items(), key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else 0)

                for chapter_num, images in sorted_chapters:
                    # Filter only image files
                    image_files = [img for img in images if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                    if image_files:
                        # Sort images by number
                        def sort_key(filename):
                            import re
                            match = re.search(r'(\d+)', filename)
                            if match:
                                return int(match.group(1))
                            return 0

                        image_files.sort(key=sort_key)

                        chapter_list.append({
                            "chapter_number": chapter_num,
                            "images": image_files,
                            "total_images": len(image_files)
                        })
                        manga_total_images += len(image_files)

                if chapter_list:
                    manga_info = {
                        "manga_title": manga_title,
                        "manga_folder": f"cloud://{manga_title}",
                        "progress": {
                            "total_chapters": len(chapter_list),
                            "completed_chapters": len(chapter_list),
                            "total_images": manga_total_images,
                            "chapters": {ch["chapter_number"]: ch for ch in chapter_list}
                        },
                        "has_metadata": False,  # Cloud doesn't have local metadata files
                        "has_chapters": len(chapter_list) > 0
                    }

                    manga_list.append(manga_info)
                    total_chapters += len(chapter_list)
                    total_images += manga_total_images

                    print(f"   📖 {manga_title}: {len(chapter_list)} chapters, {manga_total_images} images")

            # Sort by manga title
            manga_list.sort(key=lambda x: x["manga_title"])

            print(f"🎉 Cloud scan completed: {len(manga_list)} manga, {total_chapters} chapters, {total_images} images")

            return {
                "image_type": "cloud",
                "total_manga": len(manga_list),
                "total_chapters": total_chapters,
                "total_images": total_images,
                "manga_list": manga_list
            }

        except Exception as e:
            print(f"❌ Error getting cloud manga: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "image_type": "cloud",
                "error": str(e),
                "total_manga": 0,
                "manga_list": []
            }

    async def get_manga_details(self, manga_title: str, image_type: str = "local") -> dict:
        """
        Get detailed information for a specific manga

        Args:
            manga_title: Title of the manga to get details for
            image_type: Storage type ("local" or "cloud")

        Returns:
            Dictionary containing detailed manga information
        """
        try:
            print(f"🔍 Getting details for manga: {manga_title} (image_type: {image_type})")

            if image_type == "local":
                return await self._get_local_manga_details(manga_title)
            else:
                return await self._get_cloud_manga_details(manga_title)

        except Exception as e:
            print(f"❌ Error getting manga details: {str(e)}")
            return {
                "manga_title": manga_title,
                "image_type": image_type,
                "error": str(e),
                "found": False
            }

    async def _get_local_manga_details(self, manga_title: str) -> dict:
        """Get detailed information for a manga stored locally"""
        try:
            downloads_folder = "downloads"
            manga_folder = os.path.join(downloads_folder, manga_title)

            if not os.path.exists(manga_folder):
                return {
                    "manga_title": manga_title,
                    "image_type": "local",
                    "found": False,
                    "error": "Manga folder not found"
                }

            # Get progress for this manga
            progress = await self.existence_checker.get_manga_progress(manga_folder, "local")

            # Get chapter details
            chapter_details = []
            chapters_data = progress.get("chapters", {})

            for chapter_num, chapter_info in chapters_data.items():
                chapter_details.append({
                    "chapter_number": chapter_num,
                    "total_images": chapter_info.get("total_images", 0),
                    "images": chapter_info.get("images", []),
                    "status": "completed"
                })

            # Sort chapters by number
            chapter_details.sort(key=lambda x: float(x["chapter_number"]) if x["chapter_number"].replace('.', '').isdigit() else 0)

            # Get folder information
            folder_info = {
                "manga_folder": manga_folder,
                "has_metadata": os.path.exists(os.path.join(manga_folder, "manga_metadata.json")),
                "total_size": self._get_folder_size(manga_folder),
                "created_date": self._get_folder_created_date(manga_folder),
                "modified_date": self._get_folder_modified_date(manga_folder)
            }

            return {
                "manga_title": manga_title,
                "image_type": "local",
                "found": True,
                "progress": progress,
                "chapter_details": chapter_details,
                "folder_info": folder_info,
                "summary": {
                    "total_chapters": progress.get("total_chapters", 0),
                    "completed_chapters": progress.get("completed_chapters", 0),
                    "total_images": progress.get("total_images", 0),
                    "average_images_per_chapter": progress.get("total_images", 0) / max(progress.get("total_chapters", 1), 1)
                }
            }

        except Exception as e:
            print(f"❌ Error getting local manga details: {str(e)}")
            return {
                "manga_title": manga_title,
                "image_type": "local",
                "found": False,
                "error": str(e)
            }

    async def _get_cloud_manga_details(self, manga_title: str) -> dict:
        """Get detailed information for a manga stored in cloud storage"""
        try:
            if not self.existence_checker.wasabi_service:
                success = await self.existence_checker.initialize_wasabi()
                if not success:
                    return {
                        "manga_title": manga_title,
                        "image_type": "cloud",
                        "found": False,
                        "error": "Wasabi service not available"
                    }

            # List all objects for this manga
            prefix = f"{manga_title}/"
            all_objects = self.existence_checker.wasabi_service.list_objects(prefix=prefix)

            if not all_objects:
                return {
                    "manga_title": manga_title,
                    "image_type": "cloud",
                    "found": False,
                    "error": "Manga not found in cloud storage"
                }

            # Group objects by chapter
            chapter_groups = {}
            for obj in all_objects:
                parts = obj.split('/')
                if len(parts) >= 3 and parts[1].startswith("Chapter_"):
                    chapter_num = parts[1].replace("Chapter_", "")
                    if chapter_num not in chapter_groups:
                        chapter_groups[chapter_num] = []
                    chapter_groups[chapter_num].append(parts[2])

            # Get chapter details
            chapter_details = []
            total_images = 0

            # Sort chapters by number
            sorted_chapters = sorted(chapter_groups.items(), key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else 0)

            for chapter_num, images in sorted_chapters:
                # Filter only image files
                image_files = [img for img in images if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

                # Sort images by number
                def sort_key(filename):
                    import re
                    match = re.search(r'(\d+)', filename)
                    if match:
                        return int(match.group(1))
                    return 0

                image_files.sort(key=sort_key)

                chapter_details.append({
                    "chapter_number": chapter_num,
                    "total_images": len(image_files),
                    "images": image_files,
                    "status": "completed"
                })

                total_images += len(image_files)

            # Get cloud storage information
            cloud_info = {
                "manga_folder": f"cloud://{manga_title}",
                "total_objects": len(all_objects),
                "bucket_name": self.existence_checker.wasabi_service.bucket_name,
                "endpoint_url": self.existence_checker.wasabi_service.endpoint_url
            }

            return {
                "manga_title": manga_title,
                "image_type": "cloud",
                "found": True,
                "chapter_details": chapter_details,
                "cloud_info": cloud_info,
                "summary": {
                    "total_chapters": len(chapter_details),
                    "completed_chapters": len(chapter_details),
                    "total_images": total_images,
                    "average_images_per_chapter": total_images / max(len(chapter_details), 1)
                }
            }

        except Exception as e:
            print(f"❌ Error getting cloud manga details: {str(e)}")
            return {
                "manga_title": manga_title,
                "image_type": "cloud",
                "found": False,
                "error": str(e)
            }

    def _get_folder_size(self, folder_path: str) -> int:
        """Get total size of a folder in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        except Exception:
            return 0

    def _get_folder_created_date(self, folder_path: str) -> str:
        """Get folder creation date"""
        try:
            stat = os.stat(folder_path)
            return str(stat.st_ctime)
        except Exception:
            return "unknown"

    def _get_folder_modified_date(self, folder_path: str) -> str:
        """Get folder last modified date"""
        try:
            stat = os.stat(folder_path)
            return str(stat.st_mtime)
        except Exception:
            return "unknown"
