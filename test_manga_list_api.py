#!/usr/bin/env python3
"""
Test script for manga list API with new direct API logic
"""

import requests
import json
import time


def test_manga_list_crawl():
    """Test manga list crawling with new API logic"""

    print("🚀 Testing Manga List Crawling with Direct API")
    print("=" * 60)

    # Test with a manga list page
    request_body = {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 2,  # Only test with 2 manga
        "max_chapters_per_manga": 2,  # Only 2 chapters per manga
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
            print(f"📚 Total manga found: {result['total_manga_found']}")
            print(f"📚 Manga processed: {result['manga_processed']}")
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

            # Check if API worked well
            total_chapters_found = sum(
                manga['total_chapters'] for manga in result['manga_list'])
            if total_chapters_found > 50:
                print(
                    f"\n🎉 SUCCESS: Found {total_chapters_found} total chapters!")
                print("✅ Direct API call is working perfectly for manga list!")
            elif total_chapters_found > 20:
                print(
                    f"\n✅ SUCCESS: Found {total_chapters_found} total chapters!")
                print("✅ Direct API call is working for manga list!")
            else:
                print(f"\n⚠️ Found {total_chapters_found} total chapters")
                print("ℹ️ This might be normal if the manga don't have many chapters")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_manga_list_health():
    """Test manga list health endpoint"""

    print("\n\n🏥 Testing Manga List Health Endpoint")
    print("=" * 50)

    try:
        response = requests.get(
            'http://localhost:8000/api/v1/manga-list/health')

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed!")
            print(f"Status: {result.get('status', 'unknown')}")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_manga_list_examples():
    """Test manga list examples endpoint"""

    print("\n\n📖 Testing Manga List Examples Endpoint")
    print("=" * 50)

    try:
        response = requests.get(
            'http://localhost:8000/api/v1/manga-list/examples')

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Examples retrieved successfully!")
            print(f"Available examples: {len(result.get('examples', []))}")

            for i, example in enumerate(result.get('examples', [])[:3], 1):
                print(f"   {i}. {example.get('description', 'No description')}")
                print(f"      URL: {example.get('url', 'No URL')}")
        else:
            print(f"❌ Examples request failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🎯 Manga List API Test Suite")
    print("=" * 60)
    print("This script tests the manga list API with new direct API logic")
    print("Make sure the server is running on http://localhost:8000")
    print()

    # Run tests
    test_manga_list_health()
    test_manga_list_examples()
    test_manga_list_crawl()

    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
