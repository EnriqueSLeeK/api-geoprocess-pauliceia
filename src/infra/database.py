
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import configuration

engine = create_engine(str(configuration.db_url), echo=False)
Session = sessionmaker(bind=engine)

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

def execute_option(session: Session, file_path: str) -> bool:
    return

# Verifica se todas a funcao saboya_geometry existe no banco de dados, caso nao sera criado
def bootstrap():
    if (not check_existence_function("saboya_geometry")):
        with Session() as session_sql:
            execute_option(session_sql, path)
        print("Must create function")

bootstrap()

# Area de experimentacao
if __name__ == "__main__":
    # URL para conectar no banco de dados
    print(engine.url)
    # Nome do banco de dados
    print(engine.url.database)

    # Info dos drivers
    print(engine.dialect.name)      # e.g., 'postgresql'
    print(engine.dialect.driver)    # e.g., 'psycopg2'

    from pathlib import Path
    project_root = Path(__file__).resolve().parents[1]

