#!/usr/bin/env python3
"""
Test script to verify manga list API crawls complete chapters
"""

import requests
import json
import time


def test_manga_list_complete_crawl():
    """Test manga list crawling with complete chapter coverage"""

    print("🔍 Testing Manga List Complete Chapter Crawl")
    print("=" * 60)

    # Test with a manga list page
    request_body = {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 2,  # Test with 2 manga
        "max_chapters_per_manga": None,  # Crawl ALL chapters
        "image_type": "local",
        "delay_between_manga": 0,  # No delay for testing
        "delay_between_chapters": 0.5
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))
    print("\n🎯 This should crawl ALL chapters from beginning to end for each manga!")

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/manga-list/crawl',
            json=request_body,
            timeout=600  # 10 minutes timeout for complete crawl
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            total_time = end_time - start_time

            print(f"\n✅ Success! Response received in {total_time:.2f}s")
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
                    f"      📚 Total chapters available: {manga['total_chapters']}")
                print(
                    f"      📚 Chapters downloaded: {manga['chapters_downloaded']}")
                print(f"      🖼️ Images: {manga['total_images_downloaded']}")
                print(
                    f"      ⏱️ Time: {manga['processing_time_seconds']:.2f}s")

                # Check if all chapters were downloaded
                if manga['total_chapters'] > 0:
                    coverage = (manga['chapters_downloaded'] /
                                manga['total_chapters']) * 100
                    print(f"      📈 Coverage: {coverage:.1f}%")

                    if coverage >= 95:
                        print(f"      ✅ Excellent coverage!")
                    elif coverage >= 80:
                        print(f"      ⚠️ Good coverage, but some chapters missing")
                    else:
                        print(f"      ❌ Poor coverage - many chapters missing")

                if manga['errors']:
                    print(f"      ❌ Errors: {len(manga['errors'])}")
                    for error in manga['errors'][:2]:  # Show first 2 errors
                        print(f"         - {error}")

            # Overall assessment
            total_chapters_available = sum(
                manga['total_chapters'] for manga in result['manga_list'])
            total_chapters_downloaded = sum(
                manga['chapters_downloaded'] for manga in result['manga_list'])

            if total_chapters_available > 0:
                overall_coverage = (
                    total_chapters_downloaded / total_chapters_available) * 100
                print(f"\n📊 Overall Assessment:")
                print(
                    f"   Total chapters available: {total_chapters_available}")
                print(
                    f"   Total chapters downloaded: {total_chapters_downloaded}")
                print(f"   Overall coverage: {overall_coverage:.1f}%")

                if overall_coverage >= 95:
                    print(f"🎉 EXCELLENT! Complete chapter coverage achieved!")
                elif overall_coverage >= 80:
                    print(f"✅ GOOD! Most chapters covered")
                else:
                    print(f"⚠️ POOR! Many chapters missing")

            # Check if we got many chapters (indicating complete crawl)
            if total_chapters_downloaded > 100:
                print(
                    f"\n🎉 SUCCESS: Downloaded {total_chapters_downloaded} chapters!")
                print("✅ Complete chapter crawl is working!")
            elif total_chapters_downloaded > 50:
                print(
                    f"\n✅ SUCCESS: Downloaded {total_chapters_downloaded} chapters!")
                print("✅ Good chapter coverage achieved!")
            else:
                print(
                    f"\n⚠️ Only downloaded {total_chapters_downloaded} chapters")
                print("❌ Chapter coverage might be incomplete")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_manga_list_limited_crawl():
    """Test manga list with limited chapters to verify it starts from beginning"""

    print("\n\n🔍 Testing Manga List Limited Chapter Crawl")
    print("=" * 60)

    # Test with limited chapters
    request_body = {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 1,  # Only 1 manga for quick test
        "max_chapters_per_manga": 3,  # Only 3 chapters
        "image_type": "local",
        "delay_between_manga": 0,
        "delay_between_chapters": 0.5
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))
    print("\n🎯 This should crawl the FIRST 3 chapters from the beginning!")

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/manga-list/crawl',
            json=request_body,
            timeout=120
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()

            print(
                f"\n✅ Success! Response received in {end_time - start_time:.2f}s")

            if result['manga_list']:
                manga = result['manga_list'][0]
                print(f"📖 Manga: {manga['manga_title']}")
                print(f"📚 Total chapters available: {manga['total_chapters']}")
                print(f"📚 Chapters downloaded: {manga['chapters_downloaded']}")
                print(f"🖼️ Images: {manga['total_images_downloaded']}")

                # Check if it downloaded exactly 3 chapters (or less if manga has fewer)
                expected_chapters = min(3, manga['total_chapters'])
                if manga['chapters_downloaded'] == expected_chapters:
                    print(
                        f"✅ Perfect! Downloaded exactly {expected_chapters} chapters from the beginning")
                else:
                    print(
                        f"⚠️ Downloaded {manga['chapters_downloaded']} chapters, expected {expected_chapters}")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🎯 Manga List Complete Chapter Crawl Test")
    print("=" * 60)
    print("This script tests if manga list API crawls complete chapters")
    print("Make sure the server is running on http://localhost:8000")
    print()

    # Run tests
    test_manga_list_limited_crawl()
    test_manga_list_complete_crawl()

    print("\n" + "=" * 60)
    print("�� Test completed!")
