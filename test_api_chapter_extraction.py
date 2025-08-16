#!/usr/bin/env python3
"""
Test script for the new API-based chapter extraction
"""

import requests
import json
import time


def test_manga_crawl_with_api():
    """Test manga crawling with direct API call"""

    print("🚀 Testing Manga Crawling with Direct API Call")
    print("=" * 60)

    # Test with a manga that has many chapters
    request_body = {
        "url": "https://nettruyenvia.com/truyen-tranh/do-de-cua-ta-deu-la-dai-phan-phai",
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
            timeout=120
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
            # Show first 5 chapters
            for i, chapter in enumerate(result['chapters'][:5], 1):
                print(
                    f"   {i}. Chapter {chapter['chapter_number']}: {chapter['chapter_title']}")
                print(f"      🖼️ Images: {chapter['images_count']}")
                print(
                    f"      ⏱️ Time: {chapter['processing_time_seconds']:.2f}s")
                if chapter['errors']:
                    print(f"      ❌ Errors: {len(chapter['errors'])}")

            if len(result['chapters']) > 5:
                print(
                    f"   ... and {len(result['chapters']) - 5} more chapters")

            # Check if we got many chapters (indicating API worked)
            if result['total_chapters_found'] > 100:
                print(
                    f"\n🎉 SUCCESS: Found {result['total_chapters_found']} chapters!")
                print("✅ Direct API call is working perfectly!")
            elif result['total_chapters_found'] > 50:
                print(
                    f"\n✅ SUCCESS: Found {result['total_chapters_found']} chapters!")
                print("✅ Direct API call is working!")
            else:
                print(f"\n⚠️ Found {result['total_chapters_found']} chapters")
                print("ℹ️ This might be normal if the manga doesn't have many chapters")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_manga_info():
    """Test manga info endpoint to see total chapters"""

    print("\n\n📖 Testing Manga Info Endpoint")
    print("=" * 50)

    manga_url = "https://nettruyenvia.com/truyen-tranh/do-de-cua-ta-deu-la-dai-phan-phai"

    try:
        response = requests.get(
            f'http://localhost:8000/api/v1/manga/info?url={manga_url}'
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manga Info Retrieved Successfully!")
            print(f"📖 Title: {result['manga_title']}")
            print(f"📚 Total chapters: {result['total_chapters']}")

            # Show first few chapters
            print(f"\n📋 Sample Chapters:")
            for i, chapter in enumerate(result['chapters'][:5], 1):
                print(
                    f"   {i}. Chapter {chapter['chapter_number']}: {chapter['chapter_title']}")

            if len(result['chapters']) > 5:
                print(
                    f"   ... and {len(result['chapters']) - 5} more chapters")

        else:
            print(f"❌ Manga info request failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error getting manga info: {str(e)}")


if __name__ == "__main__":
    print("🎯 API Chapter Extraction Test Suite")
    print("=" * 60)
    print("This script tests the new direct API call for chapter extraction")
    print("Make sure the server is running on http://localhost:8000")
    print()

    # Run tests
    test_manga_info()
    test_manga_crawl_with_api()

    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
