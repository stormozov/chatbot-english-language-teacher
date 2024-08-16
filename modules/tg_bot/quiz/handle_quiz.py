import random

from sqlalchemy import or_
from telebot import types

from modules.db.models import Word, TranslatedWord, UserWordSetting
from modules.tg_bot.bot_config import CHATBOT_MESSAGE, SESSION
from modules.tg_bot.bot_init import bot
from modules.tg_bot.db.user_db_utils import get_user_id
from modules.tg_bot.quiz.quiz_validator import validate_and_feedback_user_answer
from modules.tg_bot.ui.quiz_menu import show_word_variant_menu
from modules.tg_bot.response_handlers import inform_user_of_word_change


@bot.message_handler(commands=['test_knowledge', 'next'])
def handle_quiz(message: types.Message) -> None:
    """Handles the 'test_knowledge' and 'next' commands.

    Retrieves a list of words from the database based on the user's ID,
    filters out hidden words, and randomly selects a word for the user to
    translate. If the word has translations, it sends a message to the user
    with the translation options; otherwise, it sends a message indicating
    that no translations were found.

    Args:
        message (types.Message): The user's message that triggered this function

    Returns:
        None
    """
    session = SESSION
    user_id: int = get_user_id(session, message)
    user_id_condition = or_(Word.user_id.is_(None), Word.user_id == user_id)
    words: list = session.query(Word).filter(user_id_condition).all()
    hidden_word_settings: list = (
        session
        .query(UserWordSetting)
        .filter_by(user_id=user_id, is_hidden=True)
    )

    hidden_word_ids: list[int] = [
        setting.word_id
        for setting in hidden_word_settings
    ]

    visible_words: list[Word] = [
        word
        for word in words
        if word.id not in hidden_word_ids
    ]

    if not visible_words:
        inform_user_of_word_change(message, 'learn_all_words')
        return

    word: Word = random.choice(visible_words)
    user_word_setting: UserWordSetting = (
        session
        .query(UserWordSetting)
        .filter_by(user_id=user_id, word_id=word.id)
        .first()
    )

    if user_word_setting is None:
        user_word_setting: UserWordSetting = UserWordSetting(
            user_id=user_id, word_id=word.id,
            correct_answers=0, is_hidden=False
        )
        session.add(user_word_setting)
        session.commit()

    translations: list[TranslatedWord] = (
        session
        .query(TranslatedWord)
        .filter_by(word_id=word.id)
        .all()
    )

    if translations:
        russian_word: str = translations[0].translation
        bot.send_message(
            message.chat.id,
            f'Выбери перевод слова:\n🇷🇺 {russian_word}',
            reply_markup=show_word_variant_menu(words, word)
        )
    else:
        # Handling the case when there are no transfers
        bot.send_message(
            message.chat.id, CHATBOT_MESSAGE['not_found_translated_word']
        )

    bot.register_next_step_handler(
        message,
        validate_and_feedback_user_answer,
        user_word_setting,
        word,
        translations
    )
