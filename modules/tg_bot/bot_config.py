from modules.db.db_session import create_db_session
from modules.fs_tools.path_utils import get_absolute_path
from modules.read_file.read_file import read_file
from modules.config.read_config import read_config

path_to_config: str = get_absolute_path(['settings.ini'])
path_to_json: str = get_absolute_path(['data', 'chatbot.json'])

TG_TOKEN = read_config(path_to_config, 'TG')['token']
DB = read_config(path_to_config, 'DB')
CHATBOT_DATA = read_file(path_to_json)
CHATBOT_MESSAGE = CHATBOT_DATA['messages']
CHATBOT_BTNS = CHATBOT_DATA['buttons']
CHATBOT_ERRORS = CHATBOT_DATA['error']
CHATBOT_REGEX = CHATBOT_DATA['regex_patterns']
SESSION = create_db_session(DB)[0]
