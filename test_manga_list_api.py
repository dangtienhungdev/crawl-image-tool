#!/usr/bin/env python3
"""
Test script for Manga List Crawling API

This script tests the new manga list crawling functionality.
"""

import requests
import json
import time


def test_manga_list_api():
    """Test the manga list crawling API"""

    print("🚀 Testing Manga List Crawling API")
    print("=" * 60)

    # Test 1: Basic manga list crawl with local storage
    print("\n📚 Test 1: Basic manga list crawl (local storage)")
    print("-" * 40)

    request_body = {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 2,  # Limit to 2 manga for testing
        "max_chapters_per_manga": 1,  # Limit to 1 chapter per manga
        "image_type": "local",
        "delay_between_manga": 2.0,
        "delay_between_chapters": 1.0
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/manga-list/crawl',
            json=request_body,
            timeout=300  # 5 minutes timeout
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(
                f"\n✅ Success! Response received in {end_time - start_time:.2f}s")
            print(f"📊 Status: {result['status']}")
            print(f"📚 Manga found: {result['total_manga_found']}")
            print(f"📖 Manga processed: {result['manga_processed']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"⏱️ Total time: {result['processing_time_seconds']:.2f}s")

            # Show details for each manga
            print(f"\n📋 Manga Details:")
            for i, manga in enumerate(result['manga_list'], 1):
                print(f"   {i}. {manga['manga_title']}")
                print(f"      📊 Status: {manga['status']}")
                print(
                    f"      📚 Chapters: {manga['chapters_downloaded']}/{manga['total_chapters']}")
                print(f"      🖼️ Images: {manga['total_images_downloaded']}")
                print(
                    f"      ⏱️ Time: {manga['processing_time_seconds']:.2f}s")
                if manga['errors']:
                    print(f"      ❌ Errors: {len(manga['errors'])}")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Test 2: Health check
    print("\n\n🏥 Test 2: Health check")
    print("-" * 40)

    try:
        response = requests.get(
            'http://localhost:8000/api/v1/manga-list/health')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed: {result}")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

    # Test 3: Examples endpoint
    print("\n\n📖 Test 3: Examples endpoint")
    print("-" * 40)

    try:
        response = requests.get(
            'http://localhost:8000/api/v1/manga-list/examples')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Examples retrieved successfully")
            print(f"📋 Available examples: {list(result['examples'].keys())}")
        else:
            print(f"❌ Examples request failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Examples error: {str(e)}")


def test_cloud_storage():
    """Test manga list crawling with cloud storage"""

    print("\n\n☁️ Test 4: Cloud storage manga list crawl")
    print("=" * 60)

    request_body = {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 1,  # Just 1 manga for cloud test
        "max_chapters_per_manga": 1,  # Just 1 chapter
        "image_type": "cloud",
        "delay_between_manga": 2.0,
        "delay_between_chapters": 1.0
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/manga-list/crawl',
            json=request_body,
            timeout=300
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Cloud storage test successful!")
            print(f"📊 Status: {result['status']}")
            print(f"📚 Manga processed: {result['manga_processed']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"⏱️ Time: {end_time - start_time:.2f}s")

            # Check if any manga were processed
            if result['manga_list']:
                manga = result['manga_list'][0]
                print(f"\n📖 Manga: {manga['manga_title']}")
                print(f"📊 Status: {manga['status']}")
                print(
                    f"🖼️ Images uploaded to cloud: {manga['total_images_downloaded']}")

        else:
            print(f"❌ Cloud storage test failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Cloud storage test error: {str(e)}")


def main():
    """Main test function"""
    print("🎯 Manga List Crawling API Test Suite")
    print("=" * 60)
    print("This script tests the new manga list crawling functionality.")
    print("Make sure the server is running on http://localhost:8000")
    print()

    # Run tests
    test_manga_list_api()
    test_cloud_storage()

    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
    print("Check the results above to verify the API is working correctly.")


if __name__ == "__main__":
    main()
