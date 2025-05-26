
from fastapi import APIRouter
from geoprocess.service import process_place_data
from typing import List
from dto.input_data import InputData
from dto.return_data import ReturnData

router = APIRouter()

@router.get("/")
async def hi():
    return "Hi boo"

@router.post("/process", response_model= ReturnData)
async def process_place_route(lugar_rua: List[InputData]):
    result = process_place_data(lugar_rua)
    return {
        "log_erro": [{"linha": 0, "descricao": "string"}],
        "log_sucesso": [{"linha": 0, "descricao": "string"}],
    }
