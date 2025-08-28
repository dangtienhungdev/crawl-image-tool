"""
Demo script showcasing the new Smart Duplicate Detection feature
"""

import asyncio
import os
import time
from services.manga_crawler import MangaCrawlerService
from services.existence_checker import ExistenceChecker


async def demo_smart_detection():
    """Demonstrate the smart duplicate detection feature"""
    print("🚀 Smart Duplicate Detection Demo")
    print("=" * 50)

    # Test manga URL (you can change this to any manga you want to test)
    test_manga_url = "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-thanh-tro-thanh-vo-dich"

    print(f"📚 Test Manga: {test_manga_url}")
    print(f"💾 Storage Type: Local (you can change to 'cloud' for cloud storage)")

    # Initialize services
    async with MangaCrawlerService() as crawler:
        print(f"\n✅ MangaCrawlerService initialized")
        print(f"✅ ExistenceChecker initialized")

        # Get manga info first
        print(f"\n📖 Getting manga information...")
        try:
            async with crawler.session.get(test_manga_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    manga_title = crawler._extract_manga_title(html_content)
                    print(f"   📚 Manga Title: {manga_title}")

                    # Get chapter list
                    chapters = await crawler._get_chapter_list(test_manga_url)
                    print(f"   📋 Total Chapters Found: {len(chapters)}")

                    if chapters:
                        print(f"   📖 Sample Chapters:")
                        for i, (num, title, url) in enumerate(chapters[:5], 1):
                            print(f"      {i}. Chapter {num}: {title}")
                        if len(chapters) > 5:
                            print(f"      ... and {len(chapters) - 5} more")
                else:
                    print(f"   ❌ Failed to access manga page: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ Error getting manga info: {str(e)}")
            return

        # Create manga folder path
        sanitized_title = crawler._sanitize_folder_name(manga_title)
        manga_folder = os.path.join('downloads', sanitized_title)

        print(f"\n📁 Manga Folder: {manga_folder}")

        # Check initial progress
        print(f"\n🔍 Checking initial progress...")
        initial_progress = await crawler.existence_checker.get_manga_progress(manga_folder, "local")
        print(f"   📊 Initial Progress: {initial_progress}")

        # Demo 1: First run (download first 3 chapters)
        print(f"\n🎯 Demo 1: First Run - Downloading first 3 chapters")
        print(f"   This will download chapters 1-3")

        start_time = time.time()
        try:
            status, title, folder, total_chapters, chapters_info, errors, processing_time = await crawler.crawl_manga(
                manga_url=test_manga_url,
                max_chapters=3,
                start_chapter=1,
                end_chapter=3,
                delay_between_chapters=1.0,
                image_type="local"
            )

            first_run_time = time.time() - start_time
            print(f"   ✅ First run completed in {first_run_time:.2f}s")
            print(f"   📊 Status: {status}")
            print(f"   📚 Chapters downloaded: {len(chapters_info)}")
            print(f"   🖼️ Total images: {sum(len(ch.images) for ch in chapters_info)}")

        except Exception as e:
            print(f"   ❌ First run failed: {str(e)}")
            return

        # Check progress after first run
        print(f"\n🔍 Checking progress after first run...")
        progress_after_first = await crawler.existence_checker.get_manga_progress(manga_folder, "local")
        print(f"   📊 Progress: {progress_after_first}")

        # Demo 2: Second run (should skip existing chapters)
        print(f"\n🎯 Demo 2: Second Run - Should skip existing chapters")
        print(f"   This should be much faster as it skips existing content")

        start_time = time.time()
        try:
            status, title, folder, total_chapters, chapters_info, errors, processing_time = await crawler.crawl_manga(
                manga_url=test_manga_url,
                max_chapters=3,
                start_chapter=1,
                end_chapter=3,
                delay_between_chapters=1.0,
                image_type="local"
            )

            second_run_time = time.time() - start_time
            print(f"   ✅ Second run completed in {second_run_time:.2f}s")
            print(f"   📊 Status: {status}")
            print(f"   📚 Chapters processed: {len(chapters_info)}")
            print(f"   🖼️ Total images: {sum(len(ch.images) for ch in chapters_info)}")

            # Show time difference
            time_diff = first_run_time - second_run_time
            if time_diff > 0:
                print(f"   ⚡ Time saved: {time_diff:.2f}s ({((time_diff/first_run_time)*100):.1f}% faster)")
            else:
                print(f"   ⚠️ No time saved (this might happen if all content was already cached)")

        except Exception as e:
            print(f"   ❌ Second run failed: {str(e)}")
            return

        # Demo 3: Check individual chapter existence
        print(f"\n🔍 Demo 3: Checking individual chapter existence...")
        for chapter_num in ["1", "2", "3"]:
            exists, images = await crawler.existence_checker.check_chapter_exists(manga_folder, chapter_num, "local")
            print(f"   📖 Chapter {chapter_num}: exists={exists}, images={len(images)}")

        # Demo 4: Check individual image existence
        print(f"\n🔍 Demo 4: Checking individual image existence...")
        chapter_1_folder = os.path.join(manga_folder, "Chapter_1")
        if os.path.exists(chapter_1_folder):
            for i in range(1, 4):
                filename = f"{i:03d}.jpg"
                exists = await crawler.existence_checker.check_image_exists(manga_folder, "1", filename, "local")
                print(f"   🖼️ Chapter 1/{filename}: exists={exists}")

        # Demo 5: Resume capability (download more chapters)
        print(f"\n🎯 Demo 5: Resume Capability - Download more chapters")
        print(f"   This will download chapters 4-6, skipping 1-3")

        start_time = time.time()
        try:
            status, title, folder, total_chapters, chapters_info, errors, processing_time = await crawler.crawl_manga(
                manga_url=test_manga_url,
                max_chapters=3,
                start_chapter=4,
                end_chapter=6,
                delay_between_chapters=1.0,
                image_type="local"
            )

            resume_time = time.time() - start_time
            print(f"   ✅ Resume run completed in {resume_time:.2f}s")
            print(f"   📊 Status: {status}")
            print(f"   📚 Chapters downloaded: {len(chapters_info)}")
            print(f"   🖼️ Total images: {sum(len(ch.images) for ch in chapters_info)}")

        except Exception as e:
            print(f"   ❌ Resume run failed: {str(e)}")

        # Final progress check
        print(f"\n🔍 Final progress check...")
        final_progress = await crawler.existence_checker.get_manga_progress(manga_folder, "local")
        print(f"   📊 Final Progress: {final_progress}")

        print(f"\n🎉 Demo completed!")
        print(f"📁 Check the downloads folder to see the organized structure:")
        print(f"   {manga_folder}")
        print(f"📄 Check the metadata file for progress tracking:")
        print(f"   {os.path.join(manga_folder, 'manga_metadata.json')}")


async def demo_cloud_storage():
    """Demonstrate cloud storage with smart detection"""
    print(f"\n☁️ Cloud Storage Demo")
    print("=" * 30)
    print(f"Note: This demo requires proper Wasabi S3 configuration")
    print(f"      Set your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.")

    try:
        from services.wasabi_service import WasabiService
        wasabi = WasabiService()
        print(f"✅ Wasabi service initialized")

        # Test cloud storage existence checking
        test_folder = "test_cloud_manga"
        checker = ExistenceChecker()
        await checker.initialize_wasabi()

        print(f"🔍 Testing cloud storage existence checking...")
        exists, images = await checker.check_chapter_exists(test_folder, "1", "cloud")
        print(f"   Cloud chapter exists: {exists}")
        print(f"   Cloud images: {images}")

    except Exception as e:
        print(f"❌ Cloud storage demo failed: {str(e)}")
        print(f"   Make sure you have proper AWS credentials configured")


if __name__ == "__main__":
    print("🚀 Starting Smart Duplicate Detection Demo...")
    print("This demo will show how the system automatically skips existing content")
    print("Make sure you have a stable internet connection for manga crawling")

    # Run the main demo
    asyncio.run(demo_smart_detection())

    # Run cloud storage demo (optional)
    asyncio.run(demo_cloud_storage())

    print(f"\n🎯 Key Benefits Demonstrated:")
    print(f"   ✅ Automatic chapter skipping")
    print(f"   ✅ Individual image detection")
    print(f"   ✅ Progress tracking with metadata")
    print(f"   ✅ Resume capability")
    print(f"   ✅ Time and bandwidth savings")
    print(f"   ✅ Both local and cloud storage support")
