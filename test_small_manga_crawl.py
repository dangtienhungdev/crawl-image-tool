#!/usr/bin/env python3
"""
Test script for small manga crawl with API
"""

import requests
import json
import time


def test_small_manga_crawl():
    """Test manga crawling with limited chapters"""

    print("🚀 Testing Small Manga Crawl with API")
    print("=" * 50)

    # Test with limited chapters
    request_body = {
        "url": "https://nettruyenvia.com/truyen-tranh/do-de-cua-ta-deu-la-dai-phan-phai",
        "max_chapters": 3,  # Only crawl 3 chapters
        "image_type": "local",
        "delay_between_chapters": 1.0
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/manga/crawl',
            json=request_body,
            timeout=60
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(
                f"\n✅ Success! Response received in {end_time - start_time:.2f}s")
            print(f"📊 Status: {result['status']}")
            print(f"📖 Manga: {result['manga_title']}")
            print(f"📚 Total chapters found: {result['total_chapters_found']}")
            print(f"📚 Chapters downloaded: {result['chapters_downloaded']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"⏱️ Total time: {result['processing_time_seconds']:.2f}s")

            # Show details for each chapter
            print(f"\n📋 Chapter Details:")
            for i, chapter in enumerate(result['chapters'], 1):
                print(
                    f"   {i}. Chapter {chapter['chapter_number']}: {chapter['chapter_title']}")
                print(f"      🖼️ Images: {chapter['images_count']}")
                print(
                    f"      ⏱️ Time: {chapter['processing_time_seconds']:.2f}s")
                if chapter['errors']:
                    print(f"      ❌ Errors: {len(chapter['errors'])}")

            # Check if API worked
            if result['total_chapters_found'] > 100:
                print(
                    f"\n🎉 SUCCESS: Found {result['total_chapters_found']} chapters!")
                print("✅ Direct API call is working perfectly!")
                print("✅ All chapters are now accessible!")
            else:
                print(f"\n⚠️ Found {result['total_chapters_found']} chapters")
                print("ℹ️ This might be normal if the manga doesn't have many chapters")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🎯 Small Manga Crawl Test")
    print("=" * 50)
    print("This script tests the new API with limited chapters")
    print("Make sure the server is running on http://localhost:8000")
    print()

    test_small_manga_crawl()

    print("\n" + "=" * 50)
    print("�� Test completed!")
