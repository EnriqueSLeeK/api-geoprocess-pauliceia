from fastapi import FastAPI
from geoprocess.controller import router as geoprocess_router

app = FastAPI()
app.include_router(geoprocess_router, prefix="/geoprocess", tags=["Geoprocess"])
