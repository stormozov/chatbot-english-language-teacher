import random
from telebot import types
from modules.db.models import Word


def generate_answer_options(word_list: list, target_word: Word) -> list:
    """Generate answer options for a quiz based on the user's text input."""
    other_words: list[str] = [
        option.word
        for option in word_list
        if option.word != target_word.word
    ]
    answer_options: list[str] = random.sample(
        other_words, min(3, len(other_words))
    )
    answer_options.insert(
        random.randint(0, len(answer_options)),
        target_word.word
    )

    return answer_options


def create_keyboard_markup(answer_options: list) -> types.ReplyKeyboardMarkup:
    """Create a keyboard markup for the quiz."""
    keyboard_markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True
    )
    options_markup = [types.KeyboardButton(option) for option in answer_options]
    keyboard_markup.add(*options_markup)

    return keyboard_markup


def show_word_variant_menu(word_list: list, target_word: Word) \
        -> types.ReplyKeyboardMarkup:
    """Generate answer choices for a quiz based on the user's text input."""
    answer_options = generate_answer_options(word_list, target_word)
    keyboard_markup = create_keyboard_markup(answer_options)

    return keyboard_markup
