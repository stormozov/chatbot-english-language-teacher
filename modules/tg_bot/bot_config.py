from ..db.db_session import create_db_session
from ..fs_tools.path_utils import get_absolute_path
from ..fs_tools.read_file import read_file
from ..fs_tools.read_config import read_config

path_to_config: str = get_absolute_path(['settings.ini'])
path_to_json: str = get_absolute_path(['data', 'chatbot.json'])

TG_TOKEN = read_config(path_to_config, 'TG')['token']
DB = read_config(path_to_config, 'DB')
CHATBOT_DATA = read_file(path_to_json)
CHATBOT_MESSAGE = CHATBOT_DATA['messages']
CHATBOT_BTNS = CHATBOT_DATA['buttons']
CHATBOT_ERRORS = CHATBOT_DATA['error']
CHATBOT_REGEX = CHATBOT_DATA['regex_patterns']
CHATBOT_COMMANDS = CHATBOT_DATA['commands']
SESSION = create_db_session(DB)[0]
