"""
Debug the Postman issue with manga crawling
"""

import requests
import json
import time


def test_problematic_request():
    """Test the exact request that's causing issues in Postman"""
    base_url = "http://localhost:8000"

    print("🔍 Debug: Postman Issue")
    print("="*50)

    # The request body that's causing issues (fixed JSON - no comments)
    request_body = {
        "url": "https://nettruyenvia.com/truyen-tranh/dai-phung-da-canh-nhan",
        "custom_headers": {},
        "delay_between_chapters": 0
    }

    print("📤 Testing request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    # First, test manga info to see what we're dealing with
    print("\n1️⃣ Getting manga info first...")
    try:
        info_response = requests.get(
            f"{base_url}/api/v1/manga/info",
            params={"url": request_body["url"]},
            timeout=30
        )

        if info_response.status_code == 200:
            info = info_response.json()
            print(f"✅ Manga: {info['manga_title']}")
            print(f"📋 Total chapters: {info['total_chapters']}")
            print(f"📖 Sample chapters: {[ch['chapter_number'] for ch in info['chapters'][:3]]}")

            if info['total_chapters'] > 50:
                print(f"⚠️ WARNING: This manga has {info['total_chapters']} chapters!")
                print(f"   This will take a VERY long time to download all chapters")
                print(f"   Estimated time: {info['total_chapters'] * 2} minutes or more")
        else:
            print(f"❌ Failed to get manga info: {info_response.status_code}")
            return

    except Exception as e:
        print(f"❌ Error getting manga info: {str(e)}")
        return

    # Now test the actual crawl request with a timeout
    print(f"\n2️⃣ Testing crawl request (with 60s timeout)...")
    print(f"⏰ This might take a long time if there are many chapters...")

    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=request_body,
            timeout=60  # 60 seconds timeout
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Request completed in {end_time - start_time:.1f} seconds")
            print(f"📊 Status: {result['status']}")
            print(f"📋 Chapters downloaded: {result['chapters_downloaded']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")

        else:
            print(f"\n❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print(f"\n⏰ Request timed out after 60 seconds")
        print(f"💡 This is likely because the manga has too many chapters")
        print(f"🔧 Solutions:")
        print(f"   1. Increase Postman timeout settings")
        print(f"   2. Add 'max_chapters': 5 to limit chapters")
        print(f"   3. The server is still processing - check downloads folder")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_with_limit():
    """Test with chapter limit to avoid timeout"""
    base_url = "http://localhost:8000"

    print(f"\n" + "="*60)
    print(f"🎯 Testing with chapter limit to avoid timeout")

    limited_request = {
        "url": "https://nettruyenvia.com/truyen-tranh/dai-phung-da-canh-nhan",
        "max_chapters": 3,  # Limit to 3 chapters
        "delay_between_chapters": 1
    }

    print(f"📤 Limited request:")
    print(json.dumps(limited_request, indent=2, ensure_ascii=False))

    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=limited_request,
            timeout=120
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Limited request completed in {end_time - start_time:.1f} seconds")
            print(f"📊 Status: {result['status']}")
            print(f"📋 Chapters downloaded: {result['chapters_downloaded']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"💡 This shows the API is working - the issue is timeout with large manga")

        else:
            print(f"❌ Failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🐛 Debugging Postman 'Sending Request...' Issue")
    print("="*60)
    print("Common causes:")
    print("1. JSON syntax error (comments // not allowed)")
    print("2. Request timeout (manga has too many chapters)")
    print("3. Postman timeout settings too low")
    print("="*60)

    test_problematic_request()
    test_with_limit()

    print(f"\n" + "="*60)
    print(f"🔧 Solutions for Postman:")
    print(f"1. Remove // comments from JSON body")
    print(f"2. Increase timeout in Postman settings")
    print(f"3. Add max_chapters limit for testing")
    print(f"4. Check if server is still processing in background")
    print(f"="*60)
