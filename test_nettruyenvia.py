"""
Test script specifically for nettruyenvia.com to handle blocked images
"""

import requests
import json
import time


def test_nettruyenvia_crawler():
    """Test the image crawler API with nettruyenvia.com"""

    # API endpoint
    base_url = "http://localhost:8000"

    print("🔍 Testing nettruyenvia.com image crawling...")
    print("="*60)

    # Test image crawling with nettruyenvia.com
    crawl_request = {
        "url": "https://nettruyenvia.com/",
        "max_images": 20,  # Limit for testing
        "include_base64": True,
        "use_selenium": True,  # Enable Selenium for JavaScript rendering
        "custom_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    }

    print(f"📤 Sending request to crawl: {crawl_request['url']}")
    print(f"⚙️ Settings:")
    print(f"   - Max images: {crawl_request['max_images']}")
    print(f"   - Use Selenium: {crawl_request['use_selenium']}")
    print(f"   - Include base64: {crawl_request['include_base64']}")
    print("\n🚀 Starting crawl process...")

    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/api/v1/crawl", json=crawl_request, timeout=120)
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            print("✅ Crawling completed successfully!")
            print("="*50)
            print(f"⏱️ Total request time: {end_time - start_time:.2f} seconds")
            print(f"🌐 Domain: {result['domain']}")
            print(f"📁 Folder: {result['folder_path']}")
            print(f"🔍 Images found: {result['total_images_found']}")
            print(f"⬇️ Images downloaded: {result['images_downloaded']}")
            print(f"⚡ Processing time: {result['processing_time_seconds']} seconds")
            print(f"📊 Success rate: {result['images_downloaded']}/{result['total_images_found']} ({result['images_downloaded']/max(result['total_images_found'], 1)*100:.1f}%)")

            if result['images']:
                print(f"\n📸 Downloaded images (showing first 10):")
                for i, img in enumerate(result['images'][:10], 1):
                    print(f"  {i}. {img['filename']}")
                    print(f"     📏 Size: {img['size_bytes']} bytes", end="")
                    if img.get('width') and img.get('height'):
                        print(f" | {img['width']}x{img['height']} pixels", end="")
                    if img.get('format'):
                        print(f" | {img['format'].upper()}", end="")
                    print()
                    print(f"     🔗 Original: {img['original_url'][:80]}...")
                    print()

            if result['errors']:
                print(f"\n⚠️ Errors encountered ({len(result['errors'])}):")
                for i, error in enumerate(result['errors'][:5], 1):  # Show first 5 errors
                    print(f"  {i}. {error}")
                if len(result['errors']) > 5:
                    print(f"  ... and {len(result['errors']) - 5} more errors")

            # Analyze results
            print(f"\n📊 Analysis:")
            if result['images_downloaded'] > 0:
                print(f"✅ Successfully bypassed blocking for {result['images_downloaded']} images!")

                # Check if we got images from kcgsbok.com domain
                kcgsbok_images = [img for img in result['images'] if 'kcgsbok.com' in img['original_url']]
                if kcgsbok_images:
                    print(f"🎯 Successfully downloaded {len(kcgsbok_images)} images from kcgsbok.com domain!")
                    print("   This means the anti-blocking strategies are working!")
                else:
                    print("ℹ️ No images from kcgsbok.com domain found in this crawl")
            else:
                print("❌ No images were downloaded. The blocking might be very strong.")

        else:
            print(f"❌ Crawling failed with status code: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error response: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ Request timed out. The crawling process might be taking too long.")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")


def test_specific_image_url():
    """Test downloading a specific blocked image URL"""
    print("\n" + "="*60)
    print("🎯 Testing specific blocked image URL...")

    # This would be a manual test - we can't directly test the internal method
    # but we can see if our crawler handles it when crawling the full page
    blocked_url = "https://kcgsbok.com/nettruyen/thumb/citrus-plus.jpg"
    print(f"Target URL: {blocked_url}")
    print("This URL should be handled by our enhanced crawler when crawling the full page.")


if __name__ == "__main__":
    print("🚀 NetTruyenVia.com Image Crawler Test")
    print("="*60)
    print("This test will specifically check if we can bypass the blocking")
    print("on kcgsbok.com image URLs found on nettruyenvia.com")
    print("="*60)
    print("Make sure the API server is running with:")
    print("  python3 main.py")
    print("="*60)

    test_nettruyenvia_crawler()
    test_specific_image_url()

    print("\n" + "="*60)
    print("💡 Tips:")
    print("- Check the downloads/nettruyenvia.com/ folder for downloaded images")
    print("- If images are still blocked, the website might have stronger protection")
    print("- The crawler tries multiple strategies automatically")
    print("="*60)
