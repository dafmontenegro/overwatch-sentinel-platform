from fastapi import FastAPI, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware  # Importa SessionMiddleware
from starlette.requests import Request
from starlette.config import Config
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Importaciones relativas desde el paquete "app"
from .database import SessionLocal, create_tables, get_db  # Importación relativa correcta
from .models import User
from .auth import create_access_token, get_current_user

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

# Añade SessionMiddleware (requerido para OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key="tu_super_secreto",  # Debe coincidir con SECRET_KEY
)

# Ejecutar al iniciar la app
@app.on_event("startup")
async def startup():
    await create_tables()  # Usa await aquí

# Configura OAuth
config = Config('.env')
oauth = OAuth(config)

# Registra proveedor Google
google = oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
#
#
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile"},
)

# Define la ruta /auth/google
@app.get("/auth/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")  # Nombre de la función del callback
    return await google.authorize_redirect(request, redirect_uri)

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await google.authorize_access_token(request)
        user_info = await google.parse_id_token(request, token)

        if not user_info:
            logging.error("Google no devolvió userinfo")
            raise HTTPException(status_code=400, detail="No se pudo obtener userinfo")

        # Busca o crea el usuario en la base de datos
        result = await db.execute(select(User).where(User.provider_id == user_info["sub"]))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                provider="google",
                provider_id=user_info["sub"],
                email=user_info["email"]
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Genera el token JWT
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logging.error(f"Error crítico: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    finally:
        await db.close()

@app.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": "Acceso autorizado", "user_id": current_user}

@app.get("/")
async def home():
    return {"message": "Bienvenido al sistema de autenticación"}