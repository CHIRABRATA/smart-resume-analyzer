# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic_settings import BaseSettings, SettingsConfigDict
# app = FastAPI(
    
#     description="ATS Resume Analyzer API"
# )

# # CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/")
# async def root():
#     return {
#         "message": "ATS Resume Analyzer API",
#         "docs": "/docs"
#     }

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}