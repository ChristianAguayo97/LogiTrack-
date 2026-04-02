from contextlib import asynccontextmanager

from sqlmodel import SQLModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.db import engine
from src.routers.envio_router import envio_router
from src.routers.auditoria_router import auditoria_router
from src.routers.cliente_router import envio_cliente_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(
        title="LogiTrack API",
        description= "API para gestión de envíos con trazabilidad y roles",
        version="0.0.1",
        lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(envio_router)
app.include_router(auditoria_router)
app.include_router(envio_cliente_router)

@app.get("/")
def home():
    return {"mensaje": "Bienvenido a LogiTrack API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}