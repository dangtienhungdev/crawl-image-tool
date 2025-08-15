"""
Debug script to test manga crawler with better error handling
"""

import requests
import json


def debug_manga_crawler():
    """Debug manga crawler with detailed output"""
    base_url = "http://localhost:8000"

    print("🔍 Debug: Manga Crawler")
    print("="*50)

    # Test with the manga that was failing
    manga_url = "https://nettruyenvia.com/truyen-tranh/bach-luyen-thanh-than"

    print(f"📚 Testing manga: {manga_url}")

    # First, get manga info to see what chapters are available
    print("\n1️⃣ Getting manga info...")
    try:
        info_response = requests.get(
            f"{base_url}/api/v1/manga/info",
            params={"url": manga_url},
            timeout=30
        )

        if info_response.status_code == 200:
            info_result = info_response.json()
            print(f"✅ Manga title: {info_result['manga_title']}")
            print(f"📋 Total chapters: {info_result['total_chapters']}")

            if info_result.get('chapters'):
                print(f"📖 Sample chapters:")
                for ch in info_result['chapters'][:5]:
                    print(f"   - Chapter {ch['chapter_number']}: {ch['chapter_title']}")

                # Get the first available chapter number
                first_chapter = info_result['chapters'][0]['chapter_number']
                print(f"\n💡 First available chapter: {first_chapter}")
        else:
            print(f"❌ Failed to get manga info: {info_response.status_code}")
            print(info_response.text)
            return

    except Exception as e:
        print(f"❌ Error getting manga info: {str(e)}")
        return

    # Now try to crawl with proper chapter range
    print(f"\n2️⃣ Testing crawl with first available chapter...")

    crawl_request = {
        "url": manga_url,
        "max_chapters": 1,  # Just 1 chapter for testing
        "start_chapter": None,  # Let it use default logic
        "end_chapter": None,
        "delay_between_chapters": 1.0
    }

    print(f"📤 Crawl request: {json.dumps(crawl_request, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=crawl_request,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Crawl result:")
            print(f"   Status: {result['status']}")
            print(f"   Chapters found: {result['total_chapters_found']}")
            print(f"   Chapters downloaded: {result['chapters_downloaded']}")
            print(f"   Total images: {result['total_images_downloaded']}")

            if result['chapters']:
                for ch in result['chapters']:
                    print(f"   📖 Chapter {ch['chapter_number']}: {ch['images_count']} images")

            if result['errors']:
                print(f"   ⚠️ Errors: {result['errors']}")

        else:
            print(f"❌ Crawl failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error during crawl: {str(e)}")


if __name__ == "__main__":
    print("🐛 Manga Crawler Debug Tool")
    print("This will help identify why manga crawling is failing")
    print("="*60)

    debug_manga_crawler()

    print("\n" + "="*60)
    print("💡 Tips:")
    print("- Check if chapters have unexpected numbering")
    print("- Look for filtering logic issues")
    print("- Verify chapter URL extraction")
    print("="*60)
