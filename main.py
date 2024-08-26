from modules.fs_tools.read_config import read_config
from modules.db import create_tables, create_db_session, import_json_data_to_db
from modules.fs_tools import get_absolute_path
from modules.tg_bot import start_bot


def bootstrap_db():
    # Get absolute path to config and data files
    path_to_config: str = get_absolute_path(['settings.ini'])
    path_to_json: str = get_absolute_path(['data', 'words.json'])

    DB = read_config(path_to_config, 'DB')

    engine = create_db_session(DB)[1]

    # Create tables in the database if they don't exist
    create_tables(engine)

    # Create a session for working with the database
    with create_db_session(DB)[0] as session:
        # Import data from a JSON file to the database
        import_json_data_to_db(session, path_to_json)


if __name__ == '__main__':
    bootstrap_db()
    start_bot()
