from typing import List
from pydantic import BaseModel

class LogEntry(BaseModel):
    linha: int
    descricao: str

class ReturnData(BaseModel):
    log_erro: List[LogEntry]
    log_sucesso: List[LogEntry]
