from sqlalchemy.exc import DatabaseError

from modules.fs_tools.read_file import read_file
from modules.db.models import Category, Word, TranslatedWord


def get_existing_objects(session) -> tuple[dict, dict, dict]:
    """Retrieves existing objects from the database.

    Args:
        session (Session): The database session.

    Returns:
        tuple: A tuple containing three dictionaries. The first
    dictionary contains existing categories, where the keys are category
    titles and the values are Category objects. The second dictionary
    contains existing all_words, where the keys are word texts and the values
    are Word objects. The third dictionary contains existing
    translations, where the keys are tuples of word texts and translation
    texts, and the values are TranslatedWord objects.
    """
    categories = {
        category.title: category for category in session.query(Category).all()
    }
    all_words = {word.word: word for word in session.query(Word).all()}
    query: list = session.query(Word, TranslatedWord).join(TranslatedWord).all()
    translations = {
        (word.word, translation.translation): translation
        for word, translation in query
    }

    return categories, all_words, translations


def create_or_update_category(
        session, categories: dict, category_title: str
) -> Category:
    """Create or update a category in the database.

    Args:
        session (Session): The database session.
        categories (dict): A dictionary of existing categories.
        category_title (str): The title of the category.

    Returns:
        Category: The created or updated category object.
    """
    category = categories.get(category_title, Category(title=category_title))

    if category not in categories:
        session.add(category)

    return category


def create_or_update_word(
        session, words: dict, word_data: dict, category: Category
) -> Word:
    """Creates or updates a word in the database.

    Args:
        session (Session): The database session.
        words (dict): A dictionary of existing words.
        word_data (dict): The data for the word, containing the word text.
        category (Category): The category the word belongs to.

    Returns:
        Word: The created or updated word object.
    """
    word_text: str = word_data['word']
    word: Word = words.get(word_text) or Word(word=word_text, category=category)
    word.word = word_text
    word.category = category

    if word not in session:
        session.add(word)

    return word


def create_or_update_translation(
        session, translations, word: Word, translation_data: dict
) -> TranslatedWord:
    """Create or update a translation for a given word in the database.

    Args:
        session (Session): The database session.
        translations (dict): A dictionary of existing translations.
        word (Word): The word for which the translation is being created
        or updated.
        translation_data (dict): The data for the translation, containing
        the translation text.

    Returns:
        TranslatedWord: The created or updated translation object.
    """
    translation_key = (word.word, translation_data['translation'])
    translation = translations.get(translation_key)

    if translation is None:
        translation = TranslatedWord(
            translation=translation_data['translation'], word=word
        )
        session.add(translation)
    return translation


def import_json_data_to_db(session, file_path: str) -> None:
    """Imports JSON data from a file into a database using the provided session.

    Args:
        session (Session): The session object used to interact with the database
        file_path (str): The path to the JSON file containing the data
        to be imported

    Returns:
        None: This function does not return anything.

    Raises:
        DatabaseError: If there is an error while importing the data into the
        database
    """
    data: dict = read_file(file_path)
    categories, words, translations = get_existing_objects(session)

    try:
        for category_title, category_content in data['categories'].items():
            category = create_or_update_category(
                session, categories, category_title
            )
            for word_data in category_content['words']:
                word = create_or_update_word(
                    session, words,
                    word_data, category
                )
                create_or_update_translation(
                    session, translations,
                    word, word_data
                )
                # session.add_all([word, translation])

        session.commit()
    except DatabaseError as e:
        session.rollback()
        raise e
