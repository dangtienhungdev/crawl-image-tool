"""
Test script for cloud storage existence checking
"""

import asyncio
import os
from services.existence_checker import ExistenceChecker
from services.wasabi_service import WasabiService


async def test_cloud_existence():
    """Test cloud storage existence checking"""
    print("☁️ Testing Cloud Storage Existence Checking...")

    try:
        # Initialize services
        checker = ExistenceChecker()
        wasabi = WasabiService()

        print("✅ Services initialized")

        # Test manga folder
        test_manga = "Anh_Hùng_Giai_Cấp_Tư_Sản"  # Use the same manga from your log
        test_manga_folder = os.path.join("downloads", test_manga)

        print(f"📁 Testing with manga: {test_manga}")

        # Test 1: Check if chapter exists in cloud
        print("\n1️⃣ Testing chapter existence in cloud...")
        exists, images = await checker.check_chapter_exists(test_manga_folder, "4", "cloud")
        print(f"   Chapter 4 exists: {exists}")
        print(f"   Images found: {len(images)}")
        if images:
            print(f"   Sample images: {images[:5]}")

        # Test 2: Check specific images
        print("\n2️⃣ Testing specific image existence...")
        test_images = ["068.jpg", "069.jpg", "070.jpg", "071.jpg", "072.jpg"]
        for img in test_images:
            exists = await checker.check_image_exists(test_manga_folder, "4", img, "cloud")
            print(f"   Chapter 4/{img}: {exists}")

        # Test 3: List objects with prefix
        print("\n3️⃣ Testing list_objects method...")
        manga_title = os.path.basename(test_manga_folder)
        chapter_prefix = f"{manga_title}/Chapter_4/"
        print(f"   Prefix: {chapter_prefix}")

        objects = wasabi.list_objects(prefix=chapter_prefix)
        print(f"   Objects found: {len(objects)}")
        if objects:
            print(f"   Sample objects: {objects[:5]}")

        # Test 4: Check object_exists method
        print("\n4️⃣ Testing object_exists method...")
        for img in test_images[:3]:  # Test first 3 images
            image_key = f"{manga_title}/Chapter_4/{img}"
            exists = wasabi.object_exists(image_key)
            print(f"   {image_key}: {exists}")

        # Test 5: Test with non-existent objects
        print("\n5️⃣ Testing non-existent objects...")
        non_existent_key = f"{manga_title}/Chapter_999/999.jpg"
        exists = wasabi.object_exists(non_existent_key)
        print(f"   {non_existent_key}: {exists}")

        print("\n✅ Cloud existence checking test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_manga_crawler_cloud_integration():
    """Test manga crawler integration with cloud storage"""
    print("\n🔗 Testing Manga Crawler Cloud Integration...")

    try:
        from services.manga_crawler import MangaCrawlerService

        async with MangaCrawlerService() as crawler:
            print("✅ MangaCrawlerService initialized")

            # Test existence checker with cloud storage
            test_manga = "Anh_Hùng_Giai_Cấp_Tư_Sản"
            test_manga_folder = os.path.join("downloads", test_manga)

            print(f"📁 Testing manga: {test_manga}")

            # Test chapter existence
            exists, images = await crawler.existence_checker.check_chapter_exists(
                test_manga_folder, "4", "cloud"
            )
            print(f"   Chapter 4 exists: {exists}")
            print(f"   Images: {len(images)}")

            # Test image existence
            test_image = "068.jpg"
            image_exists = await crawler.existence_checker.check_image_exists(
                test_manga_folder, "4", test_image, "cloud"
            )
            print(f"   Image {test_image} exists: {image_exists}")

            print("✅ Cloud integration test completed!")

    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting Cloud Storage Existence Tests...")

    # Run tests
    asyncio.run(test_cloud_existence())
    asyncio.run(test_manga_crawler_cloud_integration())

    print("\n🎉 All cloud storage tests completed!")
