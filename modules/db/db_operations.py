from .models import Base


def create_tables(engine):
    """Creates all tables in the database"""
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """Drops all tables in the database"""
    Base.metadata.drop_all(engine)
