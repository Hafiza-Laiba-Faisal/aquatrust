from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api import observations, evidence, assessments, reviews, demo

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Evidence-aware AI validation layer for citizen freshwater observations",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(observations.router, prefix=settings.API_V1_PREFIX)
app.include_router(evidence.router, prefix=settings.API_V1_PREFIX)
app.include_router(assessments.router, prefix=settings.API_V1_PREFIX)
app.include_router(reviews.router, prefix=settings.API_V1_PREFIX)
app.include_router(demo.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "0.1.0",
        "description": "Evidence-aware AI validation layer for citizen freshwater observations",
    }
