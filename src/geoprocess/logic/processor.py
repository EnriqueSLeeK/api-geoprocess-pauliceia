from typing import List
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from schemas.place_schema import lugares_area_piloto2
from infra.database import engine, Session
from dto.input_data import InputData
from dto.return_data import ReturnData, log_entry_factory, LogEntry


# Em todas as queries dinamicas usam queries parametrizadas
class GeoProcessor:
    def __init__(self, data: List[InputData]):
        self.index = 0
        self.geo_data_list: List[InputData] = data

        self.log: ReturnData = {"log_sucesso": [], "log_erro": []}

    def __fail_log(self, log: LogEntry):
        self.log["log_erro"].append(log)

    def __success_log(self, log: LogEntry):
        self.log["log_sucesso"].append(log)

    def __prepare_date(self, date_string: str):
        splitted_date = [
            int(date_component) for date_component in date_string.split("/")
        ]

        return splitted_date

    # Nao se confunda: Na funcao do saboya_geometry definida no banco pede
    # o numberPlace, mas na verdade ele quer a metragem do imovel na rua
    def __calculate_geographical_coord(self, street_id: int, metragem: float):
        geographical_coordinates = None
        try:
            with engine.connect() as conn:
                geographical_coordinates = conn.execute(
                    text(
                        "SELECT saboya_geometry(:street_id, :metragem) AS saboya_geometry"
                    ),
                    {"street_id": street_id, "metragem": metragem},
                )
                result = geographical_coordinates.scalar_one()
                return result
        except SQLAlchemyError as e:
            self.__fail_log(
                log_entry_factory(self.index, f"Erro no banco de dados: {str(e)}")
            )
            return None

    def __convert_geographical_coord_to_SRID(self, coord):
        geo_coord_srid = None
        try:
            with engine.connect() as conn:
                geo_coord_srid = conn.execute(
                    text("SELECT ST_GeomFromText(:point, 4326)"),
                    {"point": coord},
                )
            result = geo_coord_srid.scalar_one()
            return result
        except SQLAlchemyError as e:
            self.__fail_log(
                log_entry_factory(self.index, f"Erro no banco de dados: {str(e)}")
            )
            return None

    def __get_max_id(self):
        res = None
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT MAX(id) FROM places_pilot_area2"))
                return res.scalar_one()
        except SQLAlchemyError as e:
            self.__fail_log(
                log_entry_factory(self.index, f"Erro no banco de dados: {str(e)}")
            )
            return None

    def __insert_data(self, item):
        lugar = lugares_area_piloto2(
            id=self.__get_max_id() + 1,
            id_street=item["id_street"],
            number=item["number"],
            original_n=item["original_n"],
            source=item["source"],
            author=item["author"],
            date=item["date"],
            first_day=item["first_day"],
            first_month=item["first_month"],
            first_year=item["first_year"],
            last_day=item["last_day"],
            last_month=item["last_month"],
            last_year=item["last_year"],
            geom=item["geom"],
        )

        with Session() as session_sql:
            try:
                session_sql.add(lugar)
                session_sql.commit()
                self.__success_log(
                    log_entry_factory(self.index, "Operacao feita com sucesso!")
                )
            except SQLAlchemyError as e:
                session_sql.rollback()
                self.__fail_log(
                    log_entry_factory(self.index, f"Falha na insercao: {str(e)}")
                )

    def __check_date_ok(self, which, date):
        try:
            day, month, year = date
            return [day, month, year]
        except ValueError:
            self.__fail_log(
                log_entry_factory(
                    self.index,
                    f"Erro: Data {'data_' + which} incompleta, por favor verificar a sua data.",
                )
            )
            return None

    def process_data(self) -> ReturnData:
        for index, geo_data in enumerate(self.geo_data_list):
            self.index = index + 1
            item = {}
            item["date"] = geo_data.data
            item["author"] = geo_data.autor
            item["source"] = geo_data.fonte

            item["id_street"] = geo_data.id_rua
            item["number"] = geo_data.numero_lugar
            item["original_n"] = geo_data.saboya_numero

            item["coord"] = self.__calculate_geographical_coord(
                item["id_street"], geo_data.metragem
            )

            if item["coord"] is None:
                continue

            item["geom"] = self.__convert_geographical_coord_to_SRID(item["coord"])

            if item["geom"] is None:
                continue

            try:
                item["first_day"], item["first_month"], item["first_year"] = (
                    self.__check_date_ok(
                        "inicio", self.__prepare_date(geo_data.data_inicio)
                    )
                )

                item["last_day"], item["last_month"], item["last_year"] = (
                    self.__check_date_ok(
                        "final", self.__prepare_date(geo_data.data_final)
                    )
                )

            except Exception:
                # As excecoes vao ser gravadas nos metodos
                continue

            self.__insert_data(item)

        return self.log
