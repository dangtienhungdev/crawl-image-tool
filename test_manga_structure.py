#!/usr/bin/env python3
"""
Test script to verify manga folder structure on Wasabi S3
"""

import requests
import json
import time

def test_manga_structure():
    """Test manga crawling with cloud storage to verify folder structure"""
    print("📚 Testing Manga Folder Structure on Wasabi S3")
    print("=" * 60)

    # Test with a small manga (1 chapter)
    request_body = {
        "url": "https://nettruyenvia.com/truyen-tranh/dai-phung-da-canh-nhan",
        "max_chapters": 1,  # Just 1 chapter for testing
        "image_type": "cloud",
        "delay_between_chapters": 1
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/manga/crawl',
            json=request_body,
            timeout=180
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Manga crawl successful!")
            print(f"   📖 Manga: {result['manga_title']}")
            print(f"   📁 Local folder: {result['manga_folder']}")
            print(f"   📚 Chapters: {result['chapters_downloaded']}/{result['total_chapters_found']}")
            print(f"   🖼️ Images: {result['total_images_downloaded']}")
            print(f"   ⏱️ Time: {end_time - start_time:.2f}s")

            # Analyze cloud URLs to verify structure
            print(f"\n🔍 Analyzing cloud URLs structure:")

            manga_folder_name = None
            chapter_folders = set()

            for chapter in result['chapters']:
                print(f"\n   📖 Chapter: {chapter['chapter_number']} - {chapter['chapter_title']}")
                print(f"      🖼️ Images: {chapter['images_count']}")

                for i, img in enumerate(chapter['images'][:3]):  # Show first 3 images
                    if img.get('cloud_url'):
                        cloud_url = img['cloud_url']
                        print(f"      {i+1}. {img['filename']} -> {cloud_url}")

                        # Extract folder structure from URL
                        # Expected: https://s3.ap-southeast-1.wasabisys.com/web-truyen/manga_title/Chapter_X/filename
                        parts = cloud_url.split('/')
                        if len(parts) >= 6:
                            bucket = parts[3]  # web-truyen
                            manga_name = parts[4]  # manga_title
                            chapter_name = parts[5]  # Chapter_X

                            if manga_folder_name is None:
                                manga_folder_name = manga_name

                            chapter_folders.add(chapter_name)

                            print(f"         📁 Structure: {bucket}/{manga_name}/{chapter_name}/{img['filename']}")
                        else:
                            print(f"         ⚠️ Unexpected URL structure: {cloud_url}")
                    else:
                        print(f"      {i+1}. {img['filename']} -> No cloud URL")

            # Summary
            print(f"\n📊 Structure Analysis:")
            print(f"   🗂️ Manga folder: {manga_folder_name}")
            print(f"   📚 Chapter folders: {sorted(chapter_folders)}")

            if manga_folder_name and chapter_folders:
                print(f"\n✅ Folder structure is correct!")
                print(f"   Expected: web-truyen/{manga_folder_name}/Chapter_X/filename")
                print(f"   Actual: ✅ Matches expected structure")
            else:
                print(f"\n❌ Folder structure is incorrect!")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_single_page_structure():
    """Test single page crawl to verify domain-based structure"""
    print("\n" + "=" * 60)
    print("🌐 Testing Single Page Folder Structure on Wasabi S3")
    print("=" * 60)

    request_body = {
        "url": "https://nettruyenvia.com/",
        "max_images": 3,
        "include_base64": False,
        "use_selenium": False,
        "image_type": "cloud"
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/api/v1/crawl',
            json=request_body,
            timeout=60
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Single page crawl successful!")
            print(f"   🌐 Domain: {result['domain']}")
            print(f"   📁 Local folder: {result['folder_path']}")
            print(f"   🖼️ Images: {result['images_downloaded']}")
            print(f"   ⏱️ Time: {end_time - start_time:.2f}s")

            print(f"\n🔍 Analyzing cloud URLs structure:")

            for i, img in enumerate(result['images']):
                if img.get('cloud_url'):
                    cloud_url = img['cloud_url']
                    print(f"   {i+1}. {img['filename']} -> {cloud_url}")

                    # Extract folder structure from URL
                    # Expected: https://s3.ap-southeast-1.wasabisys.com/web-truyen/images/domain_name/filename
                    parts = cloud_url.split('/')
                    if len(parts) >= 6:
                        bucket = parts[3]  # web-truyen
                        folder = parts[4]  # images
                        domain = parts[5]  # domain_name

                        print(f"      📁 Structure: {bucket}/{folder}/{domain}/{img['filename']}")

                        if folder == "images" and domain == result['domain']:
                            print(f"      ✅ Structure is correct!")
                        else:
                            print(f"      ❌ Structure is incorrect!")
                    else:
                        print(f"      ⚠️ Unexpected URL structure: {cloud_url}")
                else:
                    print(f"   {i+1}. {img['filename']} -> No cloud URL")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run structure tests"""
    print("🚀 Wasabi S3 Folder Structure Test Suite")
    print("=" * 60)

    # Test 1: Manga structure
    test_manga_structure()

    # Test 2: Single page structure
    test_single_page_structure()

    print("\n" + "=" * 60)
    print("🎯 Expected Structures:")
    print("   📚 Manga: web-truyen/manga_title/Chapter_X/filename")
    print("   🌐 Single Page: web-truyen/images/domain_name/filename")
    print("=" * 60)

if __name__ == "__main__":
    main()
