from fastapi import FastAPI
from controllers import whatsapp, appointments, dashboard
from database import Base, engine

app = FastAPI(title="AtendenteIA MVP")

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(whatsapp.router, prefix="/webhook")
app.include_router(appointments.router, prefix="/appointments")
app.include_router(dashboard.router, prefix="/dashboard")


@app.get("/")
def root():
    return {"status": "AtendenteIA is running 🚀"}
