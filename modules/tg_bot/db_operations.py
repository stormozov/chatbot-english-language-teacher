from typing import Union
from telebot import types
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from modules.db.models import UserWordSetting, User, Word, TranslatedWord
from modules.tg_bot.bot_init import bot


def get_user_id(session, message: types.Message) -> int:
    """Retrieves the user ID from the database based on the provided message."""
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()

    if user is None:
        add_new_user(session, message)

    return user.id


def add_new_user(session, message: types.Message) -> None:
    """Add a new user to the database"""
    new_user = User(tg_id=message.from_user.id, username=message.from_user.username)
    session.add(new_user)
    session.commit()


def check_word_in_db(session, word: str) -> Union[Word, None]:
    """Check if the word is in the database"""
    return session.query(Word).filter_by(word=word).first()


def get_word_obj(session, word: str, user_id: int) -> Union[Word, None]:
    """Get the word object from the database"""
    return session.query(Word).filter(func.lower(Word.word) == func.lower(word), Word.user_id == user_id).first()


def add_word_to_db(
        session, word: str, user_id: int,
        translation: str, message: types.Message
) -> None:
    """Add a word to the database"""
    try:
        word_obj = Word(word=word, user_id=user_id)
        translated_word_obj = TranslatedWord(word=word_obj, translation=translation, user_id=user_id)
        user_word_setting_obj = UserWordSetting(user_id=user_id, word=word_obj)

        session.add_all([word_obj, translated_word_obj, user_word_setting_obj])
        session.commit()  # Commit the transaction
    except IntegrityError as e:
        session.rollback()  # Rollback the transaction on error
        bot.send_message(message.chat.id, f'Слово {word} уже добавлено в вашем словаре.')


def delete_word_from_db(session, word_obj: Word) -> None:
    """Delete a word from the database"""
    translated_words = session.query(TranslatedWord).filter_by(word_id=word_obj.id).all()
    user_word_setting_obj = session.query(UserWordSetting).filter_by(word_id=word_obj.id).first()

    for translated_word in translated_words:
        session.delete(translated_word)

    if user_word_setting_obj:
        session.delete(user_word_setting_obj)

    session.delete(word_obj)
    session.commit()


def remove_word_from_view(session, user_id: int, word: str) -> None:
    """Remove a word from the view"""
    word_id = check_word_in_db(session, word).id
    existing_setting = session.query(UserWordSetting).filter_by(user_id=user_id, word_id=word_id).first()

    if existing_setting:
        existing_setting.is_hidden = True
    else:
        remove = UserWordSetting(user_id=user_id, word_id=word_id, is_hidden=True)
        session.add(remove)

    session.commit()


def inform_user_of_word_change(message: types.Message, word: str, action: str) -> None:
    """Inform the user of the change in the dictionary"""
    messages = {
        'add': f'Слово "{word}" и его перевод добавлены успешно!',
        'delete': f'Слово "{word}" и его переводы удалены успешно!',
        'remove': f'Слово "{word}" было скрыто из вашей выборки'
    }
    bot.send_message(message.chat.id, messages.get(action, 'Unknown action'))
