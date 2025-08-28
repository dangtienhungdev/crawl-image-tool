# 🖼️ Image Crawler API

A powerful FastAPI service for crawling and downloading images from websites with advanced features including lazy loading support, JavaScript rendering, base64 image extraction, and comprehensive manga management.

## ✨ Features

### 🖼️ Single Page Image Crawling

- 🌐 **Standard Image Crawling**: Extract images from HTML `<img>` tags
- 🔄 **Lazy Loading Support**: Handle lazy-loaded images using Selenium WebDriver
- 📱 **JavaScript Rendering**: Process dynamically loaded content
- 🎨 **Base64 Images**: Extract and save base64 encoded images
- 📂 **Organized Storage**: Automatically save images in domain-named folders
- ☁️ **Cloud Storage Support**: Upload images to Wasabi S3 cloud storage
- ⚡ **Concurrent Downloads**: Fast parallel image downloading with aiohttp
- 📊 **Status Tracking**: Monitor crawling progress and status

### 📚 Full Manga Series Crawling

- 📖 **Complete Series Download**: Crawl entire manga series with all chapters
- 🗂️ **Chapter Organization**: Automatic folder structure (Chapter_1/, Chapter_2/, etc.)
- 🔢 **Sequential Naming**: Images named as 001.jpg, 002.jpg, etc.
- 🎯 **Chapter Range Control**: Download specific chapter ranges or limits
- ⏱️ **Rate Limiting**: Configurable delays between chapter downloads
- 🛡️ **Hotlink Protection Bypass**: Proper Referer headers for blocked images
- ☁️ **Cloud Storage Support**: Upload manga images to Wasabi S3 cloud storage
- ℹ️ **Manga Information**: Preview manga details before downloading
- 🚫 **Smart Duplicate Detection**: Automatically skip existing chapters and images
- 📊 **Progress Tracking**: Monitor download progress with metadata tracking
- 🔄 **Resume Support**: Resume interrupted downloads without re-downloading

### 📋 Manga List Batch Crawling

