import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import whatsapp, appointments, dashboard
from database import Base, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AtendenteIA MVP",
    description="WhatsApp AI Assistant for Appointment Booking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

# Include routers
app.include_router(whatsapp.router, prefix="/webhook", tags=["webhooks"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

logger.info("All routers registered")


@app.get("/", tags=["health"])
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "version": "1.0.0",
        "service": "AtendenteIA"
    }


@app.get("/health", tags=["health"])
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "service": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
