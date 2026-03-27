from contextlib import asynccontextmanager

from sqlmodel import SQLModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.db import engine
from src.models import envio
from src.routers.envio_router import envio_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(
        title="LogiTrack API",
        description= "API para gestion de envíos",
        version="0.0.1",
        lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(envio_router)

@app.get("/")
def home():
    return {"mensaje": "Bienvenido a LogiTrack API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}