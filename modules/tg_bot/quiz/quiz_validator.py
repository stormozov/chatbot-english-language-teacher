from datetime import datetime

from telebot import types

from modules.db.models import UserWordSetting, Word
from modules.tg_bot.bot_config import CHATBOT_BTNS, CHATBOT_DATA, SESSION
from modules.tg_bot.bot_init import bot
from modules.tg_bot.response_handlers import inform_user_of_word_change
from modules.tg_bot.ui.nav_menu import show_interaction_menu


def validate_and_feedback_user_answer(
    message: types.Message,
    user_word_setting: UserWordSetting,
    selected_word: Word,
    translations: list
) -> None:
    """Validates user's response and provides feedback based on its accuracy.

    Args:
        message (types.Message): The user's message to be validated.
        user_word_setting (UserWordSetting): The user's word setting.
        selected_word (Word): Selected word to be checked against
            the user's response.
        translations (list): A list of translations for the selected word.

    Returns:
        None
    """
    session = SESSION
    correct_answer: str = selected_word.word
    is_correct: bool = message.text == correct_answer

    send_feedback_message(
        message,
        is_correct,
        correct_answer,
        translations
    )

    if is_correct:
        update_user_word_setting(user_word_setting)
        if user_word_setting.is_hidden:
            inform_user_of_word_change(
                message, 'learned_word', correct_answer
                )

    session.add(user_word_setting)
    session.commit()

    bot.send_message(
        message.chat.id,
        'Продолжим?',
        reply_markup=types.ReplyKeyboardRemove()
    )
    show_interaction_menu(
        message,
        CHATBOT_BTNS,
        ['next', 'add_word', 'delete_word']
        )


def get_feedback_message(
        is_correct: bool, correct_answer: str, translations: list
) -> str:
    """Returns a feedback message based on whether the answer is correct."""
    if is_correct:
        return (f'Правильно!\nСлово 🇺🇸 {correct_answer} переводится как '
                f'🇷🇺 {translations[0].translation}')
    else:
        return f'Неправильно.\nПравильный ответ: 🇺🇸 {correct_answer}'


def send_feedback_message(
        user_message: types.Message,
        is_answer_correct: bool,
        correct_answer_text: str,
        translations_list: list
) -> None:
    """Sends a feedback message to the user based on their answer."""
    feedback_text: str = get_feedback_message(
        is_answer_correct,
        correct_answer_text,
        translations_list
    )
    result_icon: str = '✅' if is_answer_correct else '❌'
    bot.send_message(user_message.chat.id, result_icon)
    bot.send_message(user_message.chat.id, feedback_text)


def should_hide_word(
        user_word_setting: UserWordSetting, correct_answers: int
) -> bool:
    """Checks if a word should be hidden from the user.

    Determines whether a word should be hidden from the user based on
    its status and the user's preferences.

    Returns:
        bool: True if the word should be hidden, False otherwise.
    """
    return user_word_setting.correct_answers >= correct_answers


def update_user_word_setting(user_word_setting: UserWordSetting) -> None:
    """Updates the user's word settings based on their effectiveness."""
    user_word_setting.correct_answers += 1
    user_word_setting.last_shown_at = datetime.now()
    user_word_setting.is_hidden = should_hide_word(
        user_word_setting,
        CHATBOT_DATA['correct_answers']
    )