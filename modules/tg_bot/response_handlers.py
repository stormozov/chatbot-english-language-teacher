from telebot import types
from .bot_init import bot
from .bot_config import CHATBOT_ERRORS, CHATBOT_MESSAGE


def inform_user_of_word_change(
        user_message: types.Message,
        operation: str,
        word: str | None = None
) -> None:
    """Inform the user of the change in the dictionary

    Args:
        user_message (types.Message): The message object from the user.
        operation (str): The operation to be performed on the word.
        word (str | None, optional): The word to be added or deleted.

    Returns:
        None
    """
    response_messages: dict[str, str] = {
        'add': f'Слово "{word}" и его перевод добавлены успешно!',
        'delete': f'Слово "{word}" и его переводы удалены успешно!',
        'remove': f'Слово "{word}" было скрыто из вашей выборки',
        'add_word_value': CHATBOT_ERRORS['add_word_value'],
        'learn_all_words': CHATBOT_ERRORS['learn_all_words'],
        'learned_word': f'Слово "{word}"' + CHATBOT_MESSAGE['learned_word']
    }
    bot.send_message(
        user_message.chat.id, response_messages.get(operation, 'Unknown action')
    )
