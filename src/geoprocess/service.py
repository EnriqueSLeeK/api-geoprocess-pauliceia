
from typing import List
from geoprocess.logic.processor import GeoProcessor
from dto.input_data import InputData
from dto.return_data import ReturnData

def process_place_data(data: List[InputData]) -> ReturnData:
    geprocessor = GeoProcessor(data)
    result_log = geprocessor.process_data()
    return result_log

