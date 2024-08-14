from telebot import types
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from modules.db.models import UserWordSetting, User, Word, TranslatedWord
from modules.tg_bot.bot_config import CHATBOT_ERRORS, CHATBOT_MESSAGE, SESSION
from modules.tg_bot.bot_init import bot


def check_user_in_db(session: SESSION, message: types.Message) -> User | None:
    """Checks if the user is already in the database"""
    return session.query(User).filter_by(tg_id=message.chat.id).first()


def get_user_id(session: SESSION, message: types.Message) -> int:
    """Retrieves the user ID from the database based on the provided message."""
    user = check_user_in_db(session, message)
    if user:
        return user.id


def add_new_user(session: SESSION, message: types.Message) -> None:
    """Add a new user to the database"""
    new_user = User(tg_id=message.from_user.id, username=message.from_user.username)
    session.merge(new_user)
    session.commit()


def word_exists_in_db(session: SESSION, word: str) -> Word | None:
    """
    Checks if a word exists in the database.

    Args:
        session: The database session to use for the query.
        word (str): The word to check for existence.

    Returns:
        Union[Word, None]: The Word object if the word exists, otherwise None.
    """
    return session.query(Word).filter_by(word=word).first()


def get_word_by_user_id(session: SESSION, word: str, user_id: int) -> Word | None:
    """
    Retrieves a Word object from the database based on the provided word and user ID.

    Args:
        session: The database session to use for the query.
        word (str): The word to search for in the database.
        user_id (int): The ID of the user who owns the word.

    Returns:
        Union[Word, None]: The Word object if found, otherwise None.
    """
    return session.query(Word).filter(func.lower(Word.word) == func.lower(word), Word.user_id == user_id).first()


def add_word_to_db(
        session: SESSION,
        word: str,
        user_id: int,
        translation: str,
        message: types.Message
) -> None:
    """Add a word to the database"""
    try:
        word_obj = Word(word=word, user_id=user_id, category_id=3)
        translated_word_obj = TranslatedWord(word=word_obj, translation=translation, user_id=user_id)
        user_word_setting_obj = UserWordSetting(user_id=user_id, word=word_obj)

        session.add_all([word_obj, translated_word_obj, user_word_setting_obj])
        session.commit()  # Commit the transaction
    except IntegrityError:
        session.rollback()  # Rollback the transaction on error
        bot.send_message(message.chat.id, f'Слово {word} уже добавлено в вашем словаре.')


def delete_word_from_db(session: SESSION, word_obj: Word) -> None:
    """Delete a word from the database"""
    translated_words = session.query(TranslatedWord).filter_by(word_id=word_obj.id).all()
    user_word_setting_obj = session.query(UserWordSetting).filter_by(word_id=word_obj.id).first()

    for translated_word in translated_words:
        session.delete(translated_word)

    if user_word_setting_obj:
        session.delete(user_word_setting_obj)

    session.delete(word_obj)
    session.commit()


def remove_word_from_view(session: SESSION, user_id: int, word: str) -> None:
    """Remove a word from the view"""
    word_id = word_exists_in_db(session, word).id
    existing_setting = session.query(UserWordSetting).filter_by(user_id=user_id, word_id=word_id).first()

    if existing_setting:
        existing_setting.is_hidden = True
    else:
        remove = UserWordSetting(user_id=user_id, word_id=word_id, is_hidden=True)
        session.add(remove)

    session.commit()


def inform_user_of_word_change(message: types.Message, action: str, word: str | None = None) -> None:
    """Inform the user of the change in the dictionary"""
    messages = {
        'add': f'Слово "{word}" и его перевод добавлены успешно!',
        'delete': f'Слово "{word}" и его переводы удалены успешно!',
        'remove': f'Слово "{word}" было скрыто из вашей выборки',
        'add_word_value': CHATBOT_ERRORS['add_word_value'],
        'learn_all_words': CHATBOT_ERRORS['learn_all_words'],
        'learned_word': f'Слово "{word}"' + CHATBOT_MESSAGE['learned_word']
    }
    bot.send_message(message.chat.id, messages.get(action, 'Unknown action'))
