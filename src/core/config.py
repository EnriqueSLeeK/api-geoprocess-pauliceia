
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

    @field_validator("db_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v, values):
        if isinstance(v, str):
            return v
        data = values.data
        return f"postgresql://{data['db_user']}:{data['db_password']}@{data['db_host']}:{data['db_port']}/{data['db_name']}"

    class Config:
        env_file: str  = ".env"

# Singleton para configuracao global
configuration = Configuration()

if __name__ == "__main__":
    print(configuration)
