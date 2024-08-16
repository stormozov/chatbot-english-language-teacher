import random
from telebot import types
from modules.db.models import Word


def show_word_variant_menu(
        word_list: list, target_word: Word
) -> types.ReplyKeyboardMarkup:
    """Generate answer choices for a quiz based on the user's text input.

    Parameters:
        word_list (list): A list of Word objects.
        target_word (Word): The target word to generate answer choices for.

    Returns:
        tuple: A tuple containing the keyboard markup and the ID of the word.
    """
    # Generate answer options
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

    # Create the keyboard layout
    keyboard_markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True
    )
    options_markup = [types.KeyboardButton(option) for option in answer_options]
    keyboard_markup.add(*options_markup)

    return keyboard_markup
