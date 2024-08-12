import random
from telebot import types
from modules.db.models import Word, TranslatedWord, UserWordSetting
from modules.tg_bot.bot_config import CHATBOT_MESSAGE, CHATBOT_BTNS, SESSION
from modules.tg_bot.db_operations import get_user_id
from modules.tg_bot.menu import show_interaction_menu, show_word_variant_menu, show_one_item_menu
from modules.tg_bot.word_management import handle_add_word_request, handle_delete_word_request
from modules.tg_bot.bot_init import bot


@bot.message_handler(commands=['start'])
def start_message(message: types.Message) -> None:
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['start_message'])
    show_one_item_menu(
        message, CHATBOT_BTNS['test_knowledge'],
        CHATBOT_MESSAGE['second_message']
    )

    # Check if the user is already in the database
    session = SESSION
    get_user_id(session, message)
    session.close()


@bot.message_handler(content_types=['text'])
def handle_quiz_or_word_management(message: types.Message) -> None:
    """
    Handles the quiz or word management functionality of the chatbot.

    This function is triggered when the user sends a text message to the chatbot.
    It checks the message text and performs the corresponding action:
    - If the message text is 'test_knowledge' or 'next', it selects a random word from the database,
      generates a menu with word variants, and sends it to the user.
    - If the message text is 'add_word', it sends a message to the user to add a new word.
    - If the message text is 'delete_word', it sends a message to the user to delete a word.

    Parameters:
        message (types.Message): The message object containing the user's input.

    Returns:
        None
    """
    if message.text == CHATBOT_BTNS['test_knowledge'] or message.text == CHATBOT_BTNS['next']:
        session = SESSION
        user_id = get_user_id(session, message)
        words = session.query(Word).all()
        visible_words = [word for word in words if not session.query(UserWordSetting).filter_by(
            user_id=user_id, word_id=word.id, is_hidden=True
        ).first()]
        word = random.choice(visible_words)
        translations = session.query(TranslatedWord).filter_by(word_id=word.id).all()
        session.close()

        markup, word_id = show_word_variant_menu(words, word)

        if translations:
            russian_word = translations[0].translation
            bot.send_message(
                message.chat.id,
                f'Выбери перевод слова:\n🇷🇺 {russian_word}',
                reply_markup=markup
            )
        else:
            # Handling the case when there are no transfers
            bot.send_message(message.chat.id, 'Нет перевода для этого слова')

        bot.register_next_step_handler(message, validate_and_feedback_user_answer, word_id)

    if message.text == CHATBOT_BTNS['add_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['add_user_word'])
        bot.register_next_step_handler(message, handle_add_word_request)
    elif message.text == CHATBOT_BTNS['delete_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['delete_user_word'])
        bot.register_next_step_handler(message, handle_delete_word_request)


def validate_and_feedback_user_answer(message: types.Message, card: int) -> None:
    """
        Check the user's answer against the correct word and send a response message.

        Parameters:
            message (telegram.Message): The message object containing the user's answer.
            card (int): The ID of the word card.
    """
    session = SESSION
    word = session.query(Word).get(card)
    translations = session.query(TranslatedWord).filter_by(word_id=word.id).all()
    session.close()

    correct_word = word.word

    if message.text == correct_word:
        bot.send_message(message.chat.id, '✅')
        bot.send_message(
            message.chat.id,
            f'Правильно!\nСлово 🇷🇺 {correct_word} переводится как 🇺🇸 {translations[0].translation}'
        )
    else:
        bot.send_message(message.chat.id, '❌')
        bot.send_message(
            message.chat.id,
            f'Неправильно.\nПравильный ответ: {correct_word}'
        )

    show_interaction_menu(message, CHATBOT_BTNS, ['next', 'add_word', 'delete_word'])


def start_bot() -> None:
    """
    Starts the bot's polling process. This function initiates the bot's main loop,
    where it continuously checks for updates and responds to user interactions.
    """
    bot.polling()
