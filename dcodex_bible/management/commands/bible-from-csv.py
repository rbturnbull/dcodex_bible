from django.core.management.base import BaseCommand, CommandError
from dcodex_bible.models import BibleManuscript


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csv", type=str, help="The CSV file to import.")
        parser.add_argument(
            "siglum", type=str, help="The siglum of the manuscript to import."
        )
        parser.add_argument(
            "--name",
            type=str,
            help="The verbose name of the manuscript to import (optional).",
            default="",
        )
        parser.add_argument(
            "--verse-column",
            type=str,
            help="The name column to get the verse references (default: 'Verse').",
            default="Verse",
        )
        parser.add_argument(
            "--transcription-column",
            type=str,
            help="The name column to get the transcriptions (default: 'Transcription').",
            default="Transcription",
        )

    def handle(self, *args, **options):
        BibleManuscript.create_from_csv(
            siglum=options["siglum"],
            name=options["name"],
            filename=options["csv"],
            verse_column=options["verse_column"],
            transcription_column=options["transcription_column"],
        )
