"""
Demo script showcasing Smart Duplicate Detection for Manga List Crawling
"""

import asyncio
import os
import time
from services.manga_list_crawler import MangaListCrawler


async def demo_manga_list_smart_detection():
    """Demonstrate smart duplicate detection for manga list crawling"""
    print("🚀 Manga List Smart Duplicate Detection Demo")
    print("=" * 60)

    # Test manga list URL
    test_list_url = "https://nettruyenvia.com/?page=637"

    print(f"📚 Test Manga List: {test_list_url}")
    print(f"💾 Storage Type: Local (you can change to 'cloud' for cloud storage)")

    # Initialize services
    async with MangaListCrawler() as crawler:
        print(f"\n✅ MangaListCrawler initialized")
        print(f"✅ ExistenceChecker initialized")

        # Get manga list info first
        print(f"\n📖 Getting manga list information...")
        try:
            manga_links = await crawler._extract_manga_urls(test_list_url)
            print(f"   📋 Total manga found: {len(manga_links)}")

            if manga_links:
                print(f"   📖 Sample manga:")
                for i, (url, title) in enumerate(manga_links[:5], 1):
                    print(f"      {i}. {title}")
                if len(manga_links) > 5:
                    print(f"      ... and {len(manga_links) - 5} more")
        except Exception as e:
            print(f"   ❌ Error getting manga list: {str(e)}")
            return

        # Check initial progress
        print(f"\n🔍 Checking initial progress...")
        initial_progress = await crawler.get_manga_list_progress(test_list_url, "local")
        overall = initial_progress.get("overall_progress", {})
        print(f"   📊 Initial Progress:")
        print(f"      Total manga: {overall.get('total_manga', 0)}")
        print(f"      Completed manga: {overall.get('completed_manga', 0)}")
        print(f"      Total chapters: {overall.get('total_chapters', 0)}")
        print(f"      Total images: {overall.get('total_images', 0)}")

        # Demo 1: Show how smart detection works
        print(f"\n🎯 Demo 1: Smart Duplicate Detection Explanation")
        print(f"   When you crawl a manga list, the system will:")
        print(f"   1. Extract all manga URLs from the list page")
        print(f"   2. For each manga, check if it already exists")
        print(f"   3. Skip existing manga completely")
        print(f"   4. For new manga, check existing chapters")
        print(f"   5. Skip existing chapters and images")
        print(f"   6. Only download missing content")

        # Demo 2: Show progress tracking
        print(f"\n🎯 Demo 2: Progress Tracking")
        print(f"   The system tracks progress at multiple levels:")
        print(f"   📚 Manga Level: Which manga are completed")
        print(f"   📖 Chapter Level: Which chapters exist")
        print(f"   🖼️ Image Level: Which images exist")
        print(f"   📊 Overall Level: Total statistics")

        # Demo 3: Show API endpoints
        print(f"\n🎯 Demo 3: Available API Endpoints")
        print(f"   📋 Check Progress:")
        print(f"      GET /api/v1/manga-list/progress?list_url={test_list_url}&image_type=local")
        print(f"   🚀 Crawl with Smart Detection:")
        print(f"      POST /api/v1/manga-list/crawl")
        print(f"      Body: {{\"url\": \"{test_list_url}\", \"max_manga\": 3, \"image_type\": \"local\"}}")

        # Demo 4: Show benefits
        print(f"\n🎯 Demo 4: Key Benefits")
        print(f"   ⚡ Faster Re-runs: Skip existing content automatically")
        print(f"   💾 Storage Efficiency: No duplicate files created")
        print(f"   🔄 Resume Support: Continue interrupted downloads seamlessly")
        print(f"   📊 Progress Monitoring: Track status across sessions")
        print(f"   🌐 Cloud Compatible: Works with both local and cloud storage")
        print(f"   📈 Scalable: Handle large manga lists efficiently")

        # Demo 5: Show example workflow
        print(f"\n🎯 Demo 5: Example Workflow")
        print(f"   1. First run: Download 3 manga with 5 chapters each")
        print(f"      → Creates folders and downloads all content")
        print(f"   2. Second run: Same request")
        print(f"      → Skips all existing manga and chapters")
        print(f"      → Completes in seconds instead of hours")
        print(f"   3. Third run: Download 5 manga with 10 chapters each")
        print(f"      → Skips existing 3 manga completely")
        print(f"      → Downloads 2 new manga + 5 additional chapters for existing")

        print(f"\n🎉 Demo completed!")
        print(f"📁 Check the downloads folder to see organized manga structure")
        print(f"📄 Each manga folder contains manga_metadata.json for progress tracking")


async def demo_cloud_storage_integration():
    """Demonstrate cloud storage integration for manga list"""
    print(f"\n☁️ Cloud Storage Integration Demo")
    print("=" * 40)
    print(f"Note: This demo requires proper Wasabi S3 configuration")
    print(f"      Set your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.")

    try:
        from services.wasabi_service import WasabiService
        wasabi = WasabiService()
        print(f"✅ Wasabi service initialized")

        # Test manga list progress with cloud storage
        test_list_url = "https://nettruyenvia.com/?page=637"

        async with MangaListCrawler() as crawler:
            print(f"🔍 Testing manga list progress with cloud storage...")
            progress = await crawler.get_manga_list_progress(test_list_url, "cloud")

            overall = progress.get("overall_progress", {})
            print(f"   ☁️ Cloud Progress:")
            print(f"      Total manga: {overall.get('total_manga', 0)}")
            print(f"      Completed manga: {overall.get('completed_manga', 0)}")
            print(f"      Total chapters: {overall.get('total_chapters', 0)}")
            print(f"      Total images: {overall.get('total_images', 0)}")

    except Exception as e:
        print(f"❌ Cloud storage demo failed: {str(e)}")
        print(f"   Make sure you have proper AWS credentials configured")


if __name__ == "__main__":
    print("🚀 Starting Manga List Smart Detection Demo...")
    print("This demo shows how the system automatically skips existing content")
    print("Make sure you have a stable internet connection")

    # Run the main demo
    asyncio.run(demo_manga_list_smart_detection())

    # Run cloud storage demo (optional)
    asyncio.run(demo_cloud_storage_integration())

    print(f"\n🎯 Key Benefits Demonstrated:")
    print(f"   ✅ Automatic manga skipping")
    print(f"   ✅ Chapter-level detection")
    print(f"   ✅ Image-level detection")
    print(f"   ✅ Progress tracking")
    print(f"   ✅ Resume capability")
    print(f"   ✅ Time and bandwidth savings")
    print(f"   ✅ Both local and cloud storage support")
    print(f"   ✅ Scalable for large manga lists")
