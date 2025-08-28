"""
Test cloud storage with actual environment variables
"""

import asyncio
import os
from dotenv import load_dotenv
from services.existence_checker import ExistenceChecker
from services.wasabi_service import WasabiService


async def test_cloud_with_real_env():
    """Test cloud storage with real environment variables"""
    print("☁️ Testing Cloud Storage with Real Environment...")

    # Load environment variables
    load_dotenv()

    # Check environment variables
    required_vars = ['ACCESS_KEY', 'SECRET_KEY', 'ENDPOINT_URL', 'BUCKET_NAME']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)}")  # Hide sensitive data

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return

    try:
        # Initialize services
        print("\n🔧 Initializing services...")
        checker = ExistenceChecker()
        wasabi = WasabiService()

        print("✅ Services initialized")

        # Test connection
        print("\n🔗 Testing Wasabi connection...")
        success, error = wasabi.test_connection()
        if success:
            print("✅ Wasabi connection successful")
        else:
            print(f"❌ Wasabi connection failed: {error}")
            return

        # Test manga folder
        test_manga = "Anh_Hùng_Giai_Cấp_Tư_Sản"
        test_manga_folder = os.path.join("downloads", test_manga)

        print(f"\n📁 Testing manga: {test_manga}")

        # Test 1: List objects with prefix
        print("\n1️⃣ Testing list_objects method...")
        manga_title = os.path.basename(test_manga_folder)
        chapter_prefix = f"{manga_title}/Chapter_4/"
        print(f"   Prefix: {chapter_prefix}")

        objects = wasabi.list_objects(prefix=chapter_prefix)
        print(f"   Objects found: {len(objects)}")
        if objects:
            print(f"   Sample objects: {objects[:5]}")
        else:
            print("   No objects found - this might be the issue!")

        # Test 2: Check specific images
        print("\n2️⃣ Testing specific image existence...")
        test_images = ["068.jpg", "069.jpg", "070.jpg", "071.jpg", "072.jpg"]
        for img in test_images:
            image_key = f"{manga_title}/Chapter_4/{img}"
            exists = wasabi.object_exists(image_key)
            print(f"   {image_key}: {exists}")

        # Test 3: Check with existence checker
        print("\n3️⃣ Testing with ExistenceChecker...")
        exists, images = await checker.check_chapter_exists(test_manga_folder, "4", "cloud")
        print(f"   Chapter 4 exists: {exists}")
        print(f"   Images found: {len(images)}")
        if images:
            print(f"   Sample images: {images[:5]}")

        # Test 4: Check individual images with existence checker
        print("\n4️⃣ Testing individual images with ExistenceChecker...")
        for img in test_images[:3]:
            exists = await checker.check_image_exists(test_manga_folder, "4", img, "cloud")
            print(f"   Chapter 4/{img}: {exists}")

        print("\n✅ Cloud storage test completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting Cloud Storage Test with Real Environment...")
    asyncio.run(test_cloud_with_real_env())
    print("\n�� Test completed!")
