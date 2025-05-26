
from fastapi import APIRouter
from geoprocess.service import process_place_data
from typing import List
from dto.input_data import InputData
from dto.return_data import ReturnData

router = APIRouter()

@router.post("/process", response_model= List[ReturnData])
async def process_place_route(lugar_rua: List[InputData]):
    return process_place_data(lugar_rua)
