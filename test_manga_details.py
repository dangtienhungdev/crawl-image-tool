"""
Test script for getting manga details
"""

import asyncio
import os
from services.manga_list_crawler import MangaListCrawler


async def test_manga_details():
    """Test getting manga details"""
    print("📚 Testing Manga Details API...")

    try:
        # Initialize services
        async with MangaListCrawler() as crawler:
            print("✅ MangaListCrawler initialized")

            # Test 1: Get details for a cloud manga
            print("\n1️⃣ Testing cloud manga details...")
            cloud_manga_title = "Black_Clover"  # Example manga from cloud

            cloud_details = await crawler.get_manga_details(cloud_manga_title, "cloud")

            if cloud_details.get("found", False):
                print(f"   📖 Found manga: {cloud_details.get('manga_title')}")
                print(f"   📊 Summary:")
                summary = cloud_details.get("summary", {})
                print(f"      Total chapters: {summary.get('total_chapters', 0)}")
                print(f"      Total images: {summary.get('total_images', 0)}")
                print(f"      Average images per chapter: {summary.get('average_images_per_chapter', 0):.1f}")

                # Show sample chapters
                chapter_details = cloud_details.get("chapter_details", [])
                if chapter_details:
                    print(f"   📚 Sample Chapters:")
                    for i, chapter in enumerate(chapter_details[:5], 1):
                        ch_num = chapter.get("chapter_number", "Unknown")
                        ch_images = chapter.get("total_images", 0)
                        print(f"      {i}. Chapter {ch_num}: {ch_images} images")

                    if len(chapter_details) > 5:
                        print(f"      ... and {len(chapter_details) - 5} more chapters")

                # Show cloud info
                cloud_info = cloud_details.get("cloud_info", {})
                print(f"   ☁️ Cloud Info:")
                print(f"      Bucket: {cloud_info.get('bucket_name', 'Unknown')}")
                print(f"      Total objects: {cloud_info.get('total_objects', 0)}")
            else:
                print(f"   ❌ Manga not found: {cloud_details.get('error', 'Unknown error')}")

            # Test 2: Get details for a local manga (if exists)
            print(f"\n2️⃣ Testing local manga details...")
            local_manga_title = "test_manga"  # Example local manga

            local_details = await crawler.get_manga_details(local_manga_title, "local")

            if local_details.get("found", False):
                print(f"   📖 Found manga: {local_details.get('manga_title')}")
                print(f"   📊 Summary:")
                summary = local_details.get("summary", {})
                print(f"      Total chapters: {summary.get('total_chapters', 0)}")
                print(f"      Total images: {summary.get('total_images', 0)}")
                print(f"      Average images per chapter: {summary.get('average_images_per_chapter', 0):.1f}")

                # Show folder info
                folder_info = local_details.get("folder_info", {})
                print(f"   📁 Folder Info:")
                print(f"      Path: {folder_info.get('manga_folder', 'Unknown')}")
                print(f"      Size: {folder_info.get('total_size', 0)} bytes")
                print(f"      Has metadata: {folder_info.get('has_metadata', False)}")
            else:
                print(f"   📭 Local manga not found: {local_details.get('error', 'Folder not found')}")

            # Test 3: Test with non-existent manga
            print(f"\n3️⃣ Testing non-existent manga...")
            fake_manga = "NonExistentManga123"

            fake_details = await crawler.get_manga_details(fake_manga, "cloud")

            if not fake_details.get("found", False):
                print(f"   ✅ Correctly identified non-existent manga")
                print(f"   📝 Error: {fake_details.get('error', 'Unknown error')}")
            else:
                print(f"   ⚠️ Unexpectedly found non-existent manga")

            print("\n✅ Manga details test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🔗 Testing API Endpoints...")

    print("📋 Available endpoints:")
    print("   GET /api/v1/manga-list/manga/{manga_title}?image_type=local")
    print("   GET /api/v1/manga-list/manga/{manga_title}?image_type=cloud")

    print("\n📝 Example usage:")
    print("   curl 'http://localhost:8000/api/v1/manga-list/manga/Black_Clover?image_type=cloud'")
    print("   curl 'http://localhost:8000/api/v1/manga-list/manga/test_manga?image_type=local'")

    print("\n📊 Expected response format:")
    print("   {")
    print("     'manga_title': 'Black_Clover',")
    print("     'image_type': 'cloud',")
    print("     'found': true,")
    print("     'summary': {")
    print("       'total_chapters': 217,")
    print("       'total_images': 3920,")
    print("       'average_images_per_chapter': 18.1")
    print("     },")
    print("     'chapter_details': [")
    print("       {")
    print("         'chapter_number': '1',")
    print("         'total_images': 47,")
    print("         'images': ['001.jpg', '002.jpg', ...],")
    print("         'status': 'completed'")
    print("       }")
    print("     ],")
    print("     'cloud_info': {")
    print("       'bucket_name': 'web-truyen',")
    print("       'total_objects': 3920")
    print("     }")
    print("   }")


if __name__ == "__main__":
    print("🚀 Starting Manga Details Tests...")

    # Run tests
    asyncio.run(test_manga_details())
    asyncio.run(test_api_endpoints())

    print("\n🎉 All tests completed!")

