from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import datasets

# Create Tables (for MVP simple init)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Data Storytelling API",
    description="Backend API for AI Data Storytelling SaaS",
    version="0.1.0"
)

app.include_router(datasets.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "api"}

@app.get("/")
async def root():
    return {"message": "Welcome to AI Data Storytelling API"}
