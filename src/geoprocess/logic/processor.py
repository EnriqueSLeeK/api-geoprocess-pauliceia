from typing import List
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from core.config import configuration
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

    # Favor remover isso depois e colocar a logica de geracao de id no banco de dados
    def __get_max_id(self):
        res = None
        statement = f"SELECT MAX(id) FROM {configuration.table_name}"
        try:
            with engine.connect() as conn:
                res = conn.execute(
                    text(statement)
                )
                return res.scalar_one() or 0
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

    def extract_and_convert_data(self, geo_data):
        item = {}

        item["coord"] = self.__calculate_geographical_coord(
            geo_data.id_rua, geo_data.metragem
        )
        if item["coord"] is None:
            raise ValueError()

        item["geom"] = self.__convert_geographical_coord_to_SRID(item["coord"])
        if item["geom"] is None:
            raise ValueError()

        item["date"] = geo_data.data
        item["author"] = geo_data.autor
        item["source"] = geo_data.fonte

        item["id_street"] = geo_data.id_rua
        item["number"] = geo_data.numero_lugar
        item["original_n"] = geo_data.saboya_numero


        item["first_day"], item["first_month"], item["first_year"] = [
            int(date_component) for date_component in geo_data.data_inicio.split("/")
        ]

        item["last_day"], item["last_month"], item["last_year"] = (
            [None, None, None]
            if geo_data.data_final is None or geo_data.data_final == ""
            else [
                int(date_component) for date_component in geo_data.data_final.split("/")
            ]
        )

        return item

    def __check_existence(self, geo_data):

        # Sera considerado um endereco duplicado se todos
        # os requisitos a seguir forem satisfeitos:
        #  id da rua
        #  numero do edificio
        #  primeiro dia, mes e ano do emplacamento

        first_date = [int(date_component) for date_component in geo_data.data_inicio.split('/')]

        query_str = f"""
            SELECT 1 FROM {configuration.table_name}
            WHERE id_street = :id_street
              AND number = :number
              AND first_day = :first_day
              AND first_month = :first_month
              AND first_year = :first_year
            LIMIT 1
        """

        with engine.connect() as conn:
            result = conn.execute(
                text(query_str),
                {
                    "id_street": geo_data.id_rua,
                    "number": geo_data.numero_lugar,
                    "first_day": first_date[0],
                    "first_month": first_date[1],
                    "first_year": first_date[2],
                }
            ).scalar()

        if result:
            self.__fail_log(
                log_entry_factory(
                    self.index,
                    "O dado já existe"
                )
            )
            raise ValueError()


    def process_data(self) -> ReturnData:
        for index, geo_data in enumerate(self.geo_data_list):
            self.index = index + 1
            try:
                self.__check_existence(geo_data)
                item = self.extract_and_convert_data(geo_data)
            except Exception as e:
                continue

            self.__insert_data(item)

        return self.log
