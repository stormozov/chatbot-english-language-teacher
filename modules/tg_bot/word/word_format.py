import re


def check_word_format(
        english_pattern: str, russian_pattern: str,
        input_word: str, input_translation: str
) -> bool:
    """Check if the input word and its translation match the given patterns"""
    eng_regex, rus_regex = create_regex_patterns(
        english_pattern, russian_pattern
    )
    return is_valid_word(
        input_word, input_translation,
        eng_regex, rus_regex
    )


def create_regex_patterns(english_pattern: str, russian_pattern: str) \
        -> tuple[re.Pattern, re.Pattern]:
    """Create regular expressions for English and Russian languages"""
    eng_regex = re.compile(r'^' + english_pattern + '$')
    rus_regex = re.compile(r'^' + russian_pattern + '$')
    return eng_regex, rus_regex


def is_valid_word(
        input_word: str, input_translation: str,
        eng_regex: re.Pattern, rus_regex: re.Pattern
) -> bool:
    """Check if the input word and its translation match the given patterns"""
    return bool(
        eng_regex.match(input_word) and rus_regex.match(input_translation)
    )
