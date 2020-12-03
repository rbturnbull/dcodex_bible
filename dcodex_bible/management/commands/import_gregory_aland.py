from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import dcodex_bible
from dcodex_bible.models import BibleManuscript

class Command(BaseCommand):
    help = "Imports transcriptions for a Greek New Testament witness from the Birmingham TEI repository."

    def add_arguments(self, parser):
        parser.add_argument('gregory_aland', type=str, help="The Gregory-Aland number for this witness.")

    def handle(self, *args, **options):
        BibleManuscript.create_from_gregory_aland(options['gregory_aland'])