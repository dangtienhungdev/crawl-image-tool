#!/usr/bin/env python3
"""
Debug script for manga list URL extraction
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin


async def debug_manga_extraction():
    """Debug manga URL extraction from list page"""

    list_url = "https://nettruyenvia.com/?page=637"

    # Default headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    async with aiohttp.ClientSession() as session:
        try:
            print(f"🔍 Fetching: {list_url}")
            async with session.get(list_url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"❌ Failed to fetch: HTTP {response.status}")
                    return

                html_content = await response.text()
                print(f"✅ HTML content length: {len(html_content)} characters")

        except Exception as e:
            print(f"❌ Error fetching: {str(e)}")
            return

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Test different selectors
    selectors = [
        'a[href*="/truyen-tranh/"]',
        '.manga-item a',
        '.comic-item a',
        '.story-item a',
        'a[title*="Truyện tranh"]',
        '.item a',
        '.comic a',
        'a[href*="truyen-tranh"]'
    ]

    print(f"\n🔍 Testing selectors:")
    for selector in selectors:
        links = soup.select(selector)
        print(f"   {selector}: {len(links)} links found")

        if len(links) > 0:
            print(f"   Sample links:")
            for i, link in enumerate(links[:3]):
                href = link.get('href', '')
                title = link.get('title', '') or link.get_text(strip=True)
                print(f"     {i+1}. {title} -> {href}")

    # Look for any links with /truyen-tranh/
    print(f"\n🔍 All links containing '/truyen-tranh/':")
    all_links = soup.find_all('a', href=True)
    manga_links = []

    for link in all_links:
        href = link.get('href', '')
        if '/truyen-tranh/' in href:
            title = link.get('title', '') or link.get_text(strip=True)
            manga_links.append((href, title))

    print(f"   Found {len(manga_links)} manga links")
    for i, (href, title) in enumerate(manga_links[:10]):
        print(f"   {i+1}. {title} -> {href}")


if __name__ == "__main__":
    asyncio.run(debug_manga_extraction())
