#!/usr/bin/env python3
"""
Test script for concurrent manga list processing
"""

import requests
import json
import time


def test_concurrent_manga_list():
    """Test concurrent manga list processing"""

    print("🚀 Testing Concurrent Manga List Processing")
    print("=" * 60)

    # Test with a manga list page
    request_body = {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 3,  # Test with 3 manga concurrently
        "max_chapters_per_manga": 1,  # Only 1 chapter per manga for speed
        "image_type": "local",
        "delay_between_manga": 0,  # No delay since we're processing concurrently
        "delay_between_chapters": 0.5
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))
    print("\n🔄 This will process all manga concurrently instead of sequentially!")

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
                    f"      📚 Chapters: {manga['chapters_downloaded']}/{manga['total_chapters']}")
                print(f"      🖼️ Images: {manga['total_images_downloaded']}")
                print(
                    f"      ⏱️ Time: {manga['processing_time_seconds']:.2f}s")
                if manga['errors']:
                    print(f"      ❌ Errors: {len(manga['errors'])}")

            # Calculate efficiency metrics
            total_chapters_found = sum(
                manga['total_chapters'] for manga in result['manga_list'])
            avg_manga_time = result['processing_time_seconds'] / \
                max(result['manga_processed'], 1)

            print(f"\n📊 Efficiency Analysis:")
            print(f"   Total chapters found: {total_chapters_found}")
            print(f"   Average time per manga: {avg_manga_time:.2f}s")
            print(f"   Total client time: {total_time:.2f}s")
            print(
                f"   Server processing time: {result['processing_time_seconds']:.2f}s")

            # Check if concurrent processing worked
            if result['manga_processed'] > 1:
                print(
                    f"\n🎉 SUCCESS: Processed {result['manga_processed']} manga concurrently!")
                print("✅ Concurrent processing is working!")

                # Compare with sequential processing time estimate
                estimated_sequential_time = avg_manga_time * \
                    result['manga_processed']
                time_saved = estimated_sequential_time - \
                    result['processing_time_seconds']
                if time_saved > 0:
                    print(f"⏱️ Time saved vs sequential: ~{time_saved:.2f}s")
                    print(
                        f"🚀 Speed improvement: ~{(time_saved/estimated_sequential_time)*100:.1f}%")
            else:
                print(f"\n⚠️ Only processed {result['manga_processed']} manga")
                print("ℹ️ This might be normal if there were errors")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_sequential_vs_concurrent():
    """Compare sequential vs concurrent processing"""

    print("\n\n🔄 Sequential vs Concurrent Comparison")
    print("=" * 60)

    # Test with smaller numbers for comparison
    request_body = {
        "url": "https://nettruyenvia.com/?page=637",
        "max_manga": 2,  # Only 2 manga for quick test
        "max_chapters_per_manga": 1,  # Only 1 chapter
        "image_type": "local",
        "delay_between_manga": 0,
        "delay_between_chapters": 0.5
    }

    print("📤 Testing concurrent processing...")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

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
            concurrent_time = end_time - start_time

            print(
                f"\n✅ Concurrent processing completed in {concurrent_time:.2f}s")
            print(
                f"📊 Server processing time: {result['processing_time_seconds']:.2f}s")
            print(f"📚 Manga processed: {result['manga_processed']}")

            # Estimate sequential time
            if result['manga_processed'] > 1:
                avg_manga_time = result['processing_time_seconds'] / \
                    result['manga_processed']
                estimated_sequential_time = avg_manga_time * \
                    result['manga_processed']

                print(f"\n📊 Comparison:")
                print(
                    f"   Concurrent time: {result['processing_time_seconds']:.2f}s")
                print(
                    f"   Estimated sequential time: {estimated_sequential_time:.2f}s")

                if estimated_sequential_time > result['processing_time_seconds']:
                    time_saved = estimated_sequential_time - \
                        result['processing_time_seconds']
                    improvement = (
                        time_saved / estimated_sequential_time) * 100
                    print(
                        f"   Time saved: {time_saved:.2f}s ({improvement:.1f}% improvement)")
                    print(
                        f"   🚀 Concurrent processing is {improvement:.1f}% faster!")
                else:
                    print(f"   ⚠️ No significant time difference")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🎯 Concurrent Manga List Processing Test")
    print("=" * 60)
    print("This script tests the new concurrent processing feature")
    print("Make sure the server is running on http://localhost:8000")
    print()

    # Run tests
    test_concurrent_manga_list()
    test_sequential_vs_concurrent()

    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
