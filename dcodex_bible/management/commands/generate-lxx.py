from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from pathlib import Path
# import pandas as pd
import csv
import dcodex_bible
from dcodex_bible.models import BibleManuscript, BibleVerse


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "swete", type=str, help="The location of the clone of the https://github.com/jtauber/lxx-swete repository."
        )

    def handle(self, *args, **options):
        swete = Path(options['swete'])
        ms, _ = BibleManuscript.objects.update_or_create(name="Swete LXX", siglum="Swete")
        books = {
            '1 Esdras': '15.1Es.txt',
            'Wisdom of Solomon': '23.Wis.txt',
            'Sirach Prologue': '24.Sip.txt',
            'Sirach': '25.Sir.txt',
            'Judith': '27.Jdt.txt',
            'Tobit': '29.Tbs.txt',
            'Baruch': '44.Bar.txt',
            'Epistle of Jeremiah': '46.Epj.txt',
            'Susanna': '50.Sus.txt',
            'Bel and the Dragon': '52.Bel.txt',
            '1 Maccabees': '54.1Ma.txt',
            '2 Maccabees': '55.2Ma.txt',
            '3 Maccabees': '56.3Ma.txt',
            '4 Maccabees': '57.4Ma.txt',
            'Psalms of Solomon': '58.Pss.txt',
            '1 Enoch': '59.1En.txt',
            'Odes': '60.Ode.txt',

        }
        prev_verse = BibleVerse.get_from_string("Rev 22:21")
        rank = 1 + prev_verse.rank
        char_aggregate = prev_verse.char_aggregate + prev_verse.char_count
        word_aggregate = prev_verse.word_aggregate + prev_verse.word_count

        book_names = BibleVerse.book_names()
        for book, file in books.items():
            print(book)
            book_id = book_names.index(book)
            prev_verse = None
            words = []
            with open(swete/file) as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in reader:
                    verse, word = int(row[0]), row[1]
                    if verse != prev_verse and prev_verse is not None:
                        # Make verse
                        chapter = (prev_verse // 1000) % 1000
                        verse_number = prev_verse % 1000
                        text = " ".join(words)

                        verse_obj, _ = BibleVerse.objects.update_or_create(
                            book=book_id,
                            chapter=chapter,
                            verse=verse_number,
                            defaults=dict(
                                rank=rank,
                                char_aggregate=char_aggregate,
                                word_aggregate=word_aggregate,
                                char_count=len(text),
                                word_count=len(words),
                            )
                        )
                        rank += 1
                        char_aggregate = verse_obj.char_aggregate + verse_obj.char_count
                        word_aggregate = verse_obj.word_aggregate + verse_obj.word_count
                        words = []

                        # Add transcription
                        print(verse_obj, text)
                        ms.save_transcription(verse_obj, text)

                    prev_verse = verse
                    if len(word.strip()):
                        words.append(word)

            text = " ".join(words)
            chapter = (verse // 1000) % 1000
            verse_number = verse % 1000

            verse_obj, _ = BibleVerse.objects.update_or_create(
                book=book_id,
                chapter=chapter,
                verse=verse_number,
                defaults=dict(
                    rank=rank,
                    char_aggregate=char_aggregate,
                    word_aggregate=word_aggregate,
                    char_count=len(text),
                    word_count=len(words),
                )
            )
            rank += 1
            char_aggregate = verse_obj.char_aggregate + verse_obj.char_count
            word_aggregate = verse_obj.word_aggregate + verse_obj.word_count
            words = []
            print(verse_obj, text)
            ms.save_transcription(verse_obj, text)

