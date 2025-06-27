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
import asyncio
from sqlalchemy.exc import OperationalError

# Relative Imports 
from .database import SessionLocal, create_tables, get_db, engine
from .models import User
from .auth import create_access_token, get_current_user
from .config import SECRET_KEY, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, FRONTEND_URL, GOOGLE_REDIRECT_URI, GITHUB_REDIRECT_URI

"""
    Author: MiguelAngel Mosquera
    Email: crbeltranr@unal.edu.co
    Modify_by: Cristian Beltran & MiguelAngel Mosquera
    Date_Creation: 2025-05-17
    Date_Modification: 2025-06-16
    Purpose:
    //Por llenar// Miguel Angel
    
    Requirements:
    - APScheduler: For scheduling background tasks
    - fastapi: Web framework for building API endpoints
    - httpx: Asynchronous HTTP client for making requests
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
app = FastAPI(title="Authentication System", description="Authentication system")

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
    #redirect_uri = request.url_for("auth_google_callback")  # Callback endpoint name
    redirect_uri = GOOGLE_REDIRECT_URI  # Use the configured redirect URI
    if not redirect_uri:
        raise HTTPException(status_code=500, detail="Google redirect URI not configured")
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
    #redirect_uri = request.url_for("auth_github_callback")
    redirect_uri = GITHUB_REDIRECT_URI  # Use the configured redirect URI
    if not redirect_uri:
        raise HTTPException(status_code=500, detail="GitHub redirect URI not configured")
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
    return {"message": "Welcome to the backend authentication system"}