import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_data import seed_database

# Import API Routers
from app.api.auth import router as auth_router
from app.api.zones import router as zones_router
from app.api.sensors import router as sensors_router
from app.api.ppe import router as ppe_router
from app.api.risk import router as risk_router
from app.api.compliance import router as compliance_router
from app.api.actions import router as actions_router
from app.api.digital_twin import router as digital_twin_router
from app.api.workers import router as workers_router
from app.api.equipment import router as equipment_router
from app.api.reports import router as reports_router
from app.api.audit import router as audit_router
from app.api.dashboard import router as dashboard_router
from app.api.contractors import router as contractors_router
from app.api.inspections import router as inspections_router

# Create Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Driven Digital Twin & Predictive Compliance Management System for Coal Mine Safety Governance",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Uploads Directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(digital_twin_router, prefix=settings.API_V1_STR)
app.include_router(zones_router, prefix=settings.API_V1_STR)
app.include_router(ppe_router, prefix=settings.API_V1_STR)
app.include_router(sensors_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(compliance_router, prefix=settings.API_V1_STR)
app.include_router(actions_router, prefix=settings.API_V1_STR)
app.include_router(workers_router, prefix=settings.API_V1_STR)
app.include_router(equipment_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(contractors_router, prefix=settings.API_V1_STR)
app.include_router(inspections_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "Operational",
        "regulatory_standard": "Directorate General of Mines Safety (DGMS)",
        "api_documentation": "/docs"
    }

@app.get("/health")
def healthcheck():
    return {"status": "healthy", "database": "connected"}

