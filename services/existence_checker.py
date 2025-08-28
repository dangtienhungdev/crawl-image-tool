"""
Service for checking existence of manga chapters and images
"""

import os
import json
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import aiofiles
from services.wasabi_service import WasabiService


class ExistenceChecker:
    """Service to check if manga chapters and images already exist"""

    def __init__(self):
        self.wasabi_service = None
        self.metadata_file = "manga_metadata.json"

    async def initialize_wasabi(self):
        """Initialize Wasabi service for cloud storage checks"""
        try:
            self.wasabi_service = WasabiService()
            print(f"✅ Wasabi service initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ Failed to initialize Wasabi service: {str(e)}")
            self.wasabi_service = None
            return False

    def _get_metadata_path(self, manga_folder: str) -> str:
        """Get path to metadata file for a manga"""
        return os.path.join(manga_folder, self.metadata_file)

    async def load_manga_metadata(self, manga_folder: str) -> Dict:
        """Load existing metadata for a manga if it exists"""
        metadata_path = self._get_metadata_path(manga_folder)

        if os.path.exists(metadata_path):
            try:
                async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    return json.loads(content)
            except Exception as e:
                print(f"⚠️ Failed to load metadata: {str(e)}")

        return {}

    async def save_manga_metadata(self, manga_folder: str, metadata: Dict):
        """Save metadata for a manga"""
        metadata_path = self._get_metadata_path(manga_folder)

        try:
            # Ensure manga folder exists
            Path(manga_folder).mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"⚠️ Failed to save metadata: {str(e)}")

    async def check_chapter_exists(self, manga_folder: str, chapter_number: str, image_type: str = "local") -> Tuple[bool, List[str]]:
        """
        Check if a chapter already exists and return list of existing images

        Args:
            manga_folder: Base manga folder path
            chapter_number: Chapter number to check
            image_type: "local" or "cloud"

        Returns:
            Tuple of (exists, list_of_existing_images)
        """
        if image_type == "local":
            return await self._check_local_chapter(manga_folder, chapter_number)
        else:
            return await self._check_cloud_chapter(manga_folder, chapter_number)

    async def _check_local_chapter(self, manga_folder: str, chapter_number: str) -> Tuple[bool, List[str]]:
        """Check if chapter exists locally"""
        chapter_folder = os.path.join(manga_folder, f"Chapter_{chapter_number}")

        if not os.path.exists(chapter_folder):
            return False, []

        # Check for images in chapter folder
        existing_images = []
        try:
            for file in os.listdir(chapter_folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    existing_images.append(file)

            # Sort images by name (001.jpg, 002.jpg, etc.)
            existing_images.sort()

            return len(existing_images) > 0, existing_images
        except Exception as e:
            print(f"⚠️ Error checking local chapter {chapter_number}: {str(e)}")
            return False, []

    async def _check_cloud_chapter(self, manga_folder: str, chapter_number: str) -> Tuple[bool, List[str]]:
        """Check if chapter exists in cloud storage"""
        if not self.wasabi_service:
            success = await self.initialize_wasabi()
            if not success:
                print(f"⚠️ Cannot check cloud chapter {chapter_number}: Wasabi service not available")
                return False, []

        try:
            # Get manga title from folder path
            manga_title = os.path.basename(manga_folder)
            chapter_prefix = f"{manga_title}/Chapter_{chapter_number}/"

            print(f"🔍 Checking cloud chapter with prefix: {chapter_prefix}")

            # List objects in cloud storage for this chapter (not async)
            objects = self.wasabi_service.list_objects(prefix=chapter_prefix)

            print(f"📊 Found {len(objects)} objects in cloud storage")

            if not objects:
                return False, []

            # Extract image filenames
            existing_images = []
            for obj in objects:
                filename = os.path.basename(obj)
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    existing_images.append(filename)

            # Sort images by name
            existing_images.sort()

            print(f"🖼️ Found {len(existing_images)} images in cloud chapter {chapter_number}")
            return len(existing_images) > 0, existing_images
        except Exception as e:
            print(f"⚠️ Error checking cloud chapter {chapter_number}: {str(e)}")
            return False, []

    async def check_image_exists(self, manga_folder: str, chapter_number: str, filename: str, image_type: str = "local") -> bool:
        """
        Check if a specific image exists

        Args:
            manga_folder: Base manga folder path
            chapter_number: Chapter number
            filename: Image filename (e.g., "001.jpg")
            image_type: "local" or "cloud"

        Returns:
            True if image exists, False otherwise
        """
        if image_type == "local":
            return await self._check_local_image(manga_folder, chapter_number, filename)
        else:
            return await self._check_cloud_image(manga_folder, chapter_number, filename)

    async def _check_local_image(self, manga_folder: str, chapter_number: str, filename: str) -> bool:
        """Check if image exists locally"""
        image_path = os.path.join(manga_folder, f"Chapter_{chapter_number}", filename)
        return os.path.exists(image_path)

    async def _check_cloud_image(self, manga_folder: str, chapter_number: str, filename: str) -> bool:
        """Check if image exists in cloud storage"""
        if not self.wasabi_service:
            success = await self.initialize_wasabi()
            if not success:
                print(f"⚠️ Cannot check cloud image {filename}: Wasabi service not available")
                return False

        try:
            manga_title = os.path.basename(manga_folder)
            image_key = f"{manga_title}/Chapter_{chapter_number}/{filename}"

            print(f"🔍 Checking cloud image: {image_key}")

            # Check if object exists in cloud storage (not async)
            exists = self.wasabi_service.object_exists(image_key)
            print(f"   Result: {exists}")
            return exists
        except Exception as e:
            print(f"⚠️ Error checking cloud image {filename}: {str(e)}")
            return False

    async def get_existing_images_count(self, manga_folder: str, chapter_number: str, image_type: str = "local") -> int:
        """Get count of existing images in a chapter"""
        exists, images = await self.check_chapter_exists(manga_folder, chapter_number, image_type)
        return len(images) if exists else 0

    async def update_chapter_metadata(self, manga_folder: str, chapter_number: str, images: List[str], image_type: str = "local"):
        """Update metadata after downloading a chapter"""
        metadata = await self.load_manga_metadata(manga_folder)

        if "chapters" not in metadata:
            metadata["chapters"] = {}

        metadata["chapters"][chapter_number] = {
            "image_type": image_type,
            "images": images,
            "last_updated": str(Path().absolute()),
            "total_images": len(images)
        }

        await self.save_manga_metadata(manga_folder, metadata)

    async def get_manga_progress(self, manga_folder: str, image_type: str = "local") -> Dict:
        """Get overall progress of manga download"""
        metadata = await self.load_manga_metadata(manga_folder)

        if not metadata or "chapters" not in metadata:
            return {"total_chapters": 0, "completed_chapters": 0, "total_images": 0}

        chapters = metadata["chapters"]
        completed_chapters = len(chapters)
        total_images = sum(ch.get("total_images", 0) for ch in chapters.values())

        return {
            "total_chapters": completed_chapters,
            "completed_chapters": completed_chapters,
            "total_images": total_images,
            "chapters": chapters
        }