- 📚 **Batch Processing**: Crawl entire pages of manga lists (e.g., https://nettruyenvia.com/?page=637)
- 🔄 **Automatic Discovery**: Extract all manga URLs from list pages automatically
- ⚙️ **Configurable Limits**: Set limits for manga count and chapters per manga
- 🕐 **Smart Delays**: Configurable delays between manga and chapter downloads
- 📊 **Comprehensive Reporting**: Detailed statistics for each manga processed
- ☁️ **Cloud Storage Support**: Upload all manga images to Wasabi S3 cloud storage

### 🔧 Advanced Features

- 🛡️ **Robust Error Handling**: Comprehensive error reporting and recovery
- 🎯 **Clean Architecture**: Well-structured codebase with separation of concerns
- 🚫 **Anti-Bot Bypass**: Multiple strategies to handle blocked images
- 🔍 **Health Monitoring**: Service health checks and status endpoints
- 📝 **Detailed Logging**: Comprehensive logging for debugging and monitoring

### 🚫 Smart Duplicate Detection

- 🔍 **Chapter-Level Checking**: Automatically detects existing chapters and skips them
- 🖼️ **Image-Level Checking**: Checks individual images within chapters to avoid re-downloading
- 💾 **Dual Storage Support**: Works with both local storage and cloud storage (Wasabi S3)
- 📊 **Metadata Tracking**: Maintains `manga_metadata.json` files for progress tracking
- ⚡ **Performance Optimization**: Significantly faster re-runs by skipping existing content
- 🔄 **Resume Capability**: Resume interrupted downloads from where they left off
- 📈 **Progress Monitoring**: Track download progress across multiple sessions

## 🏗️ Project Structure

```
crawl-image-tool/
├── .git/                          # Git repository
├── .env                           # Environment variables
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore file
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── main.py                        # FastAPI application entry point
├── system.md                      # System architecture documentation
├── controllers/                   # Business logic controllers
│   ├── __init__.py               # Package initialization
│   ├── image_controller.py       # Image controller logic
│   ├── manga_controller.py       # Manga controller logic
│   └── manga_list_controller.py  # Manga list controller
├── services/                      # Core services and utilities
│   ├── __init__.py               # Package initialization
│   ├── image_crawler.py          # Image crawling service
│   ├── manga_crawler.py          # Manga crawling service
│   ├── manga_list_crawler.py     # Manga list crawling service
│   └── wasabi_service.py         # Wasabi storage service
├── routes/                        # FastAPI route definitions
│   ├── __init__.py               # Package initialization
│   ├── image_routes.py           # Image API endpoints
│   ├── manga_routes.py           # Manga API endpoints
│   └── manga_list_routes.py      # Manga list API endpoints
├── models/                        # Data models and schemas
│   ├── __init__.py               # Package initialization
│   └── schemas.py                # Data schemas and models
└── downloads/                     # Downloaded images storage (auto-created)
```

## 🚫 Smart Duplicate Detection

The manga crawler now includes intelligent duplicate detection to avoid re-downloading existing content:

### How It Works

1. **Chapter-Level Detection**: Before processing a chapter, the system checks if it already exists
2. **Image-Level Detection**: For each image, it verifies if the file already exists locally or in cloud storage
3. **Metadata Tracking**: Progress is tracked in `manga_metadata.json` files for each manga
4. **Automatic Skipping**: Existing chapters and images are automatically skipped during re-runs

### Benefits

- ⚡ **Faster Re-runs**: Skip existing content automatically
- 💾 **Storage Efficiency**: No duplicate files created
- 🔄 **Resume Support**: Continue interrupted downloads seamlessly
- 📊 **Progress Tracking**: Monitor download status across sessions
- 🌐 **Cloud Compatible**: Works with both local and cloud storage

### Example Usage

```bash
# First run - downloads all chapters
curl -X POST "http://localhost:8000/api/v1/manga/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://nettruyenvia.com/truyen-tranh/example", "image_type": "local"}'

# Second run - automatically skips existing chapters
curl -X POST "http://localhost:8000/api/v1/manga/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://nettruyenvia.com/truyen-tranh/example", "image_type": "local"}'

# Check progress
curl "http://localhost:8000/api/v1/manga/progress/example_manga_title?image_type=local"
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Chrome or Chromium browser (for Selenium)
- ChromeDriver (will be auto-installed via webdriver-manager)

### Installation

1. **Clone or download the project**:

   ```bash
   cd crawl-image-tool
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your Wasabi S3 credentials if using cloud storage
   ```

### Running the Application

1. **Start the FastAPI server**:

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the API**:
   - API Server: http://localhost:8000
   - Interactive Documentation: http://localhost:8000/docs
   - Alternative Documentation: http://localhost:8000/redoc

## 📖 API Reference

### Base URL
All API endpoints are prefixed with `/api/v1`

### 🖼️ Image Crawling Endpoints

#### Crawl Images from a Website

**Endpoint**: `POST /api/v1/crawl`

**Request Body**:

```json
{
    "url": "https://nettruyenvia.com/",
    "max_images": 100,
    "include_base64": true,
    "use_selenium": true,
    "image_type": "local",
    "custom_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}
```

**Parameters**:

- `url` (required): Website URL to crawl
- `max_images` (optional, default: 100): Maximum number of images to download
- `include_base64` (optional, default: true): Whether to extract base64 encoded images
- `use_selenium` (optional, default: true): Whether to use Selenium for JavaScript rendering
- `image_type` (optional, default: "local"): Storage type - "local" for local files, "cloud" for Wasabi S3
- `custom_headers` (optional): Custom HTTP headers for requests

**Response**:

```json
{
    "status": "success",
    "url": "https://nettruyenvia.com/",
    "domain": "nettruyenvia.com",
    "folder_path": "downloads/nettruyenvia_com",
    "total_images_found": 25,
    "images_downloaded": 23,
    "images": [
        {
            "original_url": "https://nettruyenvia.com/image1.jpg",
            "local_path": "downloads/nettruyenvia_com/image1.jpg",
            "filename": "image1.jpg",
            "cloud_url": "https://s3.ap-southeast-1.wasabisys.com/web-truyen/images/nettruyenvia_com/image1.jpg",
            "size_bytes": 15420,
            "width": 800,
            "height": 600,
            "format": "jpeg"
        }
    ],
    "errors": [],
    "processing_time_seconds": 12.34
}
```

#### Get Crawling Status

**Endpoint**: `GET /api/v1/status/{url:path}`

**Description**: Get the current status and information for a previously crawled URL

**Response**:
```json
{
    "url": "https://nettruyenvia.com/",
    "status": "completed",
    "last_crawled": "2024-01-15T10:30:00Z",
    "total_images": 25,
    "successful_downloads": 23,
    "failed_downloads": 2
}
```

#### Health Check

**Endpoint**: `GET /api/v1/health`

**Response**:

```json
{
    "status": "healthy",
    "service": "Image Crawler API",
    "version": "1.0.0"
}
```

### 📚 Manga Management Endpoints

#### Crawl Entire Manga Series

**Endpoint**: `POST /api/v1/manga/crawl`

**Request Body**:

```json
{
    "url": "https://nettruyenvia.com/truyen-tranh/hoc-cung-em-gai-khong-can-than-tro-thanh-vo-dich",
    "max_chapters": 10,
    "start_chapter": 1,
    "end_chapter": 10,
    "image_type": "local",
    "delay_between_chapters": 2.0,
    "custom_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}
```

**Parameters**:

- `url` (required): URL of the manga series page
- `max_chapters` (optional): Maximum number of chapters to download
- `start_chapter` (optional, default: 1): Chapter to start from
- `end_chapter` (optional): Chapter to end at
- `image_type` (optional, default: "local"): Storage type - "local" for local files, "cloud" for Wasabi S3
- `delay_between_chapters` (optional, default: 2.0): Delay between downloads
- `custom_headers` (optional): Custom HTTP headers

**Response**:

```json
{
    "status": "success",
    "manga_url": "https://nettruyenvia.com/truyen-tranh/...",
    "manga_title": "Học Cùng Em Gái, Không Cần Thận Trở Thành Vô Địch",
    "folder_path": "downloads/Hoc_Cung_Em_Gai_Khong_Can_Than_Tro_Thanh_Vo_Dich",
    "total_chapters": 20,
    "chapters_downloaded": 10,
    "total_images_downloaded": 150,
    "chapters": [
        {
            "chapter_number": "1",
            "chapter_title": "Chapter 1",
            "images_downloaded": 15,
            "status": "success"
        }
    ],
    "processing_time_seconds": 120.5
}
```

**Example Folder Structure**:

```
downloads/
└── Hoc_Cung_Em_Gai_Khong_Can_Than_Tro_Thanh_Vo_Dich/
    ├── Chapter_1/
    │   ├── 001.jpg
    │   ├── 002.jpg
    │   └── 003.jpg
    ├── Chapter_2/
    │   ├── 001.jpg
    │   ├── 002.jpg
    │   └── 004.jpg
    └── Chapter_3/
        └── ...
```

#### Get Manga Information

**Endpoint**: `GET /api/v1/manga/info?url={manga_url}`

**Description**: Preview manga information before downloading

**Response**:

```json
{
    "manga_url": "https://nettruyenvia.com/truyen-tranh/...",
    "manga_title": "Học Cùng Em Gái, Không Cần Thận Trở Thành Vô Địch",
    "total_chapters": 20,
    "chapters": [
        {
            "chapter_number": "166",
            "chapter_title": "Chapter 166",
            "chapter_url": "https://..."
        }
    ]
}
```

### 📋 Manga List Batch Processing Endpoints

#### Crawl Manga List Page

**Endpoint**: `POST /api/v1/manga-list/crawl`

**Request Body**:

```json
{
    "url": "https://nettruyenvia.com/?page=637",
    "max_manga": 5,
    "max_chapters_per_manga": 3,
    "image_type": "cloud",
    "delay_between_manga": 3.0,
    "delay_between_chapters": 2.0,
    "custom_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}
```

**Parameters**:

- `url` (required): URL of the manga list page (e.g., https://nettruyenvia.com/?page=637)
- `max_manga` (optional): Maximum number of manga to process (None for all)
- `max_chapters_per_manga` (optional): Maximum chapters per manga (None for all)
- `image_type` (optional, default: "local"): Storage type - "local" for local files, "cloud" for Wasabi S3
- `delay_between_manga` (optional, default: 3.0): Delay between manga downloads (seconds)
- `delay_between_chapters` (optional, default: 2.0): Delay between chapter downloads (seconds)
- `custom_headers` (optional): Custom HTTP headers

**Response**:

```json
{
    "status": "success",
    "list_url": "https://nettruyenvia.com/?page=637",
    "total_manga_found": 20,
    "manga_processed": 5,
    "total_images_downloaded": 150,
    "manga_list": [
        {
            "manga_url": "https://nettruyenvia.com/truyen-tranh/manga-1",
            "manga_title": "Manga Title 1",
            "manga_folder": "downloads/Manga_Title_1",
            "total_chapters": 10,
            "chapters_downloaded": 3,
            "total_images_downloaded": 30,
            "status": "success",
            "processing_time_seconds": 45.2,
            "errors": []
        }
    ],
    "errors": [],
    "processing_time_seconds": 180.5
}
```

**Example Folder Structure**:

```
downloads/
├── Manga_Title_1/
│   ├── Chapter_1/
│   │   ├── 001.jpg
│   │   └── 002.jpg
│   └── Chapter_2/
│       ├── 001.jpg
│       └── 002.jpg
├── Manga_Title_2/
│   └── Chapter_1/
│       ├── 001.jpg
│       └── 002.jpg
└── ...
```

#### Manga List Health Check

**Endpoint**: `GET /api/v1/manga-list/health`

**Response**:

```json
{
    "status": "healthy",
    "service": "Manga List Crawler API",
    "version": "1.0.0",
    "endpoints": [
        "POST /api/v1/manga-list/crawl - Crawl manga list page"
    ]
}
```

#### Get Manga List Examples

**Endpoint**: `GET /api/v1/manga-list/examples`

**Response**:

```json
{
    "examples": {
        "basic_local": {
            "description": "Basic manga list crawl with local storage",
            "request": {
                "url": "https://nettruyenvia.com/?page=637",
                "max_manga": 3,
                "max_chapters_per_manga": 2,
                "image_type": "local",
                "delay_between_manga": 3.0,
                "delay_between_chapters": 2.0
            }
        },
        "cloud_storage": {
            "description": "Manga list crawl with cloud storage",
            "request": {
                "url": "https://nettruyenvia.com/?page=637",
                "max_manga": 5,
                "max_chapters_per_manga": 3,
                "image_type": "cloud",
                "delay_between_manga": 3.0,
                "delay_between_chapters": 2.0
            }
        }
    }
}
```

### 🏠 Root Endpoint

#### API Information

**Endpoint**: `GET /`

**Response**:

```json
{
    "message": "Welcome to Image Crawler API",
    "version": "1.0.0",
    "documentation": "/docs",
    "health_check": "/api/v1/health"
}
```

## 🔧 Advanced Features

### Handling Different Image Types

The crawler can handle various image sources:

1. **Standard Images**: Regular `<img>` tags with `src` attributes
2. **Lazy-Loaded Images**: Images with `data-src`, `data-original`, or `data-lazy` attributes
3. **CSS Background Images**: Images defined in `background-image` CSS properties
4. **Base64 Images**: Inline base64 encoded images in HTML
5. **JavaScript-Rendered Images**: Images loaded dynamically via JavaScript

### Selenium Integration

When `use_selenium: true` is set, the crawler:

- Loads the page in a headless Chrome browser
- Scrolls through the entire page to trigger lazy loading
- Waits for JavaScript to execute and render content
- Extracts images from the final rendered DOM

### Error Handling

The API provides comprehensive error reporting:

- Individual image download failures don't stop the entire process
- Partial success status when some images fail to download
- Detailed error messages for troubleshooting
- Graceful fallbacks for various failure scenarios

## 🛠️ Configuration

### Environment Variables

You can configure the application using environment variables:

```bash
export HOST=0.0.0.0          # Server host (default: 0.0.0.0)
export PORT=8000             # Server port (default: 8000)
export RELOAD=true           # Auto-reload on code changes (default: true)
```

### Wasabi S3 Cloud Storage Configuration

To enable cloud storage functionality, configure the following environment variables in your `.env` file:

```bash
# Wasabi S3 Configuration
ACCESS_KEY=your_wasabi_access_key
SECRET_KEY=your_wasabi_secret_key
ENDPOINT_URL=https://s3.ap-southeast-1.wasabisys.com
BUCKET_NAME=your_bucket_name
```

**Note**: The system will automatically fall back to local storage if Wasabi configuration is missing or invalid.

### Chrome/Selenium Configuration

The Selenium WebDriver is configured with optimal settings:

- Headless mode for server environments
- Custom user agent to avoid bot detection
- Optimized window size and timeouts
- Automatic ChromeDriver management

## 📁 File Organization

Downloaded images are organized as follows:

```
downloads/
├── nettruyenvia_com/        # Domain-based folder
│   ├── image1.jpg
│   ├── image2.png
│   └── base64_image_1.jpg
├── Manga_Title_1/           # Manga series folder
│   ├── Chapter_1/
│   │   ├── 001.jpg
│   │   └── 002.jpg
│   └── Chapter_2/
│       ├── 001.jpg
│       └── 002.jpg
└── ...
```

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver not found**:

   - The webdriver-manager package should auto-install ChromeDriver
   - Ensure Google Chrome or Chromium is installed on your system

2. **Permission denied errors**:

   - Check write permissions for the downloads directory
   - Run with appropriate user permissions

3. **Timeout errors**:

   - Some websites may be slow to load
   - The crawler includes reasonable timeouts and retry logic

4. **Anti-bot protection**:
   - Some websites block automated requests
   - The crawler uses realistic user agents and headers
   - Consider adding delays or custom headers if needed

### Debug Mode

For debugging, you can run the server with detailed logging:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 📝 Example Usage

### With cURL

```bash
# Crawl images from a website (local storage)
curl -X POST "http://localhost:8000/api/v1/crawl" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://nettruyenvia.com/",
       "max_images": 50,
       "include_base64": true,
       "use_selenium": true,
       "image_type": "local"
     }'

# Crawl images from a website (cloud storage)
curl -X POST "http://localhost:8000/api/v1/crawl" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://nettruyenvia.com/",
       "max_images": 50,
       "include_base64": true,
       "use_selenium": true,
       "image_type": "cloud"
     }'

# Health check
curl -X GET "http://localhost:8000/api/v1/health"

# Crawl manga series
curl -X POST "http://localhost:8000/api/v1/manga/crawl" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://nettruyenvia.com/truyen-tranh/...",
       "max_chapters": 5,
       "image_type": "local"
     }'

# Get manga information
curl -X GET "http://localhost:8000/api/v1/manga/info?url=https://nettruyenvia.com/truyen-tranh/..."

# Crawl manga list page (batch processing)
curl -X POST "http://localhost:8000/api/v1/manga-list/crawl" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://nettruyenvia.com/?page=637",
       "max_manga": 3,
       "max_chapters_per_manga": 2,
       "image_type": "local",
       "delay_between_manga": 3.0,
       "delay_between_chapters": 2.0
     }'
