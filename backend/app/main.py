from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import upload, analyze, feedback

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ATS Resume Analyzer API"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}", tags=["upload"])
app.include_router(analyze.router, prefix=f"{settings.API_V1_STR}", tags=["analyze"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}", tags=["feedback"])

@app.get("/")
async def root():
    return {
        "message": "ATS Resume Analyzer API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)