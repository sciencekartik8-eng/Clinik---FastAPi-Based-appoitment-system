from fastapi import FastAPI
# from fastapi import Depends
# from app.db.database import  Base, engine
from app.db import base
# from app.dependencies import auth

from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.availability import router as availability_router
from app.routers.doctors import router as doctors_router
from app.routers.clinics import router as clinics_router
from app.routers.appointments import router as appointments_router
from app.routers.patients import router as patient_router

# Base.metadata.create_all(bind=engine) # what this is doing is creating the tables in the database based on the models defined in the 
# app/models directory. The Base.metadata.create_all() method is called with the engine as an argument, 
# which tells SQLAlchemy to create all the tables defined in the models that inherit from Base.

app = FastAPI(
    title="Clinic Management System",
    description="A simple clinic management system API built with FastAPI and SQLAlchemy.",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(availability_router)
app.include_router(doctors_router)
app.include_router(clinics_router)
app.include_router(appointments_router)
app.include_router(patient_router)



@app.get("/")
def read_root():
    return {"message": "Welcome to the Clinic Management System API!"}