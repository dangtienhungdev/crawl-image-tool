"""
Example usage script for the Image Crawler API
"""

import requests
import json
import time


def test_image_crawler():
    """Test the image crawler API with a sample website"""

    # API endpoint
    base_url = "http://localhost:8000"

    # Test health check first
    print("🔍 Testing health check...")
    try:
        health_response = requests.get(f"{base_url}/api/v1/health")
        if health_response.status_code == 200:
            print("✅ API is healthy!")
            print(json.dumps(health_response.json(), indent=2))
        else:
            print("❌ API health check failed!")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return

    print("\n" + "="*50)

    # Test image crawling
    print("🖼️ Testing image crawling...")

    crawl_request = {
        "url": "https://httpbin.org/html",  # Simple test page
        "max_images": 10,
        "include_base64": True,
        "use_selenium": False,  # Set to False for this simple test
        "custom_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }

    print(f"📤 Sending request to crawl: {crawl_request['url']}")
    print(f"⚙️ Settings: max_images={crawl_request['max_images']}, selenium={crawl_request['use_selenium']}")

    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/api/v1/crawl", json=crawl_request)
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print("✅ Crawling completed successfully!")
            print(f"⏱️ Request took: {end_time - start_time:.2f} seconds")
            print(f"🌐 Domain: {result['domain']}")
            print(f"📁 Folder: {result['folder_path']}")
            print(f"🔍 Images found: {result['total_images_found']}")
            print(f"⬇️ Images downloaded: {result['images_downloaded']}")
            print(f"⚡ Processing time: {result['processing_time_seconds']} seconds")

            if result['images']:
                print("\n📸 Downloaded images:")
                for i, img in enumerate(result['images'][:5], 1):  # Show first 5 images
                    print(f"  {i}. {img['filename']} ({img['size_bytes']} bytes)")
                    if img.get('width') and img.get('height'):
                        print(f"     Size: {img['width']}x{img['height']} pixels")

            if result['errors']:
                print(f"\n⚠️ Errors encountered: {len(result['errors'])}")
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"  - {error}")

        else:
            print(f"❌ Crawling failed with status code: {response.status_code}")
            print(f"Error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Image Crawler API Test")
    print("="*50)
    print("Make sure the API server is running with:")
    print("  python main.py")
    print("or")
    print("  uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    print("="*50)

    test_image_crawler()
