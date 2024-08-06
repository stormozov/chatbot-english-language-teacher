from .read_json_file import read_json_file
from ..db.models import Category, Word, TranslatedWord


def import_json_data_to_db(session, path: str) -> None:
    """Upload data from a JSON file to the database"""
    data = read_json_file(path)

    for category_title, category_content in data['categories'].items():
        category = session.query(Category).filter_by(title=category_title).first()

        if category is None:
            category = Category(title=category_title)
            session.add(category)

        for word_data in category_content['words']:
            word = session.query(Word).filter_by(word=word_data['word']).first()

            if word is None:
                word = Word(word=word_data['word'], category=category)
                session.add(word)

            translation = session.query(TranslatedWord).filter_by(word=word,
                                                                  translation=word_data['translation']).first()

            if translation is None:
                translation = TranslatedWord(translation=word_data['translation'], word=word)
                session.add(translation)

    session.commit()
