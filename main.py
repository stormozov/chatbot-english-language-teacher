from modules.fs_tools.read_config import read_config
from modules.db.db_operations import create_tables
from modules.db.db_session import create_db_session
from modules.fs_tools.path_utils import get_absolute_path
from modules.db.json2db import import_json_data_to_db
from modules.tg_bot.bot import start_bot


def bootstrap_database():
    # Get absolute path to config and data files
    path_to_config: str = get_absolute_path(['settings.ini'])
    path_to_json: str = get_absolute_path(['data', 'words.json'])

    DB = read_config(path_to_config, 'DB')

    engine = create_db_session(DB)[1]

    # Create tables in the database if they don't exist
    create_tables(engine)

    # Create a session for working with the database
    session = create_db_session(DB)[0]

    # Import data from a JSON file to the database
    import_json_data_to_db(session, path_to_json)

    session.close()


if __name__ == '__main__':
    bootstrap_database()
    start_bot()
