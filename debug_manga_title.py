"""
Debug script to check manga title processing
"""

import re
import os
from services.manga_crawler import MangaCrawlerService


def debug_manga_title():
    """Debug manga title processing"""
    print("🔍 Debugging Manga Title Processing...")

    # Test manga title from your log
    original_title = "Anh Hùng Giai Cấp Tư Sản"

    print(f"📚 Original title: '{original_title}'")

    # Test sanitization
    crawler = MangaCrawlerService()
    sanitized = crawler._sanitize_folder_name(original_title)
    print(f"🧹 Sanitized title: '{sanitized}'")

    # Test folder path
    manga_folder = os.path.join('downloads', sanitized)
    print(f"📁 Manga folder: '{manga_folder}'")

    # Test cloud storage key
    manga_title_for_cloud = os.path.basename(manga_folder)
    chapter_prefix = f"{manga_title_for_cloud}/Chapter_4/"
    print(f"☁️ Cloud chapter prefix: '{chapter_prefix}'")

    # Test individual image key
    image_key = f"{manga_title_for_cloud}/Chapter_4/068.jpg"
    print(f"🖼️ Cloud image key: '{image_key}'")

    # Check if folder exists locally
    if os.path.exists(manga_folder):
        print(f"✅ Local folder exists: {manga_folder}")

        # List contents
        try:
            contents = os.listdir(manga_folder)
            print(f"📋 Local folder contents: {contents}")

            # Check for Chapter_4
            chapter_4_path = os.path.join(manga_folder, "Chapter_4")
            if os.path.exists(chapter_4_path):
                print(f"✅ Chapter_4 folder exists locally")
                chapter_contents = os.listdir(chapter_4_path)
                print(f"📋 Chapter_4 contents: {chapter_contents[:10]}...")  # Show first 10
            else:
                print(f"❌ Chapter_4 folder does not exist locally")
        except Exception as e:
            print(f"⚠️ Error listing local folder: {str(e)}")
    else:
        print(f"❌ Local folder does not exist: {manga_folder}")

    print("\n🎯 Key Points:")
    print(f"   - Original title: {original_title}")
    print(f"   - Sanitized title: {sanitized}")
    print(f"   - Cloud prefix: {chapter_prefix}")
    print(f"   - Image key: {image_key}")


if __name__ == "__main__":
    debug_manga_title()
