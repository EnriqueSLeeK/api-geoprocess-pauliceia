
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
            item = {}
            try:
                item["first_day"],\
                item["first_month"],\
                item["first_year"]= self.__check_date_ok(index, "inicio",
                              self.__prepare_date(geo_data["data_inicio"]))
                item["last_day"],\
                item["last_month"],\
                item["last_year"]= self.__check_date_ok(index, "final",
                               self.__prepare_date(geo_data["data_final"]))
            except Exception:
                continue

            item["date"]= geo_data["data"]
            item["author"] = geo_data["autor"]
            item["source"] = geo_data["fonte"]

            item["id_street"] = geo_data["id_rua"]
            item["number"] = geo_data["numero_do_lugar"]
            item["saboya_numero"] = geo_data["original_n"]

            item["coord"] = self.__calculate_geographical_coord(item["id_street"], geo_data["metragem"])
            item["geom"] = self.__convert_geographical_coord_to_SRID(item["coord"])

        return self.log

