from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    words = relationship('Word', backref='category')


class Words(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    translations = relationship('Translation', backref='word')
    category = relationship('Category', backref='words')


class Translations(Base):
    __tablename__ = 'translations'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    translation = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    words = relationship('UserWord', backref='user')
    added_words = relationship('UserAddedWord', backref='user')


class UserWords(Base):
    __tablename__ = 'user_words'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    learned = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    words = relationship('Word', backref='user_words')
