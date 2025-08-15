"""
Test script for the manga crawler API
"""

import requests
import json
import time


def test_manga_info():
    """Test getting manga information without downloading"""
    base_url = "http://localhost:8000"

    print("🔍 Testing manga info endpoint...")

    # Test manga URL
    manga_url = "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich"

    try:
        response = requests.get(
            f"{base_url}/api/v1/manga/info",
            params={"url": manga_url},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Manga info retrieved successfully!")
            print(f"📚 Title: {result['manga_title']}")
            print(f"📋 Total chapters: {result['total_chapters']}")
            print(f"🔗 URL: {result['manga_url']}")

            if result.get('chapters'):
                print(f"\n📖 First few chapters:")
                for i, chapter in enumerate(result['chapters'][:5], 1):
                    print(f"  {i}. Chapter {chapter['chapter_number']}: {chapter['chapter_title']}")

            return True
        else:
            print(f"❌ Failed to get manga info: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error getting manga info: {str(e)}")
        return False


def test_manga_crawler():
    """Test the manga crawler with limited chapters"""
    base_url = "http://localhost:8000"

    print("\n" + "="*60)
    print("🚀 Testing manga crawler...")

    # Test with limited chapters for demo
    crawl_request = {
        "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
        "max_chapters": 2,  # Only download 2 chapters for testing
        "start_chapter": 1,
        "end_chapter": 2,
        "delay_between_chapters": 1.0,  # Reduced delay for testing
        "custom_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    }

    print(f"📤 Sending manga crawl request...")
    print(f"📚 Manga: {crawl_request['url']}")
    print(f"📋 Chapters: {crawl_request['max_chapters']} (from {crawl_request['start_chapter']} to {crawl_request['end_chapter']})")
    print(f"⏱️ Delay: {crawl_request['delay_between_chapters']}s between chapters")

    try:
        start_time = time.time()

        # This will take some time, so increase timeout
        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=crawl_request,
            timeout=300  # 5 minutes timeout
        )

        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print("\n🎉 Manga crawling completed!")
            print("="*50)

            print(f"📊 Status: {result['status']}")
            print(f"📚 Manga: {result['manga_title']}")
            print(f"📁 Folder: {result['manga_folder']}")
            print(f"📋 Chapters found: {result['total_chapters_found']}")
            print(f"⬇️ Chapters downloaded: {result['chapters_downloaded']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"⏱️ Processing time: {result['processing_time_seconds']}s")
            print(f"🌐 Request time: {end_time - start_time:.2f}s")

            if result['chapters']:
                print(f"\n📖 Chapter details:")
                for i, chapter in enumerate(result['chapters'], 1):
                    print(f"  Chapter {chapter['chapter_number']}:")
                    print(f"    📄 Title: {chapter['chapter_title']}")
                    print(f"    🖼️ Images: {chapter['images_count']}")
                    print(f"    ⏱️ Time: {chapter['processing_time_seconds']}s")

                    if chapter['images']:
                        print(f"    📸 Sample images:")
                        for j, img in enumerate(chapter['images'][:3], 1):
                            print(f"      {j}. {img['filename']} ({img['size_bytes']} bytes)")

                    if chapter['errors']:
                        print(f"    ⚠️ Errors: {len(chapter['errors'])}")
                    print()

            if result['errors']:
                print(f"⚠️ Global errors:")
                for error in result['errors']:
                    print(f"  - {error}")

            return True

        else:
            print(f"❌ Manga crawling failed: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out. Manga crawling takes time, try with fewer chapters.")
        return False
    except Exception as e:
        print(f"❌ Error during manga crawling: {str(e)}")
        return False


def test_manga_examples():
    """Test the examples endpoint"""
    base_url = "http://localhost:8000"

    print("\n" + "="*60)
    print("📋 Getting manga crawling examples...")

    try:
        response = requests.get(f"{base_url}/api/v1/manga/examples")

        if response.status_code == 200:
            examples = response.json()
            print("✅ Examples retrieved successfully!")

            for example_name, example_data in examples.items():
                print(f"\n📝 {example_name.replace('_', ' ').title()}:")
                print(f"   URL: {example_data['url'][:60]}...")
                print(f"   Max chapters: {example_data.get('max_chapters', 'All')}")
                print(f"   Start: {example_data.get('start_chapter', 1)}")
                print(f"   End: {example_data.get('end_chapter', 'Last')}")
                print(f"   Delay: {example_data.get('delay_between_chapters', 2)}s")

            return True
        else:
            print(f"❌ Failed to get examples: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error getting examples: {str(e)}")
        return False


def test_manga_health():
    """Test manga health check"""
    base_url = "http://localhost:8000"

    print("\n🔍 Testing manga health check...")

    try:
        response = requests.get(f"{base_url}/api/v1/manga/health")

        if response.status_code == 200:
            result = response.json()
            print("✅ Manga crawler is healthy!")
            print(f"Service: {result['service']}")
            print(f"Version: {result['version']}")
            print(f"Features: {result['features']}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Manga Crawler API Test Suite")
    print("="*60)
    print("This will test the manga crawling functionality.")
    print("Make sure the API server is running on http://localhost:8000")
    print("="*60)

    # Run all tests
    tests = [
        ("Health Check", test_manga_health),
        ("Manga Info", test_manga_info),
        ("Examples", test_manga_examples),
        ("Manga Crawler (Limited)", test_manga_crawler)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary:")
    print("="*60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! The manga crawler is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")

    print("\n💡 Usage Tips:")
    print("- Start with manga info to preview chapters before downloading")
    print("- Use small chapter limits for testing (max_chapters: 2-3)")
    print("- Check downloads/ folder for organized manga chapters")
    print("- Full manga series can take hours to download!")
    print("="*60)