```

### With Python

```python
import requests
import json

# Crawl images (local storage)
response = requests.post('http://localhost:8000/api/v1/crawl',
    json={
        'url': 'https://nettruyenvia.com/',
        'max_images': 50,
        'include_base64': True,
        'use_selenium': True,
        'image_type': 'local'
    }
)

result = response.json()
print(f"Downloaded {result['images_downloaded']} images to {result['folder_path']}")

# Crawl images (cloud storage)
response = requests.post('http://localhost:8000/api/v1/crawl',
    json={
        'url': 'https://nettruyenvia.com/',
        'max_images': 50,
        'include_base64': True,
        'use_selenium': True,
        'image_type': 'cloud'
    }
)

result = response.json()
print(f"Downloaded {result['images_downloaded']} images")
for image in result['images']:
    if image.get('cloud_url'):
        print(f"Cloud URL: {image['cloud_url']}")

# Get manga information
response = requests.get('http://localhost:8000/api/v1/manga/info',
    params={'url': 'https://nettruyenvia.com/truyen-tranh/...'}
)
manga_info = response.json()
print(f"Manga: {manga_info['manga_title']} - {manga_info['total_chapters']} chapters")

# Crawl manga series
response = requests.post('http://localhost:8000/api/v1/manga/crawl',
    json={
        'url': 'https://nettruyenvia.com/truyen-tranh/...',
        'max_chapters': 5,
        'image_type': 'local'
    }
)

result = response.json()
print(f"Downloaded {result['total_images_downloaded']} images from {result['chapters_downloaded']} chapters")

# Crawl manga list page (batch processing)
response = requests.post('http://localhost:8000/api/v1/manga-list/crawl',
    json={
        'url': 'https://nettruyenvia.com/?page=637',
        'max_manga': 3,
        'max_chapters_per_manga': 2,
        'image_type': 'local',
        'delay_between_manga': 3.0,
        'delay_between_chapters': 2.0
    }
)

result = response.json()
print(f"Processed {result['manga_processed']} manga")
print(f"Total images: {result['total_images_downloaded']}")
for manga in result['manga_list']:
    print(f"- {manga['manga_title']}: {manga['total_images_downloaded']} images")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate use cases only. Always respect website terms of service and robots.txt files. Be mindful of copyright and intellectual property rights when downloading images.

## 🙋‍♂️ Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Create an issue in the project repository
4. Check the system architecture documentation in `system.md`
