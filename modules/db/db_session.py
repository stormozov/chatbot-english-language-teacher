from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_db_session(config_dict: dict) -> tuple:
    """Creates a session for working with the database"""
    dbms, user, password, host, port, dbname = config_dict.values()
    DSN = f'{dbms}://{user}:{password}@{host}:{port}/{dbname}'
    engine = create_engine(DSN)
    Session = sessionmaker(bind=engine)

    return Session(), engine
