"""
Test script for getting all crawled manga
"""

import asyncio
import os
from services.manga_list_crawler import MangaListCrawler


async def test_all_crawled_manga():
    """Test getting all crawled manga"""
    print("📚 Testing All Crawled Manga API...")

    try:
        # Initialize services
        async with MangaListCrawler() as crawler:
            print("✅ MangaListCrawler initialized")

            # Test 1: Get all local manga
            print("\n1️⃣ Testing local manga retrieval...")
            local_manga = await crawler.get_all_crawled_manga("local")

            print(f"   📊 Local Manga Summary:")
            print(f"      Total manga: {local_manga.get('total_manga', 0)}")
            print(f"      Total chapters: {local_manga.get('total_chapters', 0)}")
            print(f"      Total images: {local_manga.get('total_images', 0)}")

            # Show individual manga
            manga_list = local_manga.get("manga_list", [])
            if manga_list:
                print(f"   📖 Local Manga List:")
                for i, manga in enumerate(manga_list[:10], 1):  # Show first 10
                    title = manga.get("manga_title", "Unknown")
                    progress = manga.get("progress", {})
                    chapters = progress.get("total_chapters", 0)
                    images = progress.get("total_images", 0)
                    has_metadata = manga.get("has_metadata", False)
                    has_chapters = manga.get("has_chapters", False)

                    print(f"      {i}. {title}")
                    print(f"         📚 Chapters: {chapters}, 🖼️ Images: {images}")
                    print(f"         📄 Metadata: {has_metadata}, 📁 Has Chapters: {has_chapters}")

                if len(manga_list) > 10:
                    print(f"      ... and {len(manga_list) - 10} more manga")
            else:
                print("   📭 No local manga found")

            # Test 2: Get all cloud manga
            print(f"\n2️⃣ Testing cloud manga retrieval...")
            cloud_manga = await crawler.get_all_crawled_manga("cloud")

            print(f"   ☁️ Cloud Manga Summary:")
            print(f"      Total manga: {cloud_manga.get('total_manga', 0)}")
            print(f"      Total chapters: {cloud_manga.get('total_chapters', 0)}")
            print(f"      Total images: {cloud_manga.get('total_images', 0)}")

            # Show individual cloud manga
            cloud_manga_list = cloud_manga.get("manga_list", [])
            if cloud_manga_list:
                print(f"   ☁️ Cloud Manga List:")
                for i, manga in enumerate(cloud_manga_list[:10], 1):  # Show first 10
                    title = manga.get("manga_title", "Unknown")
                    progress = manga.get("progress", {})
                    chapters = progress.get("total_chapters", 0)
                    images = progress.get("total_images", 0)

                    print(f"      {i}. {title}")
                    print(f"         📚 Chapters: {chapters}, 🖼️ Images: {images}")

                if len(cloud_manga_list) > 10:
                    print(f"      ... and {len(cloud_manga_list) - 10} more manga")
            else:
                print("   ☁️ No cloud manga found")

            # Test 3: Compare local vs cloud
            print(f"\n3️⃣ Comparison Summary:")
            print(f"   📊 Local Storage:")
            print(f"      Manga: {local_manga.get('total_manga', 0)}")
            print(f"      Chapters: {local_manga.get('total_chapters', 0)}")
            print(f"      Images: {local_manga.get('total_images', 0)}")

            print(f"   ☁️ Cloud Storage:")
            print(f"      Manga: {cloud_manga.get('total_manga', 0)}")
            print(f"      Chapters: {cloud_manga.get('total_chapters', 0)}")
            print(f"      Images: {cloud_manga.get('total_images', 0)}")

            print("\n✅ All crawled manga test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🔗 Testing API Endpoints...")

    print("📋 Available endpoints:")
    print("   GET /api/v1/manga-list/all-manga?image_type=local")
    print("   GET /api/v1/manga-list/all-manga?image_type=cloud")

    print("\n📝 Example usage:")
    print("   curl 'http://localhost:8000/api/v1/manga-list/all-manga?image_type=local'")
    print("   curl 'http://localhost:8000/api/v1/manga-list/all-manga?image_type=cloud'")

    print("\n📊 Expected response format:")
    print("   {")
    print("     'image_type': 'local',")
    print("     'total_manga': 5,")
    print("     'total_chapters': 25,")
    print("     'total_images': 1250,")
    print("     'manga_list': [")
    print("       {")
    print("         'manga_title': 'Example Manga',")
    print("         'manga_folder': 'downloads/Example_Manga',")
    print("         'progress': {")
    print("           'total_chapters': 5,")
    print("           'completed_chapters': 5,")
    print("           'total_images': 250")
    print("         },")
    print("         'has_metadata': true,")
    print("         'has_chapters': true")
    print("       }")
    print("     ]")
    print("   }")


if __name__ == "__main__":
    print("🚀 Starting All Crawled Manga Tests...")

    # Run tests
    asyncio.run(test_all_crawled_manga())
    asyncio.run(test_api_endpoints())

    print("\n🎉 All tests completed!")
