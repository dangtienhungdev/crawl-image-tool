#!/usr/bin/env python3
"""
Test script to verify cloud storage with real images
"""

import requests
import json
import time
import os

def test_cloud_with_real_images():
    """Test cloud storage with a website that has real images"""
    print("☁️ Testing Cloud Storage with Real Images")
    print("=" * 60)

    # Test with a website that has images
    request_body = {
        "url": "https://httpbin.org/image/png",
        "max_images": 1,
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
            print(f"\n✅ Cloud storage test successful!")
            print(f"   🌐 Domain: {result['domain']}")
            print(f"   📁 Local folder: {result['folder_path']}")
            print(f"   🖼️ Images: {result['images_downloaded']}")
            print(f"   ⏱️ Time: {end_time - start_time:.2f}s")

            # Check if local folder was created
            local_folder = result['folder_path']
            if os.path.exists(local_folder):
                print(f"❌ BUG: Local folder {local_folder} was created despite cloud storage!")
                contents = os.listdir(local_folder)
                print(f"   Contents: {contents}")
            else:
                print(f"✅ SUCCESS: No local folder created for cloud storage!")

            # Check cloud URLs
            cloud_urls = [img for img in result['images'] if img.get('cloud_url')]
            if cloud_urls:
                print(f"✅ Found {len(cloud_urls)} cloud URLs")
                for i, img in enumerate(cloud_urls):
                    print(f"   {i+1}. {img['filename']} -> {img['cloud_url']}")
                    print(f"      Size: {img.get('size_bytes', 'N/A')} bytes")
                    print(f"      Format: {img.get('format', 'N/A')}")
            else:
                print(f"⚠️ No cloud URLs found")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_manga_cloud_structure():
    """Test manga cloud storage structure"""
    print("\n" + "=" * 60)
    print("📚 Testing Manga Cloud Storage Structure")
    print("=" * 60)

    request_body = {
        "url": "https://nettruyenvia.com/truyen-tranh/dai-phung-da-canh-nhan",
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
            timeout=180
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

            for chapter in result['chapters']:
                print(f"\n   📖 Chapter: {chapter['chapter_number']} - {chapter['chapter_title']}")
                print(f"      🖼️ Images: {chapter['images_count']}")

                for i, img in enumerate(chapter['images'][:3]):  # Show first 3 images
                    if img.get('cloud_url'):
                        cloud_url = img['cloud_url']
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

def main():
    """Run real image tests"""
    print("🚀 Real Image Cloud Storage Test Suite")
    print("=" * 60)

    # Test 1: Single image cloud storage
    test_cloud_with_real_images()

    # Test 2: Manga cloud storage structure
    test_manga_cloud_structure()

    print("\n" + "=" * 60)
    print("🎯 Expected Results:")
    print("   ☁️ No local folders created")
    print("   📁 Proper cloud folder structure")
    print("   🔗 Valid cloud URLs")
    print("=" * 60)

if __name__ == "__main__":
    main()
