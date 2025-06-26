from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def create_tables():
    from .models import User
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:  # Usa async with
        try:
            yield session
            await session.commit()  # Commit si todo va bien
        except Exception:
            await session.rollback()  # Rollback en caso de error
            raise
        finally:
            await session.close()  # Cierra la sesión con await