import os
from dotenv import load_dotenv

load_dotenv() #Carga el archivo . env

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
DATABASE_URL = os.getenv("DATABASE_URL")

# GitHub OAuth2
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL")

# OAuth2
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
