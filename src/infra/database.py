
from sqlalchemy import create_engine, text
from core.config import configuration

engine = create_engine(str(configuration.db_url), echo=False)

def check_existence_function(func_name: str):
    result = None

    with engine.connect() as conn:
        result = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1
            FROM pg_proc
            JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid
            WHERE pg_proc.proname = :func_name
              AND pg_namespace.nspname = :schema_name
        )
        """), {"func_name": f"{func_name}", "schema_name": "public"})

    if (result is None):
        return False

    result_boolean = result.scalar_one()
    return result_boolean

# Verifica se todas a funcao saboya_geometry existe no banco de dados, caso nao sera criado
def bootstrap():
    if (not check_existence_function("saboya_geometry")):
        print("Must create function")
        pass

bootstrap()

# Area de experimentacao
if __name__ == "__main__":
    with engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id FROM places_pilot_area2 WHERE id = :id"),
            [{"id": 1}]
        )
        print(result.all())

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT saboya_geometry(:si, :me)"),
            [{"si": 1, "me": 32}]
        )
        print(result.all())

    with engine.connect() as conn:
        result = conn.execute(
                text("SELECT ST_SetSRID(ST_Point(:x, :y),4326)"),
                {"x": 13, "y": 234}
        )
        print(result.all())
    # URL para conectar no banco de dados
    print(engine.url)
    # Nome do banco de dados
    print(engine.url.database)

    # Info dos drivers
    print(engine.dialect.name)      # e.g., 'postgresql'
    print(engine.dialect.driver)    # e.g., 'psycopg2'

