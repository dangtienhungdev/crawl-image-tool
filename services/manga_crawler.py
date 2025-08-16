"""
Manga crawler service for downloading entire manga series with all chapters
"""

import os
import re
import time
import asyncio
from typing import List, Tuple, Optional
from urllib.parse import urljoin, urlparse
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from services.image_crawler import ImageCrawlerService
from models.schemas import ChapterInfo, CrawlStatus, ImageInfo


class MangaCrawlerService:
    """Service for crawling entire manga series with all chapters"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.image_crawler = ImageCrawlerService()
        self.wasabi_service = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.image_crawler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        await self.image_crawler.__aexit__(exc_type, exc_val, exc_tb)

    def _sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize folder name by removing invalid characters

        Args:
            name: Original name

        Returns:
            Sanitized folder name
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^\w\-_. ]', '_', name)
        # Replace multiple spaces/underscores with single underscore
        sanitized = re.sub(r'[_\s]+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized

    def _extract_manga_title(self, html_content: str) -> str:
        """
        Extract manga title from HTML content

        Args:
            html_content: HTML content of the manga page

        Returns:
            Manga title
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Try multiple selectors for different manga sites
        title_selectors = [
            'h1.title-detail',  # NetTruyenVia
            'h1.manga-title',
            'h1.entry-title',
            '.manga-info h1',
            '.detail-info h1',
            'h1',
            'title'
        ]

        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text(strip=True)
                if title and len(title) > 3:  # Valid title
                    return title

        return "Unknown_Manga"

    async def _get_chapter_list(self, manga_url: str, custom_headers: Optional[dict] = None) -> List[Tuple[str, str, str]]:
        """
        Get list of all chapters from manga page using direct API call

        Args:
            manga_url: URL of the manga series page
            custom_headers: Custom HTTP headers

        Returns:
            List of tuples (chapter_number, chapter_title, chapter_url)
        """
        print(f"🔍 Getting chapter list from: {manga_url}")

        try:
            # Try direct API call first (most efficient)
            chapters = await self._get_chapter_list_with_api(manga_url, custom_headers)

            if chapters:
                print(
                    f"✅ Found {len(chapters)} chapters using direct API call")
                return chapters
            else:
                print("⚠️ No chapters found with API, trying HTTP method...")
                return await self._get_chapter_list_with_http(manga_url, custom_headers)

        except Exception as e:
            print(f"❌ Error getting chapter list with API: {str(e)}")
            print("🔄 Falling back to HTTP method...")
            return await self._get_chapter_list_with_http(manga_url, custom_headers)

    async def _get_chapter_list_with_api(self, manga_url: str, custom_headers: Optional[dict] = None) -> List[Tuple[str, str, str]]:
        """
        Get chapter list using direct API call to ComicService.asmx/ChapterList
        """
        try:
            # Extract manga slug from URL
            # URL format: https://nettruyenvia.com/truyen-tranh/manga-slug
            manga_slug = manga_url.rstrip('/').split('/')[-1]

            # API endpoint
            api_url = f"https://nettruyenvia.com/Comic/Services/ComicService.asmx/ChapterList?slug={manga_slug}"

            print(f"🔗 Calling API: {api_url}")

            headers = custom_headers or {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': manga_url,
                'X-Requested-With': 'XMLHttpRequest'
            }

            async with self.session.get(api_url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"❌ API request failed: HTTP {response.status}")
                    return []

                try:
                    api_data = await response.json()
                except Exception as e:
                    print(f"❌ Failed to parse API response as JSON: {str(e)}")
                    return []

                # Parse API response
                chapters = []

                if 'data' in api_data and isinstance(api_data['data'], list):
                    print(f"📊 API returned {len(api_data['data'])} chapters")

                    for chapter_data in api_data['data']:
                        try:
                            chapter_num = str(
                                chapter_data.get('chapter_num', ''))
                            chapter_name = chapter_data.get(
                                'chapter_name', f'Chapter {chapter_num}')
                            chapter_slug = chapter_data.get('chapter_slug', '')

                            # Construct chapter URL
                            chapter_url = f"{manga_url.rstrip('/')}/{chapter_slug}"

                            if chapter_num and chapter_url:
                                chapters.append(
                                    (chapter_num, chapter_name, chapter_url))

                        except Exception as e:
                            print(f"⚠️ Error parsing chapter data: {str(e)}")
                            continue

                    # Sort chapters by chapter number (ascending order)
                    try:
                        chapters.sort(key=lambda x: float(
                            x[0]) if x[0].replace('.', '').isdigit() else 0)
                    except Exception as e:
                        print(f"⚠️ Error sorting chapters: {str(e)}")

                    print(
                        f"✅ Successfully parsed {len(chapters)} chapters from API")
                    return chapters

                else:
                    print("❌ Invalid API response format")
                    return []

        except Exception as e:
            print(f"❌ Error in API chapter extraction: {str(e)}")
            return []

    async def _get_chapter_list_with_selenium(self, manga_url: str, custom_headers: Optional[dict] = None) -> List[Tuple[str, str, str]]:
        """
        Get chapter list using Selenium to handle "xem thêm" button
        """
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Add custom headers if provided
            if custom_headers:
                for key, value in custom_headers.items():
                    chrome_options.add_argument(f'--header={key}: {value}')

            # Initialize WebDriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            print(f"🌐 Loading page: {manga_url}")
            driver.get(manga_url)

            # Wait for page to load
            await asyncio.sleep(3)

            # Try to click "xem thêm" button multiple times
            max_attempts = 10
            attempt = 0

            while attempt < max_attempts:
                attempt += 1
                print(
                    f"🔄 Attempt {attempt}/{max_attempts}: Looking for 'xem thêm' button...")

                # Try different selectors for "xem thêm" button
                button_selectors = [
                    "//button[contains(text(), 'xem thêm')]",
                    "//button[contains(text(), 'Xem thêm')]",
                    "//button[contains(text(), 'Xem Thêm')]",
                    "//a[contains(text(), 'xem thêm')]",
                    "//a[contains(text(), 'Xem thêm')]",
                    "//a[contains(text(), 'Xem Thêm')]",
                    "//button[contains(@class, 'load-more')]",
                    "//button[contains(@class, 'show-more')]",
                    "//a[contains(@class, 'load-more')]",
                    "//a[contains(@class, 'show-more')]",
                    "//button[contains(@id, 'load-more')]",
                    "//button[contains(@id, 'show-more')]",
                    ".load-more",
                    ".show-more",
                    "#load-more",
                    "#show-more"
                ]

                button_found = False
                for selector in button_selectors:
                    try:
                        if selector.startswith("//"):
                            # XPath selector
                            button = driver.find_element(By.XPATH, selector)
                        else:
                            # CSS selector
                            button = driver.find_element(
                                By.CSS_SELECTOR, selector)

                        if button.is_displayed() and button.is_enabled():
                            print(
                                f"✅ Found 'xem thêm' button with selector: {selector}")
                            driver.execute_script(
                                "arguments[0].click();", button)
                            button_found = True
                            break
                    except Exception as e:
                        continue

                if not button_found:
                    print("ℹ️ No 'xem thêm' button found, chapters may be fully loaded")
                    break

                # Wait for new content to load
                await asyncio.sleep(2)

                # Check if we've reached the end (no more chapters to load)
                try:
                    # Look for indicators that all chapters are loaded
                    end_indicators = [
                        "//div[contains(text(), 'Không còn chapter nào')]",
                        "//div[contains(text(), 'No more chapters')]",
                        "//div[contains(text(), 'End of chapters')]"
                    ]

                    for indicator in end_indicators:
                        try:
                            element = driver.find_element(By.XPATH, indicator)
                            if element.is_displayed():
                                print("🏁 Reached end of chapters")
                                break
                        except:
                            continue
                except:
                    pass

            # Extract all chapter links from the fully loaded page
            print("📖 Extracting chapter links from fully loaded page...")

            # Get the final HTML content
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            chapters = []

            # NetTruyenVia specific selectors
            chapter_links = soup.select('.list-chapter .row .chapter a')

            if not chapter_links:
                # Try alternative selectors
                chapter_links = soup.select(
                    '.chapter-list a, .chapters a, .manga-chapters a, .list-chapter a')

            print(f"🔍 Found {len(chapter_links)} chapter links")

            for link in chapter_links:
                chapter_url = link.get('href')
                if chapter_url:
                    # Make absolute URL
                    chapter_url = urljoin(manga_url, chapter_url)

                    # Extract chapter number and title
                    chapter_text = link.get_text(strip=True)

                    # Try to extract chapter number
                    chapter_match = re.search(
                        r'chapter\s*(\d+(?:\.\d+)?)', chapter_text, re.IGNORECASE)
                    if chapter_match:
                        chapter_number = chapter_match.group(1)
                    else:
                        # Fallback: use the order in list
                        chapter_number = str(len(chapters) + 1)

                    chapters.append(
                        (chapter_number, chapter_text, chapter_url))

            # Reverse to get chapters in ascending order (usually they're listed in descending order)
            chapters.reverse()

            return chapters

        except Exception as e:
            print(f"❌ Error in Selenium chapter extraction: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()

    async def _get_chapter_list_with_http(self, manga_url: str, custom_headers: Optional[dict] = None) -> List[Tuple[str, str, str]]:
        """
        Get chapter list using HTTP request (fallback method)
        """
        headers = custom_headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            async with self.session.get(manga_url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to fetch manga page: HTTP {response.status}")

                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                chapters = []

                # NetTruyenVia specific selectors
                chapter_links = soup.select('.list-chapter .row .chapter a')

                if not chapter_links:
                    # Try alternative selectors
                    chapter_links = soup.select(
                        '.chapter-list a, .chapters a, .manga-chapters a')

                for link in chapter_links:
                    chapter_url = link.get('href')
                    if chapter_url:
                        # Make absolute URL
                        chapter_url = urljoin(manga_url, chapter_url)

                        # Extract chapter number and title
                        chapter_text = link.get_text(strip=True)

                        # Try to extract chapter number
                        chapter_match = re.search(
                            r'chapter\s*(\d+(?:\.\d+)?)', chapter_text, re.IGNORECASE)
                        if chapter_match:
                            chapter_number = chapter_match.group(1)
                        else:
                            # Fallback: use the order in list
                            chapter_number = str(len(chapters) + 1)

                        chapters.append(
                            (chapter_number, chapter_text, chapter_url))

                # Reverse to get chapters in ascending order (usually they're listed in descending order)
                chapters.reverse()

                print(f"📖 Found {len(chapters)} chapters with HTTP method")
                return chapters

        except Exception as e:
            print(f"❌ Error getting chapter list with HTTP: {str(e)}")
            return []

    async def _get_chapter_images(self, chapter_url: str, custom_headers: Optional[dict] = None) -> List[str]:
        """
        Get all image URLs from a chapter page

        Args:
            chapter_url: URL of the chapter page
            custom_headers: Custom HTTP headers

        Returns:
            List of image URLs
        """
        headers = custom_headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': chapter_url
        }

        try:
            # Try basic HTTP request first
            async with self.session.get(chapter_url, headers=headers) as response:
                if response.status == 200:
                    html_content = await response.text()
                    image_urls = self._extract_chapter_images_from_html(
                        html_content, chapter_url)

                    if image_urls:
                        return image_urls

            # If no images found, try with Selenium (for JavaScript-heavy sites)
            return await self._get_chapter_images_with_selenium(chapter_url)

        except Exception as e:
            print(f"Error getting chapter images: {str(e)}")
            return []

    def _extract_chapter_images_from_html(self, html_content: str, base_url: str) -> List[str]:
        """
        Extract image URLs from chapter HTML content

        Args:
            html_content: HTML content of the chapter
            base_url: Base URL for resolving relative URLs

        Returns:
            List of image URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        image_urls = []

        # NetTruyenVia specific selectors
        img_selectors = [
            '.reading-detail .page-chapter img',  # NetTruyenVia
            '.chapter-content img',
            '.manga-content img',
            '.reader-content img',
            '.chapter img',
            'img[data-src]',
            'img[src]'
        ]

        for selector in img_selectors:
            images = soup.select(selector)
            for img in images:
                # Try multiple attributes for image source
                src = (img.get('data-src') or
                       img.get('data-original') or
                       img.get('src') or
                       img.get('data-lazy'))

                if src and src.strip() and not src.startswith('data:'):
                    # Convert to absolute URL
                    absolute_url = urljoin(base_url, src.strip())
                    # Filter out non-chapter images (ads, icons, etc.)
                    if self._is_chapter_image(absolute_url):
                        image_urls.append(absolute_url)

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in image_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

    def _is_chapter_image(self, url: str) -> bool:
        """
        Check if URL is likely a chapter image (not ad or icon)

        Args:
            url: Image URL to check

        Returns:
            True if likely a chapter image
        """
        url_lower = url.lower()

        # Skip common ad/icon patterns
        skip_patterns = [
            'ads', 'banner', 'icon', 'logo', 'avatar', 'thumb-default',
            'facebook', 'twitter', 'social', 'button'
        ]

        for pattern in skip_patterns:
            if pattern in url_lower:
                return False

        # Accept common image extensions
        return any(url_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])

    async def _get_chapter_images_with_selenium(self, chapter_url: str) -> List[str]:
        """
        Get chapter images using Selenium for JavaScript-heavy pages

        Args:
            chapter_url: URL of the chapter page

        Returns:
            List of image URLs
        """
        driver = None
        try:
            # Setup Chrome driver
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(chapter_url)

            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "img"))
            )

            # Scroll to load lazy images
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Get final HTML
            html_content = driver.page_source
            return self._extract_chapter_images_from_html(html_content, chapter_url)

        except Exception as e:
            print(f"Selenium error for chapter {chapter_url}: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()

    async def _download_chapter(
        self,
        chapter_number: str,
        chapter_title: str,
        chapter_url: str,
        manga_folder: str,
        custom_headers: Optional[dict] = None,
        image_type: str = "local"
    ) -> ChapterInfo:
        """
        Download all images from a single chapter

        Args:
            chapter_number: Chapter number
            chapter_title: Chapter title
            chapter_url: Chapter URL
            manga_folder: Base manga folder
            custom_headers: Custom HTTP headers

        Returns:
            ChapterInfo with download results
        """
        start_time = time.time()
        chapter_folder = os.path.join(
            manga_folder, f"Chapter_{chapter_number}")

        # Only create local folder if not using cloud storage
        if image_type != "cloud":
            Path(chapter_folder).mkdir(parents=True, exist_ok=True)

        print(f"📖 Processing Chapter {chapter_number}: {chapter_title}")

        try:
            # Get chapter images
            image_urls = await self._get_chapter_images(chapter_url, custom_headers)

            if not image_urls:
                return ChapterInfo(
                    chapter_number=chapter_number,
                    chapter_title=chapter_title,
                    chapter_url=chapter_url,
                    images_count=0,
                    images=[],
                    errors=["No images found in chapter"],
                    processing_time_seconds=time.time() - start_time
                )

            print(f"   Found {len(image_urls)} images")

            # Download images
            downloaded_images = []
            errors = []

            for i, img_url in enumerate(image_urls, 1):
                try:
                    # Generate sequential filename
                    filename = f"{i:03d}.jpg"  # 001.jpg, 002.jpg, etc.

                    # Use the enhanced image crawler to download
                    image_info = await self.image_crawler._download_image(
                        url=img_url,
                        folder_path=chapter_folder,
                        session=self.session,
                        base_url=chapter_url,  # Use chapter URL as referer
                        wasabi_service=self.wasabi_service if hasattr(
                            self, 'wasabi_service') else None,
                        image_type=image_type,
                        manga_folder_path=manga_folder  # Pass manga folder for proper S3 structure
                    )

                    if image_info:
                        # Handle file renaming based on storage type
                        if image_type == "cloud":
                            # For cloud storage, just update the filename in the ImageInfo
                            # No need to rename local files since they don't exist
                            image_info.filename = filename
                            print(
                                f"   ✅ Downloaded {i}/{len(image_urls)}: {filename} (cloud)")
                        else:
                            # For local storage, rename the actual file
                            old_path = image_info.local_path
                            new_path = os.path.join(chapter_folder, filename)

                            if old_path != new_path:
                                os.rename(old_path, new_path)
                                image_info.local_path = new_path
                                image_info.filename = filename

                            print(
                                f"   ✅ Downloaded {i}/{len(image_urls)}: {filename} (local)")

                        downloaded_images.append(image_info)
                    else:
                        errors.append(
                            f"Failed to download image {i}: {img_url}")
                        print(f"   ❌ Failed {i}/{len(image_urls)}: {img_url}")

                except Exception as e:
                    error_msg = f"Error downloading image {i}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   ❌ Error {i}/{len(image_urls)}: {str(e)}")

            processing_time = time.time() - start_time
            print(
                f"   ⏱️ Chapter completed in {processing_time:.2f}s ({len(downloaded_images)}/{len(image_urls)} images)")

            return ChapterInfo(
                chapter_number=chapter_number,
                chapter_title=chapter_title,
                chapter_url=chapter_url,
                images_count=len(downloaded_images),
                images=downloaded_images,
                errors=errors,
                processing_time_seconds=processing_time
            )

        except Exception as e:
            error_msg = f"Critical error processing chapter {chapter_number}: {str(e)}"
            print(f"   ❌ {error_msg}")

            return ChapterInfo(
                chapter_number=chapter_number,
                chapter_title=chapter_title,
                chapter_url=chapter_url,
                images_count=0,
                images=[],
                errors=[error_msg],
                processing_time_seconds=time.time() - start_time
            )

    async def crawl_manga(
        self,
        manga_url: str,
        max_chapters: Optional[int] = None,
        start_chapter: Optional[int] = None,
        end_chapter: Optional[int] = None,
        custom_headers: Optional[dict] = None,
        delay_between_chapters: float = 2.0,
        image_type: str = "local"
    ) -> Tuple[CrawlStatus, str, str, int, List[ChapterInfo], List[str], float]:
        """
        Crawl entire manga series

        Args:
            manga_url: URL of the manga series page
            max_chapters: Maximum chapters to download (None for all)
            start_chapter: Chapter to start from
            end_chapter: Chapter to end at (None for last)
            custom_headers: Custom HTTP headers
            delay_between_chapters: Delay between chapter downloads

        Returns:
            Tuple of (status, manga_title, manga_folder, total_chapters, chapters_info, errors, processing_time)
        """
        start_time = time.time()
        errors = []

        try:
            print(f"🚀 Starting manga crawl: {manga_url}")

            # Initialize Wasabi service if cloud storage is requested
            if image_type == "cloud":
                try:
                    from services.wasabi_service import WasabiService
                    self.wasabi_service = WasabiService()
                    print("☁️ Cloud storage (Wasabi S3) enabled for manga crawl")
                except Exception as e:
                    errors.append(
                        f"Failed to initialize Wasabi service: {str(e)}")
                    print(f"⚠️ Falling back to local storage: {str(e)}")
                    image_type = "local"

            # Get manga info and chapter list
            headers = custom_headers or {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            async with self.session.get(manga_url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to access manga page: HTTP {response.status}")

                html_content = await response.text()
                manga_title = self._extract_manga_title(html_content)

            print(f"📚 Manga: {manga_title}")

            # Create manga folder (only for local storage)
            sanitized_title = self._sanitize_folder_name(manga_title)
            manga_folder = os.path.join('downloads', sanitized_title)

            # Only create local folder if not using cloud storage
            if image_type != "cloud":
                Path(manga_folder).mkdir(parents=True, exist_ok=True)
                print(f"📁 Created local folder: {manga_folder}")
            else:
                print(f"☁️ Cloud storage mode: No local folder created")

            # Get chapter list
            all_chapters = await self._get_chapter_list(manga_url, custom_headers)

            if not all_chapters:
                return CrawlStatus.FAILED, manga_title, manga_folder, 0, [], ["No chapters found"], time.time() - start_time

            # Debug: Print first few chapters to understand the format
            print(f"📋 Sample chapters found:")
            for i, (ch_num, ch_title, ch_url) in enumerate(all_chapters[:5]):
                print(f"   {i+1}. Chapter {ch_num}: {ch_title}")

            # Extract actual chapter numbers to understand the range
            actual_chapter_numbers = []
            for chapter_num, _, _ in all_chapters:
                try:
                    actual_chapter_numbers.append(float(chapter_num))
                except ValueError:
                    pass

            # Determine if user wants all chapters (simple case)
            original_start_chapter = start_chapter
            original_end_chapter = end_chapter

            if actual_chapter_numbers:
                min_chapter = min(actual_chapter_numbers)
                max_chapter = max(actual_chapter_numbers)
                print(
                    f"📋 Available chapter range: {min_chapter} to {max_chapter}")

            # Filter chapters based on range
            filtered_chapters = []

            # If no specific filtering requested, include all chapters
            if original_start_chapter is None and original_end_chapter is None:
                print(
                    f"💡 No chapter range specified - including all {len(all_chapters)} chapters")
                filtered_chapters = all_chapters[:]
            else:
                # Set defaults for filtering
                if start_chapter is None and actual_chapter_numbers:
                    start_chapter = min(actual_chapter_numbers)
                    print(f"💡 Auto-set start_chapter to {start_chapter}")
                elif start_chapter is None:
                    start_chapter = 1

                # Check if requested range is valid
                if actual_chapter_numbers and (start_chapter > max(actual_chapter_numbers) or (end_chapter and end_chapter < min(actual_chapter_numbers))):
                    print(
                        f"⚠️ Requested range ({start_chapter}-{end_chapter or 'end'}) is outside available range")
                    print(f"💡 Including all available chapters instead")
                    filtered_chapters = all_chapters[:]
                else:
                    # Apply normal filtering
                    for chapter_num, chapter_title, chapter_url in all_chapters:
                        try:
                            num = float(chapter_num)
                            if num >= start_chapter:
                                if end_chapter is None or num <= end_chapter:
                                    filtered_chapters.append(
                                        (chapter_num, chapter_title, chapter_url))
                        except ValueError:
                            # If chapter number is not numeric, include it
                            print(f"   ⚠️ Non-numeric chapter: {chapter_num}")
                            filtered_chapters.append(
                                (chapter_num, chapter_title, chapter_url))

            print(
                f"📋 After filtering: {len(filtered_chapters)} chapters will be processed")

            # Limit chapters if specified (but ignore max_chapters=0)
            if max_chapters and max_chapters > 0:
                filtered_chapters = filtered_chapters[:max_chapters]
                print(f"📋 Limited to first {max_chapters} chapters")

            print(
                f"📋 Processing {len(filtered_chapters)} chapters (out of {len(all_chapters)} total)")

            # Download chapters
            downloaded_chapters = []

            for i, (chapter_num, chapter_title, chapter_url) in enumerate(filtered_chapters, 1):
                print(
                    f"\n📖 [{i}/{len(filtered_chapters)}] Starting Chapter {chapter_num}")

                chapter_info = await self._download_chapter(
                    chapter_number=chapter_num,
                    chapter_title=chapter_title,
                    chapter_url=chapter_url,
                    manga_folder=manga_folder,
                    custom_headers=custom_headers,
                    image_type=image_type
                )

                downloaded_chapters.append(chapter_info)

                # Add delay between chapters to avoid overwhelming the server
                if i < len(filtered_chapters) and delay_between_chapters > 0:
                    print(
                        f"   ⏸️ Waiting {delay_between_chapters}s before next chapter...")
                    await asyncio.sleep(delay_between_chapters)

            # Calculate statistics
            total_images = sum(len(ch.images) for ch in downloaded_chapters)
            successful_chapters = sum(
                1 for ch in downloaded_chapters if ch.images_count > 0)

            # Determine status
            if successful_chapters == 0:
                status = CrawlStatus.FAILED
            elif successful_chapters < len(downloaded_chapters):
                status = CrawlStatus.PARTIAL
            else:
                status = CrawlStatus.SUCCESS

            processing_time = time.time() - start_time

            print(f"\n🎉 Manga crawl completed!")
            print(f"   📊 Status: {status}")
            print(
                f"   📚 Chapters: {successful_chapters}/{len(downloaded_chapters)}")
            print(f"   🖼️ Total images: {total_images}")
            print(f"   ⏱️ Total time: {processing_time:.2f}s")

            return status, manga_title, manga_folder, len(all_chapters), downloaded_chapters, errors, processing_time

        except Exception as e:
            error_msg = f"Critical error in manga crawl: {str(e)}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")

            return CrawlStatus.FAILED, "Unknown", "", 0, [], errors, time.time() - start_time
