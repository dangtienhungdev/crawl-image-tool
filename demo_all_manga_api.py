"""
Demo script showcasing the All Manga API functionality
"""

import asyncio
import os
from services.manga_list_crawler import MangaListCrawler


async def demo_all_manga_api():
    """Demonstrate the All Manga API functionality"""
    print("📚 All Manga API Demo")
    print("=" * 50)

    print(f"🎯 This demo shows how to get all crawled manga")
    print(f"💾 Supports both local and cloud storage")

    # Initialize services
    async with MangaListCrawler() as crawler:
        print(f"\n✅ MangaListCrawler initialized")

        # Demo 1: Local Storage
        print(f"\n🎯 Demo 1: Local Storage Manga")
        print(f"   This will scan the downloads folder for all manga")

        local_manga = await crawler.get_all_crawled_manga("local")

        print(f"   📊 Local Storage Summary:")
        print(f"      Total manga: {local_manga.get('total_manga', 0)}")
        print(f"      Total chapters: {local_manga.get('total_chapters', 0)}")
        print(f"      Total images: {local_manga.get('total_images', 0)}")

        # Show sample manga
        manga_list = local_manga.get("manga_list", [])
        if manga_list:
            print(f"   📖 Sample Local Manga:")
            for i, manga in enumerate(manga_list[:3], 1):
                title = manga.get("manga_title", "Unknown")
                progress = manga.get("progress", {})
                chapters = progress.get("total_chapters", 0)
                images = progress.get("total_images", 0)
                print(f"      {i}. {title}: {chapters} chapters, {images} images")
        else:
            print(f"   📭 No local manga found")

        # Demo 2: Cloud Storage
        print(f"\n🎯 Demo 2: Cloud Storage Manga")
        print(f"   This will scan Wasabi S3 bucket for all manga")

        cloud_manga = await crawler.get_all_crawled_manga("cloud")

        print(f"   ☁️ Cloud Storage Summary:")
        print(f"      Total manga: {cloud_manga.get('total_manga', 0)}")
        print(f"      Total chapters: {cloud_manga.get('total_chapters', 0)}")
        print(f"      Total images: {cloud_manga.get('total_images', 0)}")

        # Show sample cloud manga
        cloud_manga_list = cloud_manga.get("manga_list", [])
        if cloud_manga_list:
            print(f"   ☁️ Sample Cloud Manga:")
            for i, manga in enumerate(cloud_manga_list[:3], 1):
                title = manga.get("manga_title", "Unknown")
                progress = manga.get("progress", {})
                chapters = progress.get("total_chapters", 0)
                images = progress.get("total_images", 0)
                print(f"      {i}. {title}: {chapters} chapters, {images} images")
        else:
            print(f"   ☁️ No cloud manga found")

        # Demo 3: API Usage
        print(f"\n🎯 Demo 3: API Endpoints")
        print(f"   📋 Available endpoints:")
        print(f"      GET /api/v1/manga-list/all-manga?image_type=local")
        print(f"      GET /api/v1/manga-list/all-manga?image_type=cloud")

        print(f"\n   📝 Example curl commands:")
        print(f"      curl 'http://localhost:8000/api/v1/manga-list/all-manga?image_type=local'")
        print(f"      curl 'http://localhost:8000/api/v1/manga-list/all-manga?image_type=cloud'")

        # Demo 4: Use Cases
        print(f"\n🎯 Demo 4: Use Cases")
        print(f"   📊 Inventory Management:")
        print(f"      - Track all downloaded manga")
        print(f"      - Monitor storage usage")
        print(f"      - Identify missing content")

        print(f"   🔄 Resume Operations:")
        print(f"      - Check what's already downloaded")
        print(f"      - Plan incremental downloads")
        print(f"      - Avoid duplicate work")

        print(f"   📈 Progress Monitoring:")
        print(f"      - Overall download statistics")
        print(f"      - Individual manga progress")
        print(f"      - Storage type comparison")

        # Demo 5: Response Structure
        print(f"\n🎯 Demo 5: Response Structure")
        print(f"   📄 Response includes:")
        print(f"      - image_type: Storage type used")
        print(f"      - total_manga: Count of all manga")
        print(f"      - total_chapters: Total chapters across all manga")
        print(f"      - total_images: Total images across all manga")
        print(f"      - manga_list: Array of manga objects")

        print(f"   📖 Each manga object contains:")
        print(f"      - manga_title: Name of the manga")
        print(f"      - manga_folder: Storage location")
        print(f"      - progress: Chapter and image counts")
        print(f"      - has_metadata: Whether metadata file exists")
        print(f"      - has_chapters: Whether chapters exist")

        print(f"\n🎉 Demo completed!")
        print(f"📁 Check your downloads folder for local manga")
        print(f"☁️ Check your Wasabi bucket for cloud manga")


async def demo_advanced_features():
    """Demonstrate advanced features"""
    print(f"\n🚀 Advanced Features Demo")
    print("=" * 40)

    print(f"🎯 Advanced capabilities:")

    print(f"   📊 Cross-Storage Comparison:")
    print(f"      - Compare local vs cloud content")
    print(f"      - Identify sync gaps")
    print(f"      - Plan migration strategies")

    print(f"   🔍 Content Discovery:")
    print(f"      - Find manga by title")
    print(f"      - Filter by completion status")
    print(f"      - Sort by various criteria")

    print(f"   📈 Analytics:")
    print(f"      - Storage usage patterns")
    print(f"      - Download trends")
    print(f"      - Performance metrics")

    print(f"   🔄 Integration:")
    print(f"      - Web dashboard integration")
    print(f"      - Automated backup systems")
    print(f"      - Content management workflows")


if __name__ == "__main__":
    print("🚀 Starting All Manga API Demo...")
    print("This demo shows comprehensive manga management capabilities")

    # Run the main demo
    asyncio.run(demo_all_manga_api())
    asyncio.run(demo_advanced_features())

    print(f"\n🎯 Key Benefits Demonstrated:")
    print(f"   ✅ Complete manga inventory")
    print(f"   ✅ Cross-storage visibility")
    print(f"   ✅ Progress tracking")
    print(f"   ✅ Storage management")
    print(f"   ✅ API integration")
    print(f"   ✅ Scalable architecture")
