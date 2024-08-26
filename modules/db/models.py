from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """Define the User database model.

    Attributes:
        id (int): The primary key for the User.
        tg_id (int): The Telegram ID of the User.
        created_at (datetime): The timestamp when the User record was created.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)


class Word(Base):
    """Define the Word database model.

    Attributes:
        id (int): The primary key for the Word.
        word (str): The actual word.
        translation (str): The translation of the word.
        user_id (int): Foreign key reference to the User who added this word.
    """
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    translation = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='added_words')


class UserWordSetting(Base):
    """Define the UserWordSetting database model.

    Attributes:
        id (int): The primary key for the UserWordSetting.
        user_id (int): Foreign key reference to the User associated
            with this setting.
        word_id (int): Foreign key reference to the Word associated
            with this setting.
        is_hidden (bool): Indicates if the word setting is hidden.
        correct_answers (int): The number of correct answers.
        last_shown_at (datetime): The timestamp of the last time
            the word was shown.
    """
    __tablename__ = 'user_word_settings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    word_id = Column(Integer, ForeignKey('words.id'))
    is_hidden = Column(Boolean, default=False)
    correct_answers = Column(Integer, default=0)
    last_shown_at = Column(DateTime, default=datetime.now)
    user = relationship('User', backref='user_word_settings')
    word = relationship('Word', backref='user_word_settings')
