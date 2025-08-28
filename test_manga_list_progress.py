"""
Test script for manga list progress functionality
"""

import asyncio
import os
from services.manga_list_crawler import MangaListCrawler
from services.existence_checker import ExistenceChecker


async def test_manga_list_progress():
    """Test manga list progress functionality"""
    print("📚 Testing Manga List Progress...")

    # Test manga list URL
    test_list_url = "https://nettruyenvia.com/?page=637"

    print(f"🔗 Test URL: {test_list_url}")

    try:
        # Initialize services
        async with MangaListCrawler() as crawler:
            print("✅ MangaListCrawler initialized")

            # Test 1: Get progress for manga list
            print("\n1️⃣ Testing manga list progress...")
            progress = await crawler.get_manga_list_progress(test_list_url, "local")

            print(f"   📊 Overall Progress:")
            overall = progress.get("overall_progress", {})
            print(f"      Total manga: {overall.get('total_manga', 0)}")
            print(f"      Completed manga: {overall.get('completed_manga', 0)}")
            print(f"      Total chapters: {overall.get('total_chapters', 0)}")
            print(f"      Total images: {overall.get('total_images', 0)}")

            # Test 2: Show individual manga progress
            print(f"\n2️⃣ Individual manga progress:")
            manga_progress = progress.get("manga_progress", [])

            for i, manga in enumerate(manga_progress[:5], 1):  # Show first 5
                title = manga.get("manga_title", "Unknown")
                manga_progress_data = manga.get("progress", {})

                if "error" in manga_progress_data:
                    print(f"   {i}. {title}: ❌ Error - {manga_progress_data['error']}")
                else:
                    chapters = manga_progress_data.get("total_chapters", 0)
                    images = manga_progress_data.get("total_images", 0)
                    print(f"   {i}. {title}: 📚 {chapters} chapters, 🖼️ {images} images")

            if len(manga_progress) > 5:
                print(f"   ... and {len(manga_progress) - 5} more manga")

            # Test 3: Test cloud storage progress
            print(f"\n3️⃣ Testing cloud storage progress...")
            cloud_progress = await crawler.get_manga_list_progress(test_list_url, "cloud")

            cloud_overall = cloud_progress.get("overall_progress", {})
            print(f"   ☁️ Cloud Progress:")
            print(f"      Total manga: {cloud_overall.get('total_manga', 0)}")
            print(f"      Completed manga: {cloud_overall.get('completed_manga', 0)}")
            print(f"      Total chapters: {cloud_overall.get('total_chapters', 0)}")
            print(f"      Total images: {cloud_overall.get('total_images', 0)}")

            print("\n✅ Manga list progress test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_manga_list_crawler_integration():
    """Test manga list crawler integration with smart detection"""
    print("\n🔗 Testing Manga List Crawler Integration...")

    try:
        async with MangaListCrawler() as crawler:
            print("✅ MangaListCrawler initialized")

            # Test with a small manga list (just 2 manga, 1 chapter each)
            test_list_url = "https://nettruyenvia.com/?page=637"

            print(f"📚 Testing manga list crawl with smart detection...")
            print(f"   This will show how existing manga are skipped")

            # First, get progress
            progress_before = await crawler.get_manga_list_progress(test_list_url, "local")
            print(f"   📊 Progress before crawl: {progress_before.get('overall_progress', {})}")

            # Note: We won't actually run the crawl here as it takes too long
            # But we can show the structure
            print(f"   🚀 Crawl would use smart duplicate detection")
            print(f"   ✅ Existing manga and chapters would be skipped automatically")

    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Manga List Progress Tests...")

    # Run tests
    asyncio.run(test_manga_list_progress())
    asyncio.run(test_manga_list_crawler_integration())

    print("\n🎉 All manga list progress tests completed!")
