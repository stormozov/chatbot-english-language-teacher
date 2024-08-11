import random
from telebot import types
from modules.db.models import Word, TranslatedWord, UserWordSetting, User
from modules.tg_bot.bot_config import CHATBOT_MESSAGE, CHATBOT_BTNS, SESSION
from modules.tg_bot.db_operations import get_user_id, add_new_user
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
    user = get_user_id(session, message)

    if not user:
        # If the user is not in the database, add them to the database
        add_new_user(session, message)

    session.close()


@bot.message_handler(content_types=['text'])
def handle_quiz_or_word_management(message: types.Message) -> None:
    """
        A function that handles text messages from the user.
        It generates answer choices for a quiz based on the user's text input.
    """
    if message.text == CHATBOT_BTNS['test_knowledge'] or message.text == CHATBOT_BTNS['next']:
        session = SESSION
        words = session.query(Word).all()
        word = random.choice(words)
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
