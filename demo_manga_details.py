"""
Demo script showcasing the Manga Details API functionality
"""

import asyncio
import os
from services.manga_list_crawler import MangaListCrawler


async def demo_manga_details():
    """Demonstrate the Manga Details API functionality"""
    print("📚 Manga Details API Demo")
    print("=" * 50)

    print(f"🎯 This demo shows how to get detailed information for a specific manga")
    print(f"💾 Supports both local and cloud storage")

    # Initialize services
    async with MangaListCrawler() as crawler:
        print(f"\n✅ MangaListCrawler initialized")

        # Demo 1: Cloud Manga Details
        print(f"\n🎯 Demo 1: Cloud Manga Details")
        print(f"   This will get detailed information for a manga in cloud storage")

        cloud_manga_title = "Black_Clover"
        cloud_details = await crawler.get_manga_details(cloud_manga_title, "cloud")

        if cloud_details.get("found", False):
            print(f"   📖 Manga: {cloud_details.get('manga_title')}")

            # Show summary
            summary = cloud_details.get("summary", {})
            print(f"   📊 Summary:")
            print(f"      Total chapters: {summary.get('total_chapters', 0)}")
            print(f"      Total images: {summary.get('total_images', 0)}")
            print(f"      Average images per chapter: {summary.get('average_images_per_chapter', 0):.1f}")

            # Show sample chapters
            chapter_details = cloud_details.get("chapter_details", [])
            if chapter_details:
                print(f"   📚 Sample Chapters:")
                for i, chapter in enumerate(chapter_details[:3], 1):
                    ch_num = chapter.get("chapter_number", "Unknown")
                    ch_images = chapter.get("total_images", 0)
                    print(f"      {i}. Chapter {ch_num}: {ch_images} images")

                if len(chapter_details) > 3:
                    print(f"      ... and {len(chapter_details) - 3} more chapters")

            # Show cloud info
            cloud_info = cloud_details.get("cloud_info", {})
            print(f"   ☁️ Cloud Storage Info:")
            print(f"      Bucket: {cloud_info.get('bucket_name', 'Unknown')}")
            print(f"      Total objects: {cloud_info.get('total_objects', 0)}")
        else:
            print(f"   ❌ Manga not found: {cloud_details.get('error', 'Unknown error')}")

        # Demo 2: Local Manga Details
        print(f"\n🎯 Demo 2: Local Manga Details")
        print(f"   This will get detailed information for a manga in local storage")

        local_manga_title = "test_manga"
        local_details = await crawler.get_manga_details(local_manga_title, "local")

        if local_details.get("found", False):
            print(f"   📖 Manga: {local_details.get('manga_title')}")

            # Show summary
            summary = local_details.get("summary", {})
            print(f"   📊 Summary:")
            print(f"      Total chapters: {summary.get('total_chapters', 0)}")
            print(f"      Total images: {summary.get('total_images', 0)}")
            print(f"      Average images per chapter: {summary.get('average_images_per_chapter', 0):.1f}")

            # Show folder info
            folder_info = local_details.get("folder_info", {})
            print(f"   📁 Folder Information:")
            print(f"      Path: {folder_info.get('manga_folder', 'Unknown')}")
            print(f"      Size: {folder_info.get('total_size', 0)} bytes")
            print(f"      Has metadata: {folder_info.get('has_metadata', False)}")
            print(f"      Created: {folder_info.get('created_date', 'Unknown')}")
            print(f"      Modified: {folder_info.get('modified_date', 'Unknown')}")
        else:
            print(f"   📭 Local manga not found: {local_details.get('error', 'Folder not found')}")

        # Demo 3: API Usage
        print(f"\n🎯 Demo 3: API Endpoints")
        print(f"   📋 Available endpoints:")
        print(f"      GET /api/v1/manga-list/manga/{manga_title}?image_type=local")
        print(f"      GET /api/v1/manga-list/manga/{manga_title}?image_type=cloud")

        print(f"\n   📝 Example curl commands:")
        print(f"      curl 'http://localhost:8000/api/v1/manga-list/manga/Black_Clover?image_type=cloud'")
        print(f"      curl 'http://localhost:8000/api/v1/manga-list/manga/test_manga?image_type=local'")

        # Demo 4: Use Cases
        print(f"\n🎯 Demo 4: Use Cases")
        print(f"   📊 Content Management:")
        print(f"      - Get complete chapter list for a manga")
        print(f"      - Check individual image files")
        print(f"      - Monitor download progress")

        print(f"   🔍 Quality Control:")
        print(f"      - Verify all chapters are complete")
        print(f"      - Check image counts per chapter")
        print(f"      - Identify missing content")

        print(f"   📈 Analytics:")
        print(f"      - Calculate storage usage")
        print(f"      - Track download statistics")
        print(f"      - Monitor content growth")

        # Demo 5: Response Structure
        print(f"\n🎯 Demo 5: Response Structure")
        print(f"   📄 Response includes:")
        print(f"      - manga_title: Name of the manga")
        print(f"      - image_type: Storage type used")
        print(f"      - found: Whether manga exists")
        print(f"      - summary: Overall statistics")
        print(f"      - chapter_details: Complete chapter list")
        print(f"      - folder_info/cloud_info: Storage details")

        print(f"   📖 Chapter details include:")
        print(f"      - chapter_number: Chapter identifier")
        print(f"      - total_images: Number of images")
        print(f"      - images: List of image filenames")
        print(f"      - status: Download status")

        print(f"\n🎉 Demo completed!")
        print(f"📁 Use this API to get detailed information about any manga")
        print(f"☁️ Works with both local and cloud storage")


async def demo_advanced_features():
    """Demonstrate advanced features"""
    print(f"\n🚀 Advanced Features Demo")
    print("=" * 40)

    print(f"🎯 Advanced capabilities:")

    print(f"   📊 Detailed Analytics:")
    print(f"      - Per-chapter image analysis")
    print(f"      - Storage usage breakdown")
    print(f"      - Download completion tracking")

    print(f"   🔍 Content Verification:")
    print(f"      - Verify image file integrity")
    print(f"      - Check chapter completeness")
    print(f"      - Identify missing content")

    print(f"   📈 Progress Monitoring:")
    print(f"      - Track download progress")
    print(f"      - Monitor storage growth")
    print(f"      - Analyze content patterns")

    print(f"   🔄 Integration:")
    print(f"      - Web dashboard integration")
    print(f"      - Automated quality checks")
    print(f"      - Content management workflows")


if __name__ == "__main__":
    print("🚀 Starting Manga Details API Demo...")
    print("This demo shows detailed manga information retrieval capabilities")

    # Run the main demo
    asyncio.run(demo_manga_details())
    asyncio.run(demo_advanced_features())

    print(f"\n🎯 Key Benefits Demonstrated:")
    print(f"   ✅ Detailed manga information")
    print(f"   ✅ Complete chapter listings")
    print(f"   ✅ Storage analytics")
    print(f"   ✅ Cross-storage support")
    print(f"   ✅ Error handling")
    print(f"   ✅ API integration")

