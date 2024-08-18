from sqlalchemy import func, or_
from modules.db.models import TranslatedWord, UserWordSetting, Word
from modules.tg_bot.bot_config import SESSION


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


def get_all_user_words(session: SESSION, user_id: int) -> list[Word]:
    """Retrieves all words for a specific user.

    This function queries the database to retrieve all words that are
    assigned to a given user or have no user assigned.

    Args:
        session (SESSION): The database session.
        user_id (int): The ID of the user.

    Returns:
        list[Word]: A list of words for the user.
    """
    user_id_condition = or_(Word.user_id.is_(None), Word.user_id == user_id)

    return session.query(Word).filter(user_id_condition).all()


def get_hidden_word_settings(session: SESSION, user_id: int) \
        -> list[UserWordSetting]:
    """Retrieves the hidden word settings for a specific user.

    This function queries the database to retrieve the word settings that are
    marked as hidden for a given user.

    Args:
        session (SESSION): The database session.
        user_id (int): The ID of the user.

    Returns:
        list[UserWordSetting]: A list of hidden word settings for the user.
    """
    return (
        session
        .query(UserWordSetting)
        .filter_by(user_id=user_id, is_hidden=True)
    )


def get_user_word_setting(session: SESSION, user_id: int, word_id: int) \
        -> UserWordSetting:
    """Retrieves or creates the user's word setting.

    This function retrieves the user's word setting for a given word.
    If the setting does not exist, it creates a new one with default values.

    Args:
        session (SESSION): The database session.
        user_id (int): The ID of the user.
        word_id (int): The ID of the word.

    Returns:
        UserWordSetting: The user's word setting.
    """
    user_word_setting: UserWordSetting = (
        session
        .query(UserWordSetting)
        .filter_by(user_id=user_id, word_id=word_id)
        .first()
    )

    if user_word_setting is None:
        user_word_setting = UserWordSetting(
            user_id=user_id, word_id=word_id,
            correct_answers=0, is_hidden=False
        )
        session.add(user_word_setting)
        session.commit()

    return user_word_setting


def get_all_translations_word(session: SESSION, word_id: int) \
        -> list[TranslatedWord]:
    """Retrieves the translations for a given word.

    This function queries the database to retrieve the translations for a word
    with the specified ID.

    Args:
        session (SESSION): The database session.
        word_id (int): The ID of the word.

    Returns:
        list[TranslatedWord]: A list of translations for the word.
    """
    return (
        session
        .query(TranslatedWord)
        .filter_by(word_id=word_id)
        .all()
    )
