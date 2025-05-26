
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from geoprocess.controller import router as geoprocess_router


app = FastAPI()
app.include_router(geoprocess_router, prefix="/geoprocess", tags=["Geoprocess"])
