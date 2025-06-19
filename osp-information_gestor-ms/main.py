# Standard Library Imports
import os
import logging
from datetime import datetime

# Third-party Imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

"""
    Author: Cristian Beltran
    Email: crbeltranr@unal.edu.co
    Modify_by: Cristian Beltran
    Date_Creation: 2025-05-17
    Date_Modification: 2025-06-07
    Purpose:
    This API acts as a middleware layer between client applications and Raspberry Pi devices,
    handling video streaming, log management, and event processing. It also integrates with
    MongoDB for persistent log storage and provides scheduled tasks for automatic log updates.
    
    Requirements:
    - APScheduler: For scheduling background tasks
    - fastapi: Web framework for building API endpoints
    - httpx: Asynchronous HTTP client for making requests
    - pymongo: MongoDB client for database operations
    - uvicorn: ASGI server for running the application
    Version: 1.0
"""

# Configure logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize FastAPI application instance
app = FastAPI(title="Video Surveillance System", description="System of video streaming and information management for Raspberry Pi devices", version="1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

### Raspberry Pi connection endpoints ###

# Obtener URLs desde variables de entorno
information_port = os.getenv('INFORMATION_PORT', 'http://apigateway-ms:8887/')
LOGS_URL = os.getenv('LOGS_URL', f'{information_port}/logs')
EVENTS_URL = os.getenv('EVENTS_URL', f'{information_port}/events')
VIDEOS_URL = os.getenv('VIDEOS_URL', f'{information_port}/videos')

### MongoDB Connection Setup ###
# Configure MongoDB client using cluster URI from environment variables
mongodb_uri = os.getenv("MONGODB_CLUSTER")
client = MongoClient(mongodb_uri, server_api=ServerApi('1'))

# Get database and collection names from environment variables
db_name = os.getenv("MONGODB_DB")
db = client[db_name]
collection_name = os.getenv("MONGODB_COLLECTION")

async def proxy_video_stream():
    """
    Asynchronous generator function to proxy video stream from Raspberry Pi.
    Uses streaming response to handle MJPEG format efficiently.
    """
    async with httpx.AsyncClient() as client:
        # Maintain persistent connection to video stream source
        async with client.stream("GET", VIDEOS_URL) as response:
            # Stream bytes in real-time as they arrive
            async for chunk in response.aiter_bytes():
                yield chunk

# Root endpoint
@app.get("/")
async def home():
    """Application entry point"""
    return {"message": "Welcome to the backend called logic system"}

@app.get("/video")
@app.get("/video/")
async def video():
    """
    Endpoint to provide live video streaming.
    Returns streaming response with proper MJPEG media type.
    """
    return StreamingResponse(
        proxy_video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/logs")
@app.get("/logs/")
async def get_logs(source: str = "mongo"):
    """
    Get logs from either MongoDB or directly from Raspberry Pi
    
    Parameters:
    - source: 'mongo' (default) or 'direct'
    """
    if source == "direct":
        async with httpx.AsyncClient() as client:
            response = await client.get(LOGS_URL)
            return Response(content=response.text, media_type="text/plain")
    else:
        logs = list(db[collection_name].find({}, {"_id": 0}))
        return {"logs": logs}

@app.get("/events")
@app.get("/events/")
async def proxy_events():
    """
    Proxy endpoint for event notifications from Raspberry Pi.
    Preserves original response status and content.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(EVENTS_URL)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )

# Variable to track last processed log entry
last_log = ""  

def fetch_logs():
    """
    Scheduled task to fetch and store logs from Raspberry Pi.
    Processes logs from last 24 hours and stores new entries in MongoDB.
    """
    print("Executing fetch_logs...")
    try:
        # Fetch raw logs from Raspberry Pi endpoint
        response = httpx.get(information_port)
        response.raise_for_status()
        logs = response.text.splitlines()
        now = datetime.now()
        new_logs = 0
        
        # Process each log line
        for log_line in logs:
            try:
                # Extract datetime from log entry
                date_str = log_line.split(" ", 2)[:2]
                log_datetime = datetime.strptime(" ".join(date_str), "%Y-%m-%d %H:%M:%S")
                
                # Check if log is within 24 hours window
                if (now - log_datetime).total_seconds() <= 86400:
                    # Prevent duplicate entries
                    if not db[collection_name].find_one({"log": log_line}):
                        db[collection_name].insert_one({
                            "log": log_line,
                            "timestamp": log_datetime
                        })
                        new_logs += 1
            except Exception as ex:
                print(f"Log ignored due to format issues: {log_line} | Error: {ex}")
                continue
        print(f"fetch_logs completed. New logs inserted: {new_logs}")
    except Exception as e:
        print(f"Error fetching logs: {e}")
        logging.error(f"Error fetching logs: {e}")

# Configure background scheduler for automatic log updates
scheduler = BackgroundScheduler()
# Schedule daily log sync at midnight (00:00) Monday-Friday
scheduler.add_job(
    fetch_logs,
    trigger='cron',
    day_of_week='mon-fri',
    hour=0,
    minute=0
)
scheduler.start()