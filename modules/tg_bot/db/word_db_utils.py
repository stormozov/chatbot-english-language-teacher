from telebot import types
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from modules.db.models import UserWordSetting, Word, TranslatedWord
from modules.tg_bot.bot_config import SESSION
from modules.tg_bot.bot_init import bot


def word_exists_in_db(session: SESSION, word: str) -> Word | None:
    """Checks if a word exists in the database.

    Args:
        session: The database session to use for the query.
        word (str): The word to check for existence.

    Returns:
        Word | None: The Word object if the word exists, otherwise None.
    """
    return session.query(Word).filter_by(word=word).first()


def get_word_by_user_id(
        session: SESSION, word: str, user_id: int
) -> Word | None:
    """Retrieves a Word object from the database based on the provided word
    and user ID.

    Args:
        session: The database session to use for the query.
        word (str): The word to search for in the database.
        user_id (int): The ID of the user who owns the word.

    Returns:
        Word | None: The Word object if found, otherwise None.
    """
    filter_condition: tuple = (
        func.lower(Word.word) == func.lower(word),
        Word.user_id == user_id
    )
    return session.query(Word).filter(*filter_condition).first()


def add_word_to_db(
        session: SESSION,
        word: str,
        user_id: int,
        translation: str,
        message: types.Message
) -> None:
    """Add a word to the database"""
    try:
        word_obj: Word = Word(word=word, user_id=user_id, category_id=3)
        translated_word_obj: TranslatedWord = TranslatedWord(
            word=word_obj,
            translation=translation,
            user_id=user_id
        )
        user_word_setting_obj: UserWordSetting = UserWordSetting(
            user_id=user_id, word=word_obj
        )

        session.add_all([word_obj, translated_word_obj, user_word_setting_obj])
        session.commit()
    except IntegrityError:
        session.rollback()
        bot.send_message(
            message.chat.id,
            f'Слово {word} уже добавлено в вашем словаре.'
        )


def delete_word_from_db(session: SESSION, word_obj: Word) -> None:
    """Delete a word from the database"""
    translated_words: list = (
        session
        .query(TranslatedWord)
        .filter_by(word_id=word_obj.id)
        .all()
    )

    user_word_setting_obj: UserWordSetting = (
        session
        .query(UserWordSetting)
        .filter_by(word_id=word_obj.id)
        .first()
    )

    for translated_word in translated_words:
        session.delete(translated_word)

    if user_word_setting_obj:
        session.delete(user_word_setting_obj)

    session.delete(word_obj)
    session.commit()


def remove_word_from_view(session: SESSION, user_id: int, word: str) -> None:
    """Remove a word from the view"""
    word_id: int = word_exists_in_db(session, word).id
    existing_setting: UserWordSetting = (
        session
        .query(UserWordSetting)
        .filter_by(user_id=user_id, word_id=word_id)
        .first()
    )

    if existing_setting:
        existing_setting.is_hidden = True
    else:
        hidden_setting: UserWordSetting = UserWordSetting(
            user_id=user_id, word_id=word_id, is_hidden=True
        )
        session.add(hidden_setting)

    session.commit()
