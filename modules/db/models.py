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
        username (str): The username of the User, must be unique and cannot be null.
        created_at (datetime): The timestamp when the User record was created.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)


class Category(Base):
    """Define the Category database model.

    Attributes:
        id (int): The primary key for the Category.
        title (str): The title of the Category, must be unique and cannot be null.
    """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)


class Word(Base):
    """Define the Word database model.

    Attributes:
        id (int): The primary key for the Word.
        word (str): The actual word, must be unique and cannot be null.
        category_id (int): Foreign key reference to the Category this word belongs to.
        user_id (int): Foreign key reference to the User who added this word.
    """
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", backref="words")
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref="added_words")


class TranslatedWord(Base):
    """Define the TranslatedWord database model.

    Attributes:
        id (int): The primary key for the TranslatedWord.
        word_id (int): Foreign key reference to the Word this translation belongs to.
        translation (str): The translated word, cannot be null.
        user_id (int): Foreign key reference to the User who added this translation.
    """
    __tablename__ = 'translated_words'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'))
    translation = Column(String, nullable=False)
    word = relationship("Word", backref="translated_words")
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref="added_translations")


class UserWordSetting(Base):
    """Define the UserWordSetting database model.

    Attributes:
        id (int): The primary key for the UserWordSetting.
        user_id (int): Foreign key reference to the User associated with this setting.
        word_id (int): Foreign key reference to the Word associated with this setting.
        is_hidden (bool): Indicates if the word setting is hidden, default is False.
        is_deleted (bool): Indicates if the word setting is deleted, default is False.
        user (relationship): Relationship to the User model.
        word (relationship): Relationship to the Word model.
    """
    __tablename__ = 'user_word_settings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    word_id = Column(Integer, ForeignKey('words.id'))
    is_hidden = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    user = relationship("User", backref="user_word_settings")
    word = relationship("Word", backref="user_word_settings")
