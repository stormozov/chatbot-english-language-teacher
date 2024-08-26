from telebot import types
from modules.db.models import User
from modules.tg_bot.bot_config import SESSION


def check_user_in_db(session: SESSION, message: types.Message) -> User | None:
    """Checks if the user is already in the database"""
    return session.query(User).filter_by(tg_id=message.chat.id).first()


def get_user_id(session: SESSION, message: types.Message) -> int | None:
    """Retrieve the user ID from the database based on the provided message."""
    user: User = check_user_in_db(session, message)
    return user.id if user else None


def add_new_user(session: SESSION, message: types.Message) -> None:
    """Add a new user to the database"""
    new_user = User(tg_id=message.chat.id)
    session.merge(new_user)
    session.commit()
