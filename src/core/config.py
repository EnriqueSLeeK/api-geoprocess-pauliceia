
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from typing import Optional

class Configuration(BaseSettings):
    app_name: str = "Geoprocess api"
    environment: str = "dev"
    debug: bool = True

    db_user: str
    db_password: str
    db_name: str
    db_host: str = "localhost"
    db_port: str = "5432"
    table_name: str = "places_pilot_area2"

    db_url: Optional[PostgresDsn] = None

    @field_validator("table_name", mode="before")
    @classmethod
    def validate_table_name(cls, v, values):
        import re
        if not re.fullmatch(r'\w+', v):
            raise ValueError("Invalid table name.")
        return v

    @field_validator("db_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v, values):

        if isinstance(v, str):
            return v

        db_user = values.data.get('db_user')
        db_password = values.data.get('db_password')
        db_host = values.data.get('db_host')
        db_port = values.data.get('db_port')
        db_name = values.data.get('db_name')
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    class Config:
        env_file: str  = ".env"

# Singleton para configuracao global
configuration = Configuration()

if __name__ == "__main__":
    print(configuration)
