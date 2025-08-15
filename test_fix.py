"""
Test the fixed manga crawler with the problematic request
"""

import requests
import json


def test_fixed_manga_crawler():
    """Test the manga crawler with the problematic request body"""
    base_url = "http://localhost:8000"

    print("🔧 Testing Fixed Manga Crawler")
    print("="*50)

    # The exact request body that was failing
    crawl_request = {
        "url": "https://nettruyenvia.com/truyen-tranh/bach-luyen-thanh-than",
        "max_chapters": 0,  # This was causing issues
        "start_chapter": 1,
        "end_chapter": 10,
        "custom_headers": {},
        "delay_between_chapters": 0
    }

    print("📤 Request body that was failing:")
    print(json.dumps(crawl_request, indent=2, ensure_ascii=False))

    try:
        print("\n🚀 Sending request...")
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=crawl_request,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Fixed response:")
            print("="*40)
            print(f"📊 Status: {result['status']}")
            print(f"📚 Manga: {result['manga_title']}")
            print(f"📁 Folder: {result['manga_folder']}")
            print(f"📋 Chapters found: {result['total_chapters_found']}")
            print(f"⬇️ Chapters downloaded: {result['chapters_downloaded']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"⏱️ Processing time: {result['processing_time_seconds']}s")

            if result['chapters']:
                print(f"\n📖 Downloaded chapters:")
                for ch in result['chapters']:
                    print(f"   Chapter {ch['chapter_number']}: {ch['images_count']} images")

            if result['errors']:
                print(f"\n⚠️ Errors:")
                for error in result['errors']:
                    print(f"   - {error}")

        else:
            print(f"\n❌ Request failed: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_better_request():
    """Test with a better request that should work well"""
    base_url = "http://localhost:8000"

    print("\n" + "="*60)
    print("💡 Testing with improved request...")

    # Better request - download first 2 available chapters
    improved_request = {
        "url": "https://nettruyenvia.com/truyen-tranh/bach-luyen-thanh-than",
        "max_chapters": 2,  # Limit to 2 chapters
        "start_chapter": 1,  # Will be auto-adjusted to available range
        "end_chapter": 10,   # Will be auto-adjusted
        "delay_between_chapters": 1.0
    }

    print("📤 Improved request:")
    print(json.dumps(improved_request, indent=2, ensure_ascii=False))

    try:
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=improved_request,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Improved result:")
            print(f"   Status: {result['status']}")
            print(f"   Chapters downloaded: {result['chapters_downloaded']}")
            print(f"   Total images: {result['total_images_downloaded']}")

        else:
            print(f"❌ Failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🧪 Testing manga crawler fixes")
    print("Testing the exact request body that was failing before")
    print("="*60)

    test_fixed_manga_crawler()
    test_better_request()

    print("\n" + "="*60)
    print("✅ If both tests show success, the bugs are fixed!")
    print("📋 Key fixes:")
    print("- max_chapters=0 now means 'no limit' instead of 'no chapters'")
    print("- Chapter range auto-adjusts to available chapters")
    print("- Better error messages and debugging info")
    print("="*60)
