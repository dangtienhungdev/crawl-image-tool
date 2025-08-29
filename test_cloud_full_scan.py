"""
Test script for full cloud storage scanning
"""

import asyncio
import os
from dotenv import load_dotenv
from services.manga_list_crawler import MangaListCrawler
from services.wasabi_service import WasabiService


async def test_full_cloud_scan():
    """Test full cloud storage scanning"""
    print("☁️ Testing Full Cloud Storage Scan...")

    # Load environment variables
    load_dotenv()

    try:
        # Test 1: Direct Wasabi service scan
        print("\n1️⃣ Testing direct Wasabi service scan...")
        wasabi = WasabiService()

        # Get all objects
        all_objects = wasabi.list_objects(prefix="")
        print(f"   📦 Total objects in bucket: {len(all_objects)}")

        # Group by manga
        manga_groups = {}
        for obj in all_objects:
            parts = obj.split('/')
            if len(parts) >= 3 and parts[1].startswith("Chapter_"):
                manga_title = parts[0]
                if manga_title not in manga_groups:
                    manga_groups[manga_title] = set()
                manga_groups[manga_title].add(parts[1])

        print(f"   📚 Found {len(manga_groups)} manga")

        # Show sample manga
        sample_manga = list(manga_groups.items())[:10]
        for manga_title, chapters in sample_manga:
            print(f"      📖 {manga_title}: {len(chapters)} chapters")

        if len(manga_groups) > 10:
            print(f"      ... and {len(manga_groups) - 10} more manga")

        # Test 2: MangaListCrawler scan
        print(f"\n2️⃣ Testing MangaListCrawler scan...")
        async with MangaListCrawler() as crawler:
            cloud_manga = await crawler.get_all_crawled_manga("cloud")

            print(f"   ☁️ Cloud Manga Summary:")
            print(f"      Total manga: {cloud_manga.get('total_manga', 0)}")
            print(f"      Total chapters: {cloud_manga.get('total_chapters', 0)}")
            print(f"      Total images: {cloud_manga.get('total_images', 0)}")

            # Show sample manga with details
            manga_list = cloud_manga.get("manga_list", [])
            if manga_list:
                print(f"   📖 Sample Manga Details:")
                for i, manga in enumerate(manga_list[:5], 1):
                    title = manga.get("manga_title", "Unknown")
                    progress = manga.get("progress", {})
                    chapters = progress.get("total_chapters", 0)
                    images = progress.get("total_images", 0)
                    print(f"      {i}. {title}")
                    print(f"         📚 Chapters: {chapters}, 🖼️ Images: {images}")

                    # Show sample chapters
                    chapters_data = progress.get("chapters", {})
                    if chapters_data:
                        sample_chapters = list(chapters_data.items())[:3]
                        for ch_num, ch_data in sample_chapters:
                            ch_images = ch_data.get("total_images", 0)
                            print(f"            Chapter {ch_num}: {ch_images} images")

                if len(manga_list) > 5:
                    print(f"      ... and {len(manga_list) - 5} more manga")

        # Test 3: Compare results
        print(f"\n3️⃣ Comparison:")
        print(f"   Direct scan: {len(manga_groups)} manga")
        print(f"   MangaListCrawler: {cloud_manga.get('total_manga', 0)} manga")

        if len(manga_groups) == cloud_manga.get('total_manga', 0):
            print(f"   ✅ Results match!")
        else:
            print(f"   ⚠️ Results don't match - investigating...")

            # Find differences
            direct_manga = set(manga_groups.keys())
            crawler_manga = set(m.get("manga_title") for m in manga_list)

            missing_in_crawler = direct_manga - crawler_manga
            extra_in_crawler = crawler_manga - direct_manga

            if missing_in_crawler:
                print(f"   📭 Missing in crawler: {len(missing_in_crawler)}")
                for manga in list(missing_in_crawler)[:5]:
                    print(f"      - {manga}")

            if extra_in_crawler:
                print(f"   ➕ Extra in crawler: {len(extra_in_crawler)}")
                for manga in list(extra_in_crawler)[:5]:
                    print(f"      - {manga}")

        print("\n✅ Full cloud scan test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_pagination():
    """Test pagination functionality"""
    print(f"\n📄 Testing Pagination...")

    try:
        wasabi = WasabiService()

        # Test with different max_keys values
        for max_keys in [100, 500, 1000]:
            print(f"\n   Testing with max_keys={max_keys}")
            objects = wasabi.list_objects(prefix="", max_keys=max_keys)
            print(f"      Retrieved {len(objects)} objects")

            if len(objects) < max_keys:
                print(f"      ✅ All objects retrieved (no pagination needed)")
            else:
                print(f"      ⚠️ May need pagination (got {len(objects)} objects)")

    except Exception as e:
        print(f"❌ Pagination test failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Full Cloud Storage Scan Tests...")
    print("This will test if we can retrieve all 94 manga from cloud storage")

    # Run tests
    asyncio.run(test_full_cloud_scan())
    asyncio.run(test_pagination())

    print("\n🎉 All tests completed!")
