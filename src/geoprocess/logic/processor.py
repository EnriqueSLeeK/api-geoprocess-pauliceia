
from typing import List
from sqlalchemy import text
from infra.database import engine
from dto.input_data import InputData
from dto.return_data import ReturnData

class GeoProcessor:
    def __init__(self, data: List[InputData]):
        self.geo_data_list: List[InputData] = data
        self.log: ReturnData = {
            "log_sucesso": [],
            "log_erro": []
        }

    def __prepare_date(self, date_string: str) -> [int, int, int]:
        splitted_date = [
            int(date_component) for date_component in date_string.split("/")
        ]

        return splitted_date

    # Nao se confunda: Na funcao do saboya_geometry definida no banco pede
    # o numberPlace, mas na verdade ele quer a metragem do imovel na rua
    def __calculate_geographical_coord(self, stree_id: int, metragem: float):
        geographical_coordinates = None
        with engine.connect() as conn:
            geographical_coordinates = conn.execute(
                text("SELECT saboya_geometry(:street_id, :metragem) AS saboya_geometry"),
                {"street_id": stree_id, "metragem": metragem},
            )
        result = geographical_coordinates.fetchone()
        return result


    def __convert_geographical_coord_to_SRID(self, coord):
        geo_coord_srid = None
        with engine.connect() as conn:
            geo_coord_srid = conn.execute(
                text("SELECT ST_SetSRID(ST_Point(:x, :y),4326)"),
                {"x": coord[0], "y": coord[1]},
            )
        result = geo_coord_srid.fetchone()
        return result

    def __insert_data(batch):
        return

    def __check_date_ok(self, index, which, date):
        try:
            day, month, year = date
            return [day, month, year]
        except ValueError:
            self.log["log_error"].append({"linha": index,
                 "descricao": f"Erro: Data {"data_" + which} incompleta, por favor verificar a sua data."})

    def process_data(self) -> ReturnData:

        for index, geo_data in enumerate(self.geo_data_list):
            try:
                first_day,\
                first_month,\
                first_year = self.__check_date_ok(index, "inicio",
                              self.__prepare_date(geo_data["data_inicio"]))
                last_day,\
                last_month,\
                last_year = self.__check_date_ok(index, "final",
                               self.__prepare_date(geo_data["data_final"]))
            except Exception:
                continue

            date = geo_data["data"]
            author = geo_data["autor"]
            source = geo_data["fonte"]

            id_street = geo_data["id_rua"]
            number = geo_data["numero_do_lugar"]
            saboya_numero = geo_data["original_n"]

            coord = self.__calculate_geographical_coord(id_street, geo_data["metragem"])
            geom = self.__convert_geographical_coord_to_SRID(coord)
        return self.log

