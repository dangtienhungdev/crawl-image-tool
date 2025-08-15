#!/usr/bin/env python3
"""
Test script for cloud storage functionality
"""

import requests
import json
import time

def test_wasabi_connection():
    """Test Wasabi S3 connection"""
    print("🔍 Testing Wasabi S3 connection...")

    try:
        response = requests.get('http://localhost:8000/api/v1/wasabi-test', timeout=10)
        result = response.json()

        if result['status'] == 'success':
            print(f"✅ Wasabi connection successful!")
            print(f"   Bucket: {result['bucket']}")
            print(f"   Endpoint: {result['endpoint']}")
            return True
        else:
            print(f"❌ Wasabi connection failed: {result['message']}")
            return False

    except Exception as e:
        print(f"❌ Error testing Wasabi connection: {str(e)}")
        return False

def test_local_storage():
    """Test local storage functionality"""
    print("\n📁 Testing local storage...")

    request_body = {
        "url": "https://nettruyenvia.com/",
        "max_images": 3,
        "include_base64": False,
        "use_selenium": False,
        "image_type": "local"
    }

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/crawl',
            json=request_body,
            timeout=60
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Local storage test successful!")
            print(f"   Downloaded: {result['images_downloaded']} images")
            print(f"   Folder: {result['folder_path']}")
            print(f"   Time: {end_time - start_time:.2f}s")

            # Check that no cloud URLs are present
            cloud_urls = [img for img in result['images'] if img.get('cloud_url')]
            if not cloud_urls:
                print("   ✅ No cloud URLs (as expected for local storage)")
            else:
                print(f"   ⚠️ Found {len(cloud_urls)} cloud URLs (unexpected)")

            return True
        else:
            print(f"❌ Local storage test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error testing local storage: {str(e)}")
        return False

def test_cloud_storage():
    """Test cloud storage functionality"""
    print("\n☁️ Testing cloud storage...")

    request_body = {
        "url": "https://nettruyenvia.com/",
        "max_images": 3,
        "include_base64": False,
        "use_selenium": False,
        "image_type": "cloud"
    }

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/crawl',
            json=request_body,
            timeout=120  # Longer timeout for cloud uploads
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cloud storage test successful!")
            print(f"   Downloaded: {result['images_downloaded']} images")
            print(f"   Folder: {result['folder_path']}")
            print(f"   Time: {end_time - start_time:.2f}s")

            # Check for cloud URLs
            cloud_urls = [img for img in result['images'] if img.get('cloud_url')]
            if cloud_urls:
                print(f"   ✅ Found {len(cloud_urls)} cloud URLs")
                for i, img in enumerate(cloud_urls[:2]):  # Show first 2
                    print(f"      {i+1}. {img['cloud_url']}")
            else:
                print("   ⚠️ No cloud URLs found (may indicate fallback to local)")

            return True
        else:
            print(f"❌ Cloud storage test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error testing cloud storage: {str(e)}")
        return False

def test_manga_cloud_storage():
    """Test manga crawling with cloud storage"""
    print("\n📚 Testing manga cloud storage...")

    request_body = {
        "url": "https://nettruyenvia.com/truyen-tranh/dai-phung-da-canh-nhan",
        "max_chapters": 1,  # Just 1 chapter for testing
        "image_type": "cloud",
        "delay_between_chapters": 1
    }

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/manga/crawl',
            json=request_body,
            timeout=180  # Longer timeout for manga + cloud uploads
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manga cloud storage test successful!")
            print(f"   Manga: {result['manga_title']}")
            print(f"   Chapters: {result['chapters_downloaded']}/{result['total_chapters_found']}")
            print(f"   Images: {result['total_images_downloaded']}")
            print(f"   Time: {end_time - start_time:.2f}s")

            # Check for cloud URLs in chapters
            total_cloud_urls = 0
            for chapter in result['chapters']:
                cloud_urls = [img for img in chapter['images'] if img.get('cloud_url')]
                total_cloud_urls += len(cloud_urls)

            if total_cloud_urls > 0:
                print(f"   ✅ Found {total_cloud_urls} cloud URLs across chapters")
            else:
                print("   ⚠️ No cloud URLs found in chapters")

            return True
        else:
            print(f"❌ Manga cloud storage test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error testing manga cloud storage: {str(e)}")
        return False

def main():
    """Run all cloud storage tests"""
    print("🚀 Cloud Storage Test Suite")
    print("=" * 50)

    # Test 1: Wasabi connection
    wasabi_ok = test_wasabi_connection()

    if not wasabi_ok:
        print("\n⚠️ Wasabi connection failed. Cloud storage tests may not work properly.")
        print("   Please check your .env configuration.")

    # Test 2: Local storage
    local_ok = test_local_storage()

    # Test 3: Cloud storage (only if Wasabi is working)
    cloud_ok = False
    if wasabi_ok:
        cloud_ok = test_cloud_storage()
    else:
        print("\n⏭️ Skipping cloud storage test (Wasabi not available)")

    # Test 4: Manga cloud storage (only if Wasabi is working)
    manga_cloud_ok = False
    if wasabi_ok:
        manga_cloud_ok = test_manga_cloud_storage()
    else:
        print("\n⏭️ Skipping manga cloud storage test (Wasabi not available)")

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Wasabi Connection: {'✅ PASS' if wasabi_ok else '❌ FAIL'}")
    print(f"   Local Storage: {'✅ PASS' if local_ok else '❌ FAIL'}")
    print(f"   Cloud Storage: {'✅ PASS' if cloud_ok else '❌ FAIL' if wasabi_ok else '⏭️ SKIP'}")
    print(f"   Manga Cloud Storage: {'✅ PASS' if manga_cloud_ok else '❌ FAIL' if wasabi_ok else '⏭️ SKIP'}")

    if wasabi_ok and local_ok and cloud_ok and manga_cloud_ok:
        print("\n🎉 All tests passed! Cloud storage is working correctly.")
    elif local_ok:
        print("\n✅ Local storage is working. Cloud storage needs configuration.")
    else:
        print("\n❌ Some tests failed. Please check the configuration and try again.")

if __name__ == "__main__":
    main()
