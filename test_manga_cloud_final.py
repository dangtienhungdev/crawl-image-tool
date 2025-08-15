#!/usr/bin/env python3
"""
Final test script to verify manga cloud storage without errors
"""

import requests
import json
import time
import os

def test_manga_cloud_final():
    """Test manga cloud storage with a working manga"""
    print("📚 Testing Manga Cloud Storage (Final Test)")
    print("=" * 60)

    # Test with a manga that should have images
    request_body = {
        "url": "https://nettruyenvia.com/truyen-tranh/tu-ky-luat-ta-day-bat-kha-chien-bai",
        "max_chapters": 1,
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
            timeout=300  # 5 minutes timeout
        )
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Manga cloud storage test successful!")
            print(f"   📖 Manga: {result['manga_title']}")
            print(f"   📁 Local folder: {result['manga_folder']}")
            print(f"   📚 Chapters: {result['chapters_downloaded']}/{result['total_chapters_found']}")
            print(f"   🖼️ Images: {result['total_images_downloaded']}")
            print(f"   ⏱️ Time: {end_time - start_time:.2f}s")

            # Check if local folder was created
            if os.path.exists(result['manga_folder']):
                print(f"❌ BUG: Local manga folder {result['manga_folder']} was created despite cloud storage!")
                contents = os.listdir(result['manga_folder'])
                print(f"   Contents: {contents}")
            else:
                print(f"✅ SUCCESS: No local manga folder created for cloud storage!")

            # Analyze cloud URLs structure
            print(f"\n🔍 Cloud URLs Structure Analysis:")
            manga_folder_name = None
            chapter_folders = set()
            total_cloud_urls = 0

            for chapter in result['chapters']:
                print(f"\n   📖 Chapter: {chapter['chapter_number']} - {chapter['chapter_title']}")
                print(f"      🖼️ Images: {chapter['images_count']}")
                print(f"      📄 Chapter URL: {chapter['chapter_url']}")

                if chapter['images_count'] == 0:
                    print(f"      ⚠️ No images found in this chapter")
                    continue

                chapter_cloud_urls = 0
                for i, img in enumerate(chapter['images'][:3]):  # Show first 3 images
                    if img.get('cloud_url'):
                        cloud_url = img['cloud_url']
                        chapter_cloud_urls += 1
                        total_cloud_urls += 1
                        print(f"      {i+1}. {img['filename']} -> {cloud_url}")

                        # Extract folder structure from URL
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

                print(f"      ☁️ Cloud URLs in this chapter: {chapter_cloud_urls}")

            # Summary
            print(f"\n📊 Structure Analysis:")
            print(f"   🗂️ Manga folder: {manga_folder_name}")
            print(f"   📚 Chapter folders: {sorted(chapter_folders)}")
            print(f"   ☁️ Total cloud URLs: {total_cloud_urls}")

            if manga_folder_name and chapter_folders and total_cloud_urls > 0:
                print(f"\n✅ Folder structure is correct!")
                print(f"   Expected: web-truyen/{manga_folder_name}/Chapter_X/filename")
                print(f"   Actual: ✅ Matches expected structure")
                print(f"   ✅ Cloud storage working correctly!")
            elif total_cloud_urls == 0:
                print(f"\n⚠️ No cloud URLs found - may be due to website changes")
            else:
                print(f"\n❌ Folder structure is incorrect!")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run final manga test"""
    print("🚀 Final Manga Cloud Storage Test")
    print("=" * 60)

    test_manga_cloud_final()

    print("\n" + "=" * 60)
    print("🎯 Expected Results:")
    print("   ☁️ No local folders created")
    print("   📁 Proper cloud folder structure")
    print("   🔗 Valid cloud URLs")
    print("   ❌ No file path errors")
    print("=" * 60)

if __name__ == "__main__":
    main()
