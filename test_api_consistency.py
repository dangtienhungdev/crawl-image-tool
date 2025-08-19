#!/usr/bin/env python3
"""
Test script to check API consistency for all manga
"""

import requests
import json
import time


def test_api_consistency():
    """Test API consistency across different manga"""

    print("🔍 Testing API Consistency for All Manga")
    print("=" * 60)

    # Test with different manga to ensure API works consistently
    test_manga = [
        {
            "url": "https://nettruyenvia.com/truyen-tranh/do-de-cua-ta-deu-la-dai-phan-phai",
            "name": "Đồ Đệ Của Ta Đều Là Đại Phản Phái"
        },
        {
            "url": "https://nettruyenvia.com/truyen-tranh/ta-co-the-don-ngo-vo-han",
            "name": "Ta Có Thể Đốn Ngộ Vô Hạn"
        },
        {
            "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
            "name": "Học Cùng Em Gái, Không Cần Thận Trở Thành Vô Địch"
        }
    ]

    results = []

    for i, manga in enumerate(test_manga, 1):
        print(f"\n📖 Testing manga {i}/{len(test_manga)}: {manga['name']}")
        print(f"🔗 URL: {manga['url']}")

        try:
            # Test manga info first
            info_response = requests.get(
                f'http://localhost:8000/api/v1/manga/info?url={manga["url"]}',
                timeout=30
            )

            if info_response.status_code == 200:
                info_result = info_response.json()
                total_chapters = info_result.get('total_chapters', 0)
                print(f"📊 Manga Info: {total_chapters} chapters found")

                # Test small crawl to see if API is used
                crawl_request = {
                    "url": manga['url'],
                    "max_chapters": 1,  # Only 1 chapter for quick test
                    "image_type": "local",
                    "delay_between_chapters": 0.5
                }

                print(f"🔄 Testing crawl with API...")
                crawl_response = requests.post(
                    'http://localhost:8000/api/v1/manga/crawl',
                    json=crawl_request,
                    timeout=60
                )

                if crawl_response.status_code == 200:
                    crawl_result = crawl_response.json()
                    chapters_found = crawl_result.get(
                        'total_chapters_found', 0)
                    chapters_downloaded = crawl_result.get(
                        'chapters_downloaded', 0)

                    print(f"✅ Crawl successful!")
                    print(f"   📚 Chapters found: {chapters_found}")
                    print(f"   📚 Chapters downloaded: {chapters_downloaded}")
                    print(
                        f"   🖼️ Images: {crawl_result.get('total_images_downloaded', 0)}")

                    # Check if API was used (should find many chapters)
                    if chapters_found > 50:
                        status = "✅ API Working"
                        print(f"   🎉 API is working perfectly!")
                    elif chapters_found > 20:
                        status = "⚠️ API Partial"
                        print(
                            f"   ⚠️ API found some chapters, but might be incomplete")
                    else:
                        status = "❌ API Failed"
                        print(f"   ❌ API might not be working properly")

                    results.append({
                        "manga": manga['name'],
                        "url": manga['url'],
                        "info_chapters": total_chapters,
                        "crawl_chapters_found": chapters_found,
                        "crawl_chapters_downloaded": chapters_downloaded,
                        "status": status
                    })

                else:
                    print(f"❌ Crawl failed: HTTP {crawl_response.status_code}")
                    results.append({
                        "manga": manga['name'],
                        "url": manga['url'],
                        "info_chapters": total_chapters,
                        "crawl_chapters_found": 0,
                        "crawl_chapters_downloaded": 0,
                        "status": "❌ Crawl Failed"
                    })
            else:
                print(f"❌ Manga info failed: HTTP {info_response.status_code}")
                results.append({
                    "manga": manga['name'],
                    "url": manga['url'],
                    "info_chapters": 0,
                    "crawl_chapters_found": 0,
                    "crawl_chapters_downloaded": 0,
                    "status": "❌ Info Failed"
                })

        except Exception as e:
            print(f"❌ Error testing {manga['name']}: {str(e)}")
            results.append({
                "manga": manga['name'],
                "url": manga['url'],
                "info_chapters": 0,
                "crawl_chapters_found": 0,
                "crawl_chapters_downloaded": 0,
                "status": f"❌ Error: {str(e)}"
            })

    # Summary
    print(f"\n📊 API Consistency Test Summary")
    print("=" * 60)

    for result in results:
        print(f"📖 {result['manga']}")
        print(f"   Status: {result['status']}")
        print(f"   Info chapters: {result['info_chapters']}")
        print(f"   Crawl found: {result['crawl_chapters_found']}")
        print(f"   Crawl downloaded: {result['crawl_chapters_downloaded']}")
        print()

    # Overall assessment
    working_apis = sum(1 for r in results if "✅" in r['status'])
    total_tests = len(results)

    print(f"🎯 Overall Assessment:")
    print(f"   Working APIs: {working_apis}/{total_tests}")
    print(f"   Success rate: {(working_apis/total_tests)*100:.1f}%")

    if working_apis == total_tests:
        print(f"🎉 All APIs are working consistently!")
    elif working_apis > 0:
        print(f"⚠️ Some APIs are working, but not all")
    else:
        print(f"❌ No APIs are working properly")


if __name__ == "__main__":
    print("🎯 API Consistency Test")
    print("=" * 60)
    print("This script tests if the API works consistently for all manga")
    print("Make sure the server is running on http://localhost:8000")
    print()

    test_api_consistency()

    print("\n" + "=" * 60)
    print("�� Test completed!")
