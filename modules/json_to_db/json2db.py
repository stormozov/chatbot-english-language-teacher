from .read_json_file import read_json_file
from ..db.models import Category, Word, TranslatedWord


def import_json_data_to_db(session, path: str) -> None:
    """Upload data from a JSON file to the database"""
    data = read_json_file(path)

    # Create dictionaries to keep track of existing objects
    categories = {category.title: category for category in session.query(Category).all()}
    words = {word.word: word for word in session.query(Word).all()}
    translations = {(word.word, translation.translation): translation
                    for word, translation in session.query(Word, TranslatedWord).join(TranslatedWord).all()}

    try:
        for category_title, category_content in data['categories'].items():
            category = categories.get(category_title)

            if category is None:
                category = Category(title=category_title)
                categories[category_title] = category
                session.add(category)  # Add the category to the session
            else:
                # Merge the existing category with the new one
                category.title = category_title

            for word_data in category_content['words']:
                word = words.get(word_data['word'])

                if word is None:
                    word = Word(word=word_data['word'], category=category)
                    words[word_data['word']] = word
                    session.add(word)  # Add the word to the session
                else:
                    # Merge the existing word with the new one
                    word.word = word_data['word']
                    word.category = category

                translation_key = (word_data['word'], word_data['translation'])
                translation = translations.get(translation_key)

                if translation is None:
                    translation = TranslatedWord(translation=word_data['translation'], word=word)
                    translations[translation_key] = translation
                    session.add(translation)  # Add the translation to the session
                else:
                    # Merge the existing translation with the new one
                    translation.translation = word_data['translation']
                    translation.word = word

        session.commit()

    except Exception as e:
        # Roll back the changes if something goes wrong
        session.rollback()
        raise e
