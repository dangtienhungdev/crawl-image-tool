"""
Test script for the new existence checker functionality
"""

import asyncio
import os
from services.existence_checker import ExistenceChecker


async def test_existence_checker():
    """Test the existence checker functionality"""
    print("🧪 Testing Existence Checker...")

    # Initialize checker
    checker = ExistenceChecker()
    await checker.initialize_wasabi()

    # Test manga folder
    test_manga = "test_manga_existence"
    test_manga_folder = os.path.join("downloads", test_manga)

    print(f"📁 Testing with manga folder: {test_manga_folder}")

    # Test 1: Check non-existent manga
    print("\n1️⃣ Testing non-existent manga...")
    progress = await checker.get_manga_progress(test_manga_folder, "local")
    print(f"   Progress: {progress}")

    # Test 2: Create test chapter and check
    print("\n2️⃣ Creating test chapter structure...")
    test_chapter = "Chapter_1"
    test_chapter_folder = os.path.join(test_manga_folder, test_chapter)

    # Create test structure
    os.makedirs(test_chapter_folder, exist_ok=True)

    # Create test images
    test_images = ["001.jpg", "002.jpg", "003.jpg"]
    for img in test_images:
        img_path = os.path.join(test_chapter_folder, img)
        with open(img_path, 'w') as f:
            f.write("test image content")

    # Test 3: Check existing chapter
    print("\n3️⃣ Testing existing chapter check...")
    exists, images = await checker.check_chapter_exists(test_manga_folder, "1", "local")
    print(f"   Chapter exists: {exists}")
    print(f"   Images found: {images}")

    # Test 4: Check individual images
    print("\n4️⃣ Testing individual image checks...")
    for img in test_images:
        exists = await checker.check_image_exists(test_manga_folder, "1", img, "local")
        print(f"   {img}: {exists}")

    # Test 5: Update metadata
    print("\n5️⃣ Testing metadata update...")
    await checker.update_chapter_metadata(test_manga_folder, "1", test_images, "local")

    # Test 6: Check progress after metadata update
    print("\n6️⃣ Testing progress after metadata update...")
    progress = await checker.get_manga_progress(test_manga_folder, "local")
    print(f"   Progress: {progress}")

    # Test 7: Check cloud storage mode (should work even without actual cloud)
    print("\n7️⃣ Testing cloud storage mode...")
    cloud_exists, cloud_images = await checker.check_chapter_exists(test_manga_folder, "1", "cloud")
    print(f"   Cloud chapter exists: {cloud_exists}")
    print(f"   Cloud images: {cloud_images}")

    # Cleanup
    print("\n🧹 Cleaning up test files...")
    import shutil
    if os.path.exists(test_manga_folder):
        shutil.rmtree(test_manga_folder)

    print("✅ Test completed!")


async def test_manga_crawler_integration():
    """Test the integration with manga crawler"""
    print("\n🔗 Testing Manga Crawler Integration...")

    try:
        from services.manga_crawler import MangaCrawlerService

        async with MangaCrawlerService() as crawler:
            print("✅ MangaCrawlerService initialized successfully")
            print(f"   Existence checker: {crawler.existence_checker}")

            # Test existence checker methods
            test_folder = "test_integration"
            exists, images = await crawler.existence_checker.check_chapter_exists(test_folder, "1", "local")
            print(f"   Test chapter check: exists={exists}, images={images}")

    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Existence Checker Tests...")

    # Run tests
    asyncio.run(test_existence_checker())
    asyncio.run(test_manga_crawler_integration())

    print("\n🎉 All tests completed!")
