# Crawl Image Tool - Project Structure

## Overview
This is a Python-based image crawling tool with a modular architecture designed for manga and image management.

## Directory Structure

```
crawl-image-tool/
├── .git/                          # Git repository
├── .env                           # Environment variables (0.0B)
├── .env.example                   # Environment variables template (330B)
├── .gitignore                     # Git ignore file (46B)
├── README.md                      # Project documentation (16KB, 568 lines)
├── requirements.txt               # Python dependencies (687B, 35 lines)
├── main.py                        # Main application entry point (4.7KB, 167 lines)
├── system.md                      # This file - system documentation
├── controllers/                   # Controller layer
│   ├── __init__.py               # Package initialization (0.0B)
│   ├── image_controller.py       # Image controller logic (3.9KB, 127 lines)
│   ├── manga_controller.py       # Manga controller logic (6.4KB, 180 lines)
│   └── manga_list_controller.py  # Manga list controller (2.0KB, 56 lines)
├── services/                      # Business logic layer
│   ├── __init__.py               # Package initialization (0.0B)
│   ├── image_crawler.py          # Image crawling service (29KB, 678 lines)
│   ├── manga_crawler.py          # Manga crawling service (38KB, 965 lines)
│   ├── manga_list_crawler.py     # Manga list crawling service (15KB, 375 lines)
│   ├── wasabi_service.py         # Wasabi storage service (6.9KB, 220 lines)
│   └── existence_checker.py      # Smart duplicate detection service (NEW)
├── routes/                        # API routing layer
│   ├── __init__.py               # Package initialization (0.0B)
│   ├── image_routes.py           # Image API endpoints (4.6KB, 166 lines)
│   ├── manga_routes.py           # Manga API endpoints (5.9KB, 190 lines)
│   └── manga_list_routes.py      # Manga list API endpoints (3.8KB, 123 lines)
├── models/                        # Data models and schemas
│   ├── __init__.py               # Package initialization (0.0B)
│   └── schemas.py                # Data schemas and models (7.7KB, 130 lines)
└── downloads/                     # Download storage directory
    └── (empty)
```

## Architecture Overview

### Layers
1. **Routes Layer** (`routes/`) - API endpoint definitions and HTTP request handling
2. **Controllers Layer** (`controllers/`) - Request processing and business logic coordination
3. **Services Layer** (`services/`) - Core business logic and external service integration
4. **Models Layer** (`models/`) - Data structures and validation schemas

### Key Components
- **Image Management**: Handles individual image crawling and processing
- **Manga Management**: Manages manga series and chapters
- **Manga List Management**: Handles manga listing and categorization
- **Wasabi Integration**: Cloud storage service for downloaded content
- **Download Management**: Local storage for crawled content
- **Smart Duplicate Detection**: NEW - Prevents re-downloading existing content

### File Sizes
- Largest files are in the services layer, indicating complex business logic
- Controllers are lightweight, focusing on request coordination
- Routes provide API interface definitions
- Models contain data validation schemas

## Technology Stack
- **Language**: Python
- **Architecture**: Layered architecture with separation of concerns
- **Storage**: Local downloads + Wasabi cloud storage
- **API**: RESTful API design
- **Dependencies**: Managed via requirements.txt

## Notes
- The project follows a clean architecture pattern
- Services contain the most complex logic (largest files)
- Controllers act as thin coordination layers
- Routes provide clean API interfaces
- Models ensure data consistency and validation

## Recent Updates (Smart Duplicate Detection)

### New Service: ExistenceChecker
- **Purpose**: Prevents re-downloading existing manga chapters and images
- **Features**:
  - Chapter-level existence checking
  - Image-level existence checking
  - Support for both local and cloud storage
  - Metadata tracking for progress monitoring
- **Benefits**:
  - Faster re-runs by skipping existing content
  - Resume capability for interrupted downloads
  - Storage efficiency (no duplicate files)
  - Progress tracking across multiple sessions

### Integration Points
- **MangaCrawlerService**: Now checks existence before downloading
- **MangaController**: New endpoint for progress checking
- **MangaRoutes**: New `/progress/{manga_title}` endpoint
- **Metadata Files**: `manga_metadata.json` tracks download progress
