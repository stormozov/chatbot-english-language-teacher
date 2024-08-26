from pprint import pprint

from sqlalchemy.exc import DatabaseError

from modules.fs_tools.read_file import read_file
from modules.db.models import Word


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
    words = extract_words_from_json(data)
    existing_word_words = get_existing_words(session, words)
    words = filter_out_existing_words(words, existing_word_words)
    import_words_to_db(session, words)


def extract_words_from_json(data: dict) -> list[Word]:
    """Extracts words from the JSON data and returns a list of Word objects."""
    return [
        Word(word=word_data['word'], translation=word_data['translation'])
        for category_content in data['categories'].values()
        for word_data in category_content
    ]


def get_existing_words(session, words: list[Word]) -> list[str]:
    """Returns a list of words that already exist in the database. """
    existing_word_words = (
        session
        .query(Word.word)
        .filter(Word.word.in_([word.word for word in words]))
        .all()
    )
    return [word[0] for word in existing_word_words]


def filter_out_existing_words(
        words: list[Word], existing_word_words: list[str]
) -> list[Word]:
    """Filters out words that already exist in the database."""
    return [word for word in words if word.word not in existing_word_words]


def import_words_to_db(session, words: list[Word]) -> None:
    """Imports words into the database using the provided session."""
    session.add_all(words)
    try:
        session.commit()
    except DatabaseError as e:
        session.rollback()
        raise e
