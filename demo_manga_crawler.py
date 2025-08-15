"""
Demo script for manga crawler - crawl 1 chapter only for demonstration
"""

import requests
import json
import time


def demo_manga_crawler():
    """Demo the manga crawler with just 1 chapter"""
    base_url = "http://localhost:8000"

    print("🚀 Demo: Manga Crawler - 1 Chapter Only")
    print("="*60)

    # Crawl request for just 1 chapter
    crawl_request = {
        "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
        "max_chapters": 1,  # Only 1 chapter for demo
        "start_chapter": 166,  # Start from chapter 166 (latest)
        "end_chapter": 166,   # End at chapter 166
        "delay_between_chapters": 0.5,
        "custom_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }

    print(f"📚 Manga: Học Cùng Em Gái, Không Cần Thận Trở Thành Vô Địch")
    print(f"📖 Chapter: {crawl_request['start_chapter']} (1 chapter only)")
    print(f"🚀 Starting crawl...")

    try:
        start_time = time.time()

        response = requests.post(
            f"{base_url}/api/v1/manga/crawl",
            json=crawl_request,
            timeout=180  # 3 minutes should be enough for 1 chapter
        )

        end_time = time.time()

        if response.status_code == 200:
            result = response.json()

            print("\n🎉 SUCCESS! Chapter downloaded!")
            print("="*50)
            print(f"📊 Status: {result['status']}")
            print(f"📚 Manga: {result['manga_title']}")
            print(f"📁 Saved to: {result['manga_folder']}")
            print(f"📖 Chapters processed: {result['chapters_downloaded']}")
            print(f"🖼️ Total images: {result['total_images_downloaded']}")
            print(f"⏱️ Processing time: {result['processing_time_seconds']}s")
            print(f"🌐 Request time: {end_time - start_time:.2f}s")

            if result['chapters']:
                chapter = result['chapters'][0]  # First (and only) chapter
                print(f"\n📖 Chapter {chapter['chapter_number']} Details:")
                print(f"   📄 Title: {chapter['chapter_title']}")
                print(f"   🖼️ Images downloaded: {chapter['images_count']}")
                print(f"   ⏱️ Chapter processing time: {chapter['processing_time_seconds']}s")

                if chapter['images']:
                    print(f"\n📸 Downloaded images:")
                    for i, img in enumerate(chapter['images'][:10], 1):  # Show first 10
                        print(f"     {i:2d}. {img['filename']} ({img['size_bytes']:,} bytes)")
                        if 'kcgsbok.com' in img['original_url']:
                            print(f"         🎯 SUCCESS: Bypassed kcgsbok.com blocking!")

                    if len(chapter['images']) > 10:
                        print(f"     ... and {len(chapter['images']) - 10} more images")

                if chapter['errors']:
                    print(f"\n⚠️ Chapter errors ({len(chapter['errors'])}):")
                    for error in chapter['errors'][:3]:
                        print(f"     - {error}")

            print(f"\n📁 Check folder: {result['manga_folder']}/Chapter_{crawl_request['start_chapter']}/")
            print("   You should see files like: 001.jpg, 002.jpg, 003.jpg, etc.")

            return True

        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout! The chapter might be very large or server is slow.")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🎯 This demo will download just 1 chapter to test the system")
    print("Make sure the server is running: python3 main.py")
    print("="*60)

    success = demo_manga_crawler()

    print("\n" + "="*60)
    if success:
        print("✅ Demo completed successfully!")
        print("\n💡 Next steps:")
        print("- Check the downloads folder for organized chapter images")
        print("- Try crawling more chapters by increasing max_chapters")
        print("- Use the full test script: python3 test_manga_crawler.py")
        print("- Access API docs: http://localhost:8000/docs")
    else:
        print("❌ Demo failed. Check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("- Make sure the server is running")
        print("- Check your internet connection")
        print("- Try a different manga URL")

    print("="*60)
