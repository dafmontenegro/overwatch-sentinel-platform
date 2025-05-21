from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://auth_user:abc123@db:5432/auth_db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def create_tables():
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