import re
from telebot import types
from modules.db.models import UserWordSetting, Word
from modules.tg_bot.bot_init import bot
from modules.tg_bot.bot_config import (
    SESSION, CHATBOT_BTNS, CHATBOT_ERRORS, CHATBOT_REGEX
)
from modules.tg_bot.db_operations import (
    get_user_id,
    get_word_by_user_id,
    add_word_to_db,
    delete_word_from_db,
    inform_user_of_word_change,
    remove_word_from_view,
    word_exists_in_db
)
from modules.tg_bot.menu import show_interaction_menu


def validate_user_input(message: types.Message) \
        -> tuple[str | None, str | None]:
    """Validates user input and returns word and translation"""
    user_input: list = message.text.split(',', 1)

    if len(user_input) != 2:
        inform_user_of_word_change(message, 'add_word_value')
        return None, None

    first_name: str = user_input[0].strip().title()
    last_name: str = user_input[1].strip().title()

    return first_name, last_name


def check_word_format(
        english_pattern: str,
        russian_pattern: str,
        input_word: str,
        input_translation: str
) -> bool:
    """Checks if the input word and its translation match the given English and
    Russian patterns.

    Args:
        english_pattern (str): The pattern to match the English word against.
        russian_pattern (str): The pattern to match the Russian translation
        against.
        input_word (str): The English word to check.
        input_translation (str): The Russian translation to check.

    Returns:
        bool: True if the input word and translation match the patterns, False
        otherwise.
    """
    eng_regex = re.compile(r'^' + english_pattern + '$')
    rus_regex = re.compile(r'^' + russian_pattern + '$')
    return bool(
        eng_regex.match(input_word) and rus_regex.match(input_translation)
    )


def handle_add_word_request(message: types.Message) -> None:
    """Handles the request to add a new word to the user's word list."""
    with SESSION as session:
        user_id: int = get_user_id(session, message)

        word, translation = validate_user_input(message)

        if not word or not translation:
            return

        if not check_word_format(
                CHATBOT_REGEX['eng'],
                CHATBOT_REGEX['rus'],
                word,
                translation
        ):
            inform_user_of_word_change(message, 'add_word_value')
            return

        word_obj = get_word_by_user_id(session, word, user_id)

        if not word_obj:
            add_word_to_db(
                session,
                word,
                user_id,
                translation,
                message
            )
            inform_user_of_word_change(message, 'add', word)

        show_interaction_menu(
            message,
            CHATBOT_BTNS,
            ['next', 'add_word', 'delete_word']
        )


def handle_word_not_in_user_db(
        session: SESSION,
        user_id: int,
        word: str,
        message: types.Message
) -> None:
    """Handles the case when a word is not in the user's database."""
    if not word_exists_in_db(session, word):
        bot.send_message(message.chat.id, CHATBOT_ERRORS['word_not_found'])
        return
    with session.begin():
        remove_word_from_view(session, user_id, word)
        inform_user_of_word_change(message, 'remove', word)


def handle_word_in_user_db(
        session: SESSION,
        word_in_user_db: Word,
        message: types.Message
) -> None:
    """Handles the case when a word is in the user's database."""
    delete_word_from_db(session, word_in_user_db)
    inform_user_of_word_change(
        message,
        'delete',
        word_in_user_db.word
    )


def handle_delete_word_request(message: types.Message) -> None:
    """Handles the request to delete a word from the user's word list."""
    with SESSION as session:
        user_id: int = get_user_id(session, message)
        word: str = message.text.lower()

        word_in_user_db: Word = get_word_by_user_id(
            session,
            word,
            user_id
        )
        if word_in_user_db is None:
            handle_word_not_in_user_db(
                session,
                user_id,
                word,
                message
            )
        else:
            handle_word_in_user_db(
                session,
                word_in_user_db,
                message
            )

        session.close()
        show_interaction_menu(
            message,
            CHATBOT_BTNS,
            ['next', 'add_word', 'delete_word']
        )


def should_hide_word(
        user_word_setting: UserWordSetting, correct_answers: int
) -> bool:
    """Determines whether a word should be hidden based on the user's word
    setting and the number of correct answers."""
    return user_word_setting.correct_answers >= correct_answers
