from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import dcodex_bible
from dcodex_bible.models import BibleVerse
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        dcodex_bible_path = Path(dcodex_bible.__file__).parents[0]
        path = dcodex_bible_path / "data" / "BibleVerses.csv"

        df = pd.read_csv(path)
        # print(df)
        for index, row in df.iterrows():
            row_dict = row.to_dict()
            book = row_dict.pop("book")
            chapter = row_dict.pop("chapter")
            verse = row_dict.pop("verse")
            BibleVerse.objects.update_or_create(
                book=book, chapter=chapter, verse=verse, defaults=row_dict
            )
