import random

from telebot import types

from modules.db.models import Word, UserWordSetting
from modules.tg_bot.bot_config import SESSION
from modules.tg_bot.bot_init import bot
from modules.tg_bot.db.user_db_utils import get_user_id, handle_new_user
from modules.tg_bot.db.word_db_utils import (
    get_all_user_words, get_hidden_word_settings, get_user_word_setting
)
from modules.tg_bot.quiz.quiz_validator import validate_and_feedback_user_answer
from modules.tg_bot.ui.quiz_menu import show_word_variant_menu
from modules.tg_bot.response_handlers import inform_user_of_word_change


@bot.message_handler(commands=['test_knowledge', 'next'])
def handle_quiz(message: types.Message) -> None:
    """Handles the 'test_knowledge' and 'next' commands.

    This function is responsible for testing the user's knowledge of words.
    It selects a random word from the list of visible words for the user,
    sends the word's translation to the user, and registers a callback
    to handle the user's response.

    Args:
        message (types.Message): The message that triggered this function.

    Returns:
        None
    """
    session = SESSION
    handle_new_user(message)
    user_id: int = get_user_id(session, message)
    all_user_words: list = get_all_user_words(session, user_id)
    visible_words: list[Word] = get_visible_words(
        session, user_id, all_user_words
    )

    if not visible_words:
        inform_user_of_word_change(message, 'learn_all_words')
        return

    target_word: Word = get_random_word(visible_words)
    user_word_setting = get_user_word_setting(
        session, user_id, target_word.id
    )

    send_message_to_user(
        message,
        all_user_words,
        target_word,
        target_word.translation
    )
    register_validation_step(
        message,
        user_word_setting,
        target_word
    )


def get_random_word(visible_words: list[Word]) -> Word:
    """Selects a random word from a list of visible words.

    Args:
        visible_words (list[Word]): A list of visible words.

    Returns:
        Word: A random word from the list of visible words.
    """
    return random.choice(visible_words)


def get_visible_words(session: SESSION, user_id: int, user_words: list[Word]) \
        -> list[Word]:
    """Retrieves a list of visible words for a specific user.

    Parameters:
        session (SESSION): The database session.
        user_id (int): The ID of the user.
        user_words (list[Word]): The list of user words.

    Returns:
        list[Word]: A list of visible words for the user.
    """
    hidden_settings: list = get_hidden_word_settings(session, user_id)
    hidden_word_ids: list[int] = [
        setting.word_id
        for setting in hidden_settings
    ]

    return [word for word in user_words if word.id not in hidden_word_ids]


def send_message_to_user(
        message: types.Message, user_words: list[Word], target_word: Word,
        translation: str
):
    """Sends a message to the user with the word's translation.

    This function sends a message to the user with the translation of the
    target word. If the translation is available, it also includes a menu
    with word variants. If the translation is not available, it sends a
    corresponding error message.

    Args:
        message (types.Message): The message that triggered this function.
        user_words (list[Word]): The list of words for the user.
        target_word (Word): The target word being tested.
        translation (str): The translation of the target word.

    Returns:
        None
    """
    markup: types.ReplyKeyboardMarkup = show_word_variant_menu(
        user_words, target_word
    )
    bot.send_message(
        message.chat.id,
        f'Выбери перевод слова:\n🇷🇺 {translation}',
        reply_markup=markup
    )


def register_validation_step(
        message: types.Message,
        user_word_setting: UserWordSetting,
        word: Word
):
    """Registers the next step handler for the user's response.

    This function registers a callback to handle the user's response
    to the word's translation. It uses the provided user word setting,
    word, and translations to determine the correct response.

    Args:
        message (types.Message): The message that triggered this function.
        user_word_setting (UserWordSetting): The user's word setting.
        word (Word): The word being tested.

    Returns:
        None
    """
    bot.register_next_step_handler(
        message,
        validate_and_feedback_user_answer,
        user_word_setting,
        word,
        word.translation
    )
