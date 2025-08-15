"""
Test manga crawler with simplified request - only URL required
"""

import requests
import json


def test_simple_manga_request():
    """Test manga crawler with only URL in request body"""
    base_url = "http://localhost:8000"

    print("🚀 Testing Simplified Manga Crawler")
    print("="*50)
    print("Request body contains ONLY the URL - all other fields are optional")

    # Simplest possible request - just URL
    simple_request = {
        "url": "https://nettruyenvia.com/truyen-tranh/bach-luyen-thanh-than"
    }

    print(f"\n📤 Simple request body:")
    print(json.dumps(simple_request, indent=2, ensure_ascii=False))
    print(f"\n🎯 Expected behavior: Crawl ALL available chapters")

    try:
        print(f"\n🚀 Sending request...")
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=simple_request,
            timeout=180  # 3 minutes for all chapters
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS! Simplified request works!")
            print("="*50)
            print(f"📊 Status: {result['status']}")
            print(f"📚 Manga: {result['manga_title']}")
            print(f"📁 Folder: {result['manga_folder']}")
            print(f"📋 Total chapters found: {result['total_chapters_found']}")
            print(f"⬇️ Chapters downloaded: {result['chapters_downloaded']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"⏱️ Processing time: {result['processing_time_seconds']}s")

            if result['chapters']:
                print(f"\n📖 Sample downloaded chapters:")
                for i, ch in enumerate(result['chapters'][:5], 1):
                    print(f"   {i}. Chapter {ch['chapter_number']}: {ch['images_count']} images")

                if len(result['chapters']) > 5:
                    print(f"   ... and {len(result['chapters']) - 5} more chapters")

            # Verify it downloaded ALL available chapters
            if result['chapters_downloaded'] == result['total_chapters_found']:
                print(f"\n🎉 PERFECT! Downloaded ALL {result['total_chapters_found']} available chapters!")
            else:
                print(f"\n⚠️ Downloaded {result['chapters_downloaded']}/{result['total_chapters_found']} chapters")

        else:
            print(f"\n❌ Request failed: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print(f"\n⏰ Request timed out (this is normal for large manga series)")
        print(f"The crawler is still working in the background")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_with_limit():
    """Test with just URL and max_chapters limit"""
    base_url = "http://localhost:8000"

    print(f"\n" + "="*60)
    print(f"🎯 Testing with URL + max_chapters limit")

    # Request with just URL and chapter limit
    limited_request = {
        "url": "https://nettruyenvia.com/truyen-tranh/bach-luyen-thanh-than",
        "max_chapters": 3  # Only this field + URL
    }

    print(f"\n📤 Limited request:")
    print(json.dumps(limited_request, indent=2, ensure_ascii=False))

    try:
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=limited_request,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Limited request works!")
            print(f"   Downloaded: {result['chapters_downloaded']} chapters")
            print(f"   Total images: {result['total_images_downloaded']}")

            if result['chapters_downloaded'] == 3:
                print(f"   🎯 Perfect! Respected the 3-chapter limit")

        else:
            print(f"❌ Failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🎯 Testing Simplified Manga Crawler API")
    print("This tests the new simplified request format")
    print("="*60)
    print("✨ New features:")
    print("- Only URL is required")
    print("- max_chapters, start_chapter, end_chapter are optional")
    print("- Default behavior: crawl ALL available chapters")
    print("="*60)

    test_simple_manga_request()
    test_with_limit()

    print(f"\n" + "="*60)
    print(f"💡 Usage Summary:")
    print(f'📝 Minimal request: {{"url": "https://manga-site.com/series"}}')
    print(f'📝 With limit: {{"url": "...", "max_chapters": 5}}')
    print(f"📝 All other fields (start_chapter, end_chapter, etc.) are optional")
    print(f"🎯 Default behavior: Download ALL available chapters")
    print(f"="*60)
