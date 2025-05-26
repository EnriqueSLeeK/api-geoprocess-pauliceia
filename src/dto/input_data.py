

from pydantic import BaseModel, Field, StrictStr, field_validator

def date_validator():
    return True

class InputData(BaseModel):
    rua: str = Field(..., min_length=1, max_length=1000)
    autor: str = Field(...)
    fonte: str = Field(...)

    id_rua: int = Field(...)
    saboya_numero: int = Field(...)
    id_ponto: int = Field(...)
    metragem: float = Field(...)
    numero_lugar: int = Field(...)

    data: str = Field(...)
    data_inicio: str = Field(...)
    data_final: str = Field(...)

    @field_validator("data", "data_inicio", "data_final", mode="before")
    @classmethod
    def check_date_format(cls, v):
        import datetime
        try:
            datetime.datetime.strptime(v, "%d/%m/%Y")
        except ValueError:
            raise ValueError("O formato da data pode estar errado (dd/mm/YYYY) ou os valores do dia(1 ~ 31) ou mês (1 ~ 12) fogem dos intervalos aceitos")
        return v.lstrip("0")

    @field_validator("data_final", mode="plain")
    @classmethod
    def check_dates_order(cls, v, values):
        import datetime

        if v is None or v == "":
            return v
        
        data = values.data
        final = datetime.datetime.strptime(v, "%d/%m/%Y")
        inicio = datetime.datetime.strptime(data["data_inicio"], "%d/%m/%Y")
        if (inicio > final):
            raise ValueError("Data final é maior que a data inicial.")
        return v

if __name__ == "__main__":
    data = {
        "rua": "we",
        "autor": "asdas",
        "fonte": "sabo sabo",
        "id_rua": 23,
        "saboya_numero": 3,
        "id_ponto": 3,
        "metragem": 3,
        "numero_lugar": 3,
        "data": "23/03/2303",
        "data_inicio": "11/11/1111",
        "data_final": "12/11/1111"
    } 
    InputData(**data)
