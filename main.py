"""
Main FastAPI application for Image Crawler service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.image_routes import router as image_router
from routes.manga_routes import router as manga_router


# Create downloads directory if it doesn't exist
downloads_dir = Path("downloads")
downloads_dir.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Image Crawler API is starting up...")
    print(f"📁 Downloads directory: {downloads_dir.absolute()}")

    yield

    # Shutdown
    print("🛑 Image Crawler API is shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Image Crawler API",
    description="""
    ## Advanced Image Crawler Service

    A powerful FastAPI service for crawling and downloading images from websites.

    ### Features:
    - 🖼️ **Standard Image Crawling**: Extract images from HTML img tags
    - 🔄 **Lazy Loading Support**: Handle lazy-loaded images using Selenium
    - 📱 **JavaScript Rendering**: Process dynamically loaded content
    - 🎨 **Base64 Images**: Extract and save base64 encoded images
    - 📂 **Organized Storage**: Save images in domain-named folders
    - ⚡ **Concurrent Downloads**: Fast parallel image downloading
    - 🛡️ **Error Handling**: Robust error handling and reporting

    ### Supported Image Sources:
    - Regular `<img>` tags with `src` attributes
    - Lazy-loaded images with `data-src`, `data-original` attributes
    - CSS background images
    - Base64 encoded images in HTML
    - JavaScript-rendered images

    ### Usage:
    1. Send a POST request to `/api/v1/crawl` with a website URL
    2. The system will crawl and download all images
    3. Images are saved to a folder named after the domain
    4. Get detailed results including download statistics
    """,
    version="1.0.0",
    contact={
        "name": "Image Crawler API",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(image_router)
app.include_router(manga_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "🖼️ Image Crawler API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
        "endpoints": {
            "crawl_images": "POST /api/v1/crawl",
            "check_status": "GET /api/v1/status/{url}",
            "health_check": "GET /api/v1/health",
            "crawl_manga": "POST /api/v1/manga/crawl",
            "manga_info": "GET /api/v1/manga/info",
            "manga_health": "GET /api/v1/manga/health",
            "manga_examples": "GET /api/v1/manga/examples"
        }
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "detail": f"The requested endpoint {request.url.path} was not found",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred on the server",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"🌐 Starting server on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"📖 ReDoc Documentation: http://{host}:{port}/redoc")

    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
