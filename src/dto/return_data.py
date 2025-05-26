from typing import List
from pydantic import BaseModel

def log_entry_factory(index, descricao):
    return {
        "linha": index,
        "descricao": descricao
    }

class LogEntry(BaseModel):
    linha: int
    descricao: str

class ReturnData(BaseModel):
    log_erro: List[LogEntry]
    log_sucesso: List[LogEntry]
