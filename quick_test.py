"""
Quick test for the enhanced image crawler
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.image_crawler import ImageCrawlerService


async def test_crawler():
    """Quick test of the image crawler service"""
    print("🚀 Testing Enhanced Image Crawler")
    print("="*50)

    # Test URL
    test_url = "https://nettruyenvia.com/"
    print(f"Testing with: {test_url}")

    try:
        async with ImageCrawlerService() as crawler:
            print("🔍 Starting crawl...")

            result = await crawler.crawl_images(
                url=test_url,
                max_images=10,  # Limit for testing
                include_base64=True,
                use_selenium=True,
                custom_headers=None
            )

            status, domain, folder_path, total_found, images_info, errors, processing_time = result

            print(f"✅ Crawl completed!")
            print(f"📊 Status: {status}")
            print(f"🌐 Domain: {domain}")
            print(f"📁 Folder: {folder_path}")
            print(f"🔍 Images found: {total_found}")
            print(f"⬇️ Images downloaded: {len(images_info)}")
            print(f"⚡ Processing time: {processing_time:.2f} seconds")

            if images_info:
                print(f"\n📸 Downloaded images:")
                for i, img in enumerate(images_info[:5], 1):
                    print(f"  {i}. {img.filename} ({img.size_bytes} bytes)")
                    if 'kcgsbok.com' in img.original_url:
                        print(f"     🎯 SUCCESS: Bypassed kcgsbok.com blocking!")
                    print(f"     URL: {img.original_url[:80]}...")

            if errors:
                print(f"\n⚠️ Errors ({len(errors)}):")
                for error in errors[:3]:
                    print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Make sure you have Chrome/Chromium installed for Selenium!")
    print("Installing dependencies if needed...")

    # Run the async test
    asyncio.run(test_crawler())
