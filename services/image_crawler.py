"""
Advanced image crawler service with support for various image loading techniques
"""

import os
import re
import time
import base64
import hashlib
import asyncio
from io import BytesIO
from typing import List, Tuple, Optional, Set
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path

import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from PIL import Image

from models.schemas import ImageInfo, CrawlStatus


class ImageCrawlerService:
    """Advanced image crawler with support for various obfuscation techniques"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.downloaded_urls: Set[str] = set()  # Track downloaded URLs to avoid duplicates

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_domain_folder(self, url: str) -> Tuple[str, str]:
        """
        Extract domain from URL and create folder name

        Args:
            url: Website URL

        Returns:
            Tuple of (domain, folder_path)
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        # Create safe folder name
        folder_name = re.sub(r'[^\w\-_.]', '_', domain)
        folder_path = os.path.join('downloads', folder_name)

        # Create directory if it doesn't exist
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        return domain, folder_path

    def _setup_selenium_driver(self) -> webdriver.Chrome:
        """
        Setup Selenium Chrome driver with optimal settings

        Returns:
            Configured Chrome WebDriver
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # Disable images loading initially to speed up page load
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise Exception(f"Failed to setup Selenium driver: {str(e)}")

    def _extract_images_from_html(self, html_content: str, base_url: str) -> List[str]:
        """
        Extract image URLs from HTML content using BeautifulSoup

        Args:
            html_content: HTML content of the page
            base_url: Base URL for resolving relative URLs

        Returns:
            List of image URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        image_urls = []

        # Standard img tags with multiple lazy loading attributes
        for img in soup.find_all('img'):
            # Try multiple common lazy loading attributes
            src = (img.get('src') or
                   img.get('data-src') or
                   img.get('data-original') or
                   img.get('data-lazy') or
                   img.get('data-retries') or  # Specific to nettruyenvia.com
                   img.get('data-url') or
                   img.get('data-img-src'))

            if src and src.strip() and not src.startswith('data:'):  # Skip base64 images here
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, src.strip())
                image_urls.append(absolute_url)

            # Also check for srcset attributes
            srcset = img.get('srcset')
            if srcset:
                # Parse srcset and extract URLs
                srcset_urls = []
                for src_item in srcset.split(','):
                    src_part = src_item.strip().split(' ')[0]  # Get URL part before size descriptor
                    if src_part:
                        absolute_url = urljoin(base_url, src_part)
                        srcset_urls.append(absolute_url)
                image_urls.extend(srcset_urls)

        # Background images in CSS
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            bg_matches = re.findall(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
            for match in bg_matches:
                absolute_url = urljoin(base_url, match)
                image_urls.append(absolute_url)

        # CSS background images in style tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                bg_matches = re.findall(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style_tag.string)
                for match in bg_matches:
                    absolute_url = urljoin(base_url, match)
                    image_urls.append(absolute_url)

        return list(set(image_urls))  # Remove duplicates

    def _extract_base64_images(self, html_content: str) -> List[Tuple[str, str]]:
        """
        Extract base64 encoded images from HTML

        Args:
            html_content: HTML content of the page

        Returns:
            List of tuples (base64_data, format)
        """
        base64_images = []

        # Find base64 images in src attributes
        base64_pattern = r'data:image/([a-zA-Z]*);base64,([^"\']*)'
        matches = re.findall(base64_pattern, html_content)

        for format_type, base64_data in matches:
            base64_images.append((base64_data, format_type))

        return base64_images

    def _extract_lazy_loaded_images(self, driver: webdriver.Chrome, base_url: str) -> List[str]:
        """
        Extract lazy-loaded images using Selenium

        Args:
            driver: Selenium WebDriver instance
            base_url: Base URL for resolving relative URLs

        Returns:
            List of image URLs
        """
        image_urls = []

        try:
            # Scroll to trigger lazy loading
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait for new content to load
                time.sleep(2)

                # Calculate new scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Extract all images after lazy loading
            img_elements = driver.find_elements(By.TAG_NAME, "img")

            for img in img_elements:
                src = img.get_attribute('src')
                if src and src not in self.downloaded_urls:
                    absolute_url = urljoin(base_url, src)
                    image_urls.append(absolute_url)

            # Check for data-src attributes (common in lazy loading)
            lazy_imgs = driver.find_elements(By.CSS_SELECTOR, "[data-src], [data-original], [data-lazy]")
            for img in lazy_imgs:
                src = img.get_attribute('data-src') or img.get_attribute('data-original') or img.get_attribute('data-lazy')
                if src and src not in self.downloaded_urls:
                    absolute_url = urljoin(base_url, src)
                    image_urls.append(absolute_url)

        except Exception as e:
            print(f"Error extracting lazy-loaded images: {str(e)}")

        return list(set(image_urls))

    async def _download_image(self, url: str, folder_path: str, session: aiohttp.ClientSession, base_url: str = None) -> Optional[ImageInfo]:
        """
        Download a single image from URL with anti-blocking measures

        Args:
            url: Image URL
            folder_path: Local folder to save the image
            session: aiohttp session for downloading
            base_url: Base URL of the original page (for Referer header)

        Returns:
            ImageInfo object if successful, None otherwise
        """
        try:
            # Skip if already downloaded
            if url in self.downloaded_urls:
                return None

            # Try multiple strategies to bypass blocking
            strategies = [
                # Strategy 1: Standard headers with proper referer
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': base_url or url,
                    'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site'
                },
                # Strategy 2: Mobile user agent
                {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                    'Referer': base_url or url,
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
                },
                # Strategy 3: Different browser (Firefox)
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Referer': base_url or url,
                    'Accept': 'image/webp,*/*'
                }
            ]

            for strategy_idx, headers in enumerate(strategies):
                try:
                    print(f"Trying strategy {strategy_idx + 1} for {url}")

                    # Add random delay to avoid rate limiting
                    if strategy_idx > 0:
                        await asyncio.sleep(1)

                    async with session.get(url, headers=headers, timeout=30, allow_redirects=True) as response:
                        print(f"Response status: {response.status} for {url}")

                        if response.status == 200:
                            content = await response.read()

                            # Check if content is actually an image (not error page)
                            if len(content) < 1000:  # Very small content might be error page
                                content_str = content.decode('utf-8', errors='ignore').lower()
                                if any(error_text in content_str for error_text in ['blocked', 'access denied', 'forbidden', 'error']):
                                    print(f"Content appears to be error page for {url}")
                                    continue

                            # Validate image content
                            try:
                                with Image.open(BytesIO(content)) as img:
                                    # If we can open it as image, it's valid
                                    width, height = img.size
                                    format_type = img.format.lower() if img.format else 'unknown'
                            except Exception as img_error:
                                print(f"Content is not a valid image for {url}: {img_error}")
                                continue

                            # Generate filename from URL or hash
                            parsed_url = urlparse(url)
                            filename = os.path.basename(unquote(parsed_url.path))

                            if not filename or '.' not in filename:
                                # Generate filename from URL hash
                                url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
                                content_type = response.headers.get('content-type', '')

                                if 'jpeg' in content_type or 'jpg' in content_type:
                                    filename = f"{url_hash}.jpg"
                                elif 'png' in content_type:
                                    filename = f"{url_hash}.png"
                                elif 'gif' in content_type:
                                    filename = f"{url_hash}.gif"
                                elif 'webp' in content_type:
                                    filename = f"{url_hash}.webp"
                                else:
                                    filename = f"{url_hash}.jpg"

                            filepath = os.path.join(folder_path, filename)

                            # Save image
                            async with aiofiles.open(filepath, 'wb') as f:
                                await f.write(content)

                            self.downloaded_urls.add(url)

                            print(f"✅ Successfully downloaded {url} using strategy {strategy_idx + 1}")

                            return ImageInfo(
                                original_url=url,
                                local_path=filepath,
                                filename=filename,
                                size_bytes=len(content),
                                width=width,
                                height=height,
                                format=format_type
                            )

                        elif response.status == 403:
                            print(f"403 Forbidden for {url}, trying next strategy...")
                            continue
                        elif response.status == 429:
                            print(f"Rate limited for {url}, waiting before retry...")
                            await asyncio.sleep(2)
                            continue
                        else:
                            print(f"HTTP {response.status} for {url}")

                except asyncio.TimeoutError:
                    print(f"Timeout for {url} with strategy {strategy_idx + 1}")
                    continue
                except Exception as strategy_error:
                    print(f"Strategy {strategy_idx + 1} failed for {url}: {str(strategy_error)}")
                    continue

            print(f"❌ All strategies failed for {url}")
            return None

        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return None

    async def _save_base64_image(self, base64_data: str, format_type: str, folder_path: str, index: int) -> Optional[ImageInfo]:
        """
        Save base64 encoded image to disk

        Args:
            base64_data: Base64 encoded image data
            format_type: Image format (jpg, png, etc.)
            folder_path: Local folder to save the image
            index: Index for filename generation

        Returns:
            ImageInfo object if successful, None otherwise
        """
        try:
            # Decode base64 data
            image_data = base64.b64decode(base64_data)

            # Generate filename
            filename = f"base64_image_{index}.{format_type}"
            filepath = os.path.join(folder_path, filename)

            # Save image
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(image_data)

            # Get image info
            try:
                with Image.open(BytesIO(image_data)) as img:
                    width, height = img.size
            except:
                width = height = None

            return ImageInfo(
                original_url=f"data:image/{format_type};base64,{base64_data[:50]}...",
                local_path=filepath,
                filename=filename,
                size_bytes=len(image_data),
                width=width,
                height=height,
                format=format_type
            )

        except Exception as e:
            print(f"Error saving base64 image: {str(e)}")
            return None

    async def crawl_images(
        self,
        url: str,
        max_images: int = 100,
        include_base64: bool = True,
        use_selenium: bool = True,
        custom_headers: Optional[dict] = None
    ) -> Tuple[CrawlStatus, str, str, int, List[ImageInfo], List[str], float]:
        """
        Main method to crawl images from a website

        Args:
            url: Website URL to crawl
            max_images: Maximum number of images to download
            include_base64: Whether to include base64 encoded images
            use_selenium: Whether to use Selenium for JavaScript rendering
            custom_headers: Custom HTTP headers

        Returns:
            Tuple of (status, domain, folder_path, total_found, images_info, errors, processing_time)
        """
        start_time = time.time()
        errors = []
        images_info = []

        try:
            # Setup
            domain, folder_path = self._get_domain_folder(url)

            # Initialize session
            if not self.session:
                self.session = aiohttp.ClientSession()

            image_urls = []
            base64_images = []

            # Method 1: Basic HTTP request with BeautifulSoup
            try:
                headers = custom_headers or {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }

                async with self.session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        html_content = await response.text()

                        # Extract regular images
                        basic_images = self._extract_images_from_html(html_content, url)
                        image_urls.extend(basic_images)

                        # Extract base64 images if requested
                        if include_base64:
                            base64_images = self._extract_base64_images(html_content)

            except Exception as e:
                errors.append(f"Basic crawling failed: {str(e)}")

            # Method 2: Selenium for JavaScript-rendered content
            if use_selenium:
                driver = None
                try:
                    driver = self._setup_selenium_driver()
                    driver.get(url)

                    # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    # Extract lazy-loaded images
                    selenium_images = self._extract_lazy_loaded_images(driver, url)
                    image_urls.extend(selenium_images)

                    # Get final HTML after JavaScript execution
                    final_html = driver.page_source
                    js_images = self._extract_images_from_html(final_html, url)
                    image_urls.extend(js_images)

                    if include_base64:
                        js_base64_images = self._extract_base64_images(final_html)
                        base64_images.extend(js_base64_images)

                except Exception as e:
                    errors.append(f"Selenium crawling failed: {str(e)}")
                finally:
                    if driver:
                        driver.quit()

            # Remove duplicates
            image_urls = list(set(image_urls))
            total_found = len(image_urls) + len(base64_images)

            # Limit images if specified
            if max_images > 0:
                image_urls = image_urls[:max_images]
                base64_images = base64_images[:max(0, max_images - len(image_urls))]

            # Download regular images concurrently
            download_tasks = []
            for img_url in image_urls:
                task = self._download_image(img_url, folder_path, self.session, url)
                download_tasks.append(task)

            # Execute downloads concurrently
            if download_tasks:
                download_results = await asyncio.gather(*download_tasks, return_exceptions=True)

                for result in download_results:
                    if isinstance(result, ImageInfo):
                        images_info.append(result)
                    elif isinstance(result, Exception):
                        errors.append(f"Download error: {str(result)}")

            # Save base64 images
            for i, (base64_data, format_type) in enumerate(base64_images):
                base64_info = await self._save_base64_image(base64_data, format_type, folder_path, i)
                if base64_info:
                    images_info.append(base64_info)

            # Determine status
            if len(images_info) == 0:
                status = CrawlStatus.FAILED
            elif len(errors) > 0:
                status = CrawlStatus.PARTIAL
            else:
                status = CrawlStatus.SUCCESS

            processing_time = time.time() - start_time

            return status, domain, folder_path, total_found, images_info, errors, processing_time

        except Exception as e:
            errors.append(f"Critical error: {str(e)}")
            processing_time = time.time() - start_time
            return CrawlStatus.FAILED, "", "", 0, [], errors, processing_time
