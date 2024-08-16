from telebot import types

from modules.tg_bot.response_handlers import inform_user_of_word_change


def split_user_input(message: types.Message) -> list:
    """Splits the user input into two parts: word and translation."""
    return message.text.split(',', 1)


def validate_user_input_parts(
        message: types.Message, user_input_parts: list
) -> tuple[str | None, str | None]:
    """Validates user input parts and returns first and last names.

    If the user input doesn't contain two parts, sends a message to the user
    and returns None for both first and last names.

    Args:
        message: The message object from the user.
        user_input_parts: The list of user input parts.

    Returns:
        tuple[str | None, str | None]: A tuple of first name and last name.
    """
    if len(user_input_parts) != 2:
        inform_user_of_word_change(message, 'add_word_value')
        return None, None

    first_name: str = user_input_parts[0].strip().title()
    last_name: str = user_input_parts[1].strip().title()

    return first_name, last_name


def validate_user_input(message: types.Message) \
        -> tuple[str | None, str | None]:
    """Validates user input and returns first and last names."""
    user_input: list = split_user_input(message)
    return validate_user_input_parts(message, user_input)
