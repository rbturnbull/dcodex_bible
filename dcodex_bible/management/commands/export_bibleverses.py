from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import dcodex_bible
from dcodex_bible.models import BibleVerse

class Command(BaseCommand):

    def handle(self, *args, **options):
        attribute_names = [
            'rank',
            'book',
            'chapter',
            'verse',
            'word_count',
            'char_count',
            'char_aggregate',
            'word_aggregate',
        ]
        print(','.join(attribute_names))
        for verse in BibleVerse.objects.all():
            verse_attributes = [str(getattr( verse, attribute_name )) for attribute_name in attribute_names]
            print(','.join(verse_attributes))
    
