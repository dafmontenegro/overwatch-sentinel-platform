# Standard Library Imports
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# Third-party Imports
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import asyncio
from sqlalchemy.exc import OperationalError

# Relative Imports 
from .database import SessionLocal, create_tables, get_db, engine
from .models import User
from .auth import create_access_token, get_current_user
from .config import SECRET_KEY, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, FRONTEND_URL

"""
    Author: Cristian Beltran
    Email: crbeltranr@unal.edu.co
    Modify_by: Cristian Beltran & MiguelAngel Mosquera
    Date_Creation: 2025-05-17
    Date_Modification: 2025-05-18
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
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize FastAPI application instance
app = FastAPI(title="Video Surveillance System", description="Combined video streaming and authentication system")

# Add SessionMiddleware (required for OAuth to work)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.add_middleware(
    SessionMiddleware,
    # secret_key=os.getenv("SECRET_KEY", "default_super_secret_key")
    secret_key=SECRET_KEY,
)

### Raspberry Pi connection endpoints ###
# Environment variables for device endpoints
VIDEO_STREAM_URL = os.getenv("VIDEO_STREAM_URL")  # URL for live video streaming
LOGS_URL = os.getenv("LOGS_URL")                  # URL to fetch raw logs from device
EVENTS_URL = os.getenv("EVENTS_URL")              # URL for event notifications
PLAY_URL = os.getenv("PLAY_URL")                  # Base URL for video playback

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
        async with client.stream("GET", VIDEO_STREAM_URL) as response:
            # Stream bytes in real-time as they arrive
            async for chunk in response.aiter_bytes():
                yield chunk

# Execute during application startup
@app.on_event("startup")
async def startup():
    logger.info("Starting database initialization...")
    
    # Verifica si las tablas ya existen
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT users FROM information_schema.tables WHERE table_schema='public'"))
            tables = result.scalars().all()
            logger.info(f"Existing tables: {tables}")
    except Exception as e:
        logger.error(f"Error checking existing tables: {str(e)}")

    max_retries = 5
    for attempt in range(max_retries):
        try:
            await create_tables()
            logger.info("Database tables created successfully")
            break
        except OperationalError as e:
            logger.warning(f"Database connection failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Espera exponencial
            else:
                logger.error("Failed to connect to database after multiple attempts")
                raise

# OAuth configuration
config = Config('.env')
oauth = OAuth(config)

# Register Google provider
google = oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile"},
)

# Google authentication endpoint
@app.get("/auth/google")
async def login_google(request: Request):
    """Initiates Google OAuth2 flow"""
    redirect_uri = request.url_for("auth_google_callback")  # Callback endpoint name
    return await google.authorize_redirect(request, redirect_uri)

# Database dependency
def get_db():
    """Provides an async database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Google OAuth callback handler
@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles Google OAuth2 callback and user management"""
    try:
        # Exchange authorization code for tokens
        token = await google.authorize_access_token(request)
        user_info = await google.parse_id_token(request, token)

        if not user_info:
            logging.error("Google did not return userinfo")
            raise HTTPException(status_code=400, detail="Failed to retrieve userinfo")

        # Database query for existing user
        result = await db.execute(
            select(User).where(
                (User.provider_id == user_info["sub"]) | (User.email == user_info["email"])
            )
        )
        user = result.scalar_one_or_none()

        name = user_info.get("name", "")
        picture = user_info.get("picture", "")

        # Create new user if not exists
        if not user:
            user = User(
                provider="google",
                provider_id=user_info["sub"],
                email=user_info["email"],
                name=name,
                picture=picture
            )
            db.add(user)
        else:
            if name:
                user.name = name
            if picture:
                user.picture = picture

        await db.commit()
        await db.refresh(user)

        # Generate JWT for API access
        access_token = create_access_token(data={"sub": str(user.id)})
        #return {"access_token": access_token, "token_type": "bearer"}
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?access_token={access_token}"
        )

    except Exception as e:
        logging.error(f"Critical error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    
    finally:
        await db.close()

# Register GitHub provider
github = oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

# GitHub authentication endpoint
@app.get("/auth/github")
async def login_github(request: Request):
    """Initiates GitHub OAuth2 flow"""
    redirect_uri = request.url_for("auth_github_callback")
    return await github.authorize_redirect(request, redirect_uri)

# gitHub OAuth callback handler
@app.get("/auth/github/callback")
async def auth_github_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles Google OAuth2 callback and user management"""
    try:
        # Exchange authorization code for tokens
        token = await github.authorize_access_token(request)
        resp = await github.get("user", token=token)
        profile = resp.json()

        # Github puede no dar email por defecto
        email = profile.get("email")
        if not email:
            emails_resp = await github.get("user/emails", token=token)
            emails = emails_resp.json()
            email = next((e["email"] for e in emails if e["primary"] and e["verified"]), None)

        if not email:
            raise HTTPException(status_code=400, detail="No email found from GitHub")
        
        provider_id = str(profile["id"])
        name = profile.get("name", profile.get("login"))
        picture = profile.get("avatar_url", "")

        #Buscar o crear usuario
        # Buscar usuario por provider_id o por email existente
        result = await db.execute(
            select(User).where(
                (User.provider_id == str(profile["id"])) | (User.email == email)
            )
        )
        user = result.scalar_one_or_none()

        # Create new user if not exists
        if not user:
            user = User(
                provider="github",
                provider_id=provider_id,
                email=email,
                name=name,
                picture=picture
            )
            db.add(user)
        else:
            if name:  # Solo actualiza si name tiene valor
                user.name = name
            if picture:  # Solo actualiza si picture tiene valor
                user.picture = picture

        await db.commit()
        await db.refresh(user)

        # Generate JWT for API access
        access_token = create_access_token(data={"sub": str(user.id)})
        #return {"access_token": access_token, "token_type": "bearer"}
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?access_token={access_token}"
        )

    except Exception as e:
        logging.error(f"GitHub login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Protected endpoint example
@app.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    """Example protected route requiring valid JWT"""
    return {"message": "Authorized access", "user_id": current_user}

# Root endpoint
@app.get("/")
async def home():
    """Application entry point"""
    return {"message": "Welcome to the backend called logic system"}

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

@app.get("/logs/")
def get_logs():
    """
    Retrieve stored logs from MongoDB collection.
    Returns logs without MongoDB's internal _id field for cleaner output.
    """
    # Fetch all documents from collection, excluding MongoDB's internal ID
    logs = list(db[collection_name].find({}, {"_id": 0}))
    return {"logs": logs}

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

@app.get("/events/stream/{video_path:path}")
async def proxy_event_stream(video_path: str):
    """
    Stream recorded event videos from Raspberry Pi.
    :param video_path: Path segment for requested video file
    """
    # Construct full URL for video playback
    url = f"{PLAY_URL}{video_path}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, stream=True)
        # Handle missing videos
        if resp.status_code != 200:
            return JSONResponse(
                content={"error": "Video not found"},
                status_code=404
            )
        # Stream video content directly to client
        return StreamingResponse(resp.aiter_bytes(), media_type="video/mp4")

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
        response = httpx.get(LOGS_URL)
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