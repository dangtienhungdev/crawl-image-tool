#!/usr/bin/env python3
"""
Test script to verify cloud-only storage without creating local folders
"""

import requests
import json
import time
import os

def test_cloud_only_storage():
    """Test that cloud storage doesn't create local folders"""
    print("☁️ Testing Cloud-Only Storage (No Local Folders)")
    print("=" * 60)

    # Test with a different domain to avoid existing folders
    request_body = {
        "url": "https://example.com",
        "max_images": 2,
        "include_base64": False,
        "use_selenium": False,
        "image_type": "cloud"
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    # Check if example.com folder exists before test
    example_folder = "downloads/example.com"
    if os.path.exists(example_folder):
        print(f"⚠️ Warning: {example_folder} already exists before test")
    else:
        print(f"✅ {example_folder} does not exist before test")

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
            if os.path.exists(example_folder):
                print(f"❌ BUG: Local folder {example_folder} was created despite cloud storage!")
                print(f"   Expected: No local folder for cloud storage")
                print(f"   Actual: Folder exists")

                # List contents
                contents = os.listdir(example_folder)
                print(f"   Contents: {contents}")
            else:
                print(f"✅ SUCCESS: No local folder created for cloud storage!")

            # Check cloud URLs
            cloud_urls = [img for img in result['images'] if img.get('cloud_url')]
            if cloud_urls:
                print(f"✅ Found {len(cloud_urls)} cloud URLs")
                for i, img in enumerate(cloud_urls[:2]):
                    print(f"   {i+1}. {img['cloud_url']}")
            else:
                print(f"⚠️ No cloud URLs found")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_local_only_storage():
    """Test that local storage creates folders"""
    print("\n" + "=" * 60)
    print("💾 Testing Local-Only Storage (With Local Folders)")
    print("=" * 60)

    request_body = {
        "url": "https://test-local.com",
        "max_images": 2,
        "include_base64": False,
        "use_selenium": False,
        "image_type": "local"
    }

    print("📤 Request body:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))

    # Check if test-local.com folder exists before test
    test_folder = "downloads/test-local.com"
    if os.path.exists(test_folder):
        print(f"⚠️ Warning: {test_folder} already exists before test")
    else:
        print(f"✅ {test_folder} does not exist before test")

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
            print(f"\n✅ Local storage test successful!")
            print(f"   🌐 Domain: {result['domain']}")
            print(f"   📁 Local folder: {result['folder_path']}")
            print(f"   🖼️ Images: {result['images_downloaded']}")
            print(f"   ⏱️ Time: {end_time - start_time:.2f}s")

            # Check if local folder was created
            if os.path.exists(test_folder):
                print(f"✅ SUCCESS: Local folder {test_folder} was created!")

                # List contents
                contents = os.listdir(test_folder)
                print(f"   Contents: {contents}")
            else:
                print(f"❌ BUG: Local folder {test_folder} was not created!")
                print(f"   Expected: Local folder for local storage")
                print(f"   Actual: No folder exists")

            # Check that no cloud URLs exist
            cloud_urls = [img for img in result['images'] if img.get('cloud_url')]
            if not cloud_urls:
                print(f"✅ No cloud URLs found (as expected for local storage)")
            else:
                print(f"❌ BUG: Found {len(cloud_urls)} cloud URLs in local storage!")

        else:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run storage tests"""
    print("🚀 Storage Mode Test Suite")
    print("=" * 60)

    # Test 1: Cloud-only storage
    test_cloud_only_storage()

    # Test 2: Local-only storage
    test_local_only_storage()

    print("\n" + "=" * 60)
    print("🎯 Expected Behavior:")
    print("   ☁️ Cloud Storage: No local folders, only cloud URLs")
    print("   💾 Local Storage: Local folders created, no cloud URLs")
    print("=" * 60)

if __name__ == "__main__":
    main()
