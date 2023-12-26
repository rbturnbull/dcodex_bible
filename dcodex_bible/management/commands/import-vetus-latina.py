from django.core.management.base import BaseCommand, CommandError
from dcodex_bible.models import BibleManuscript


class Command(BaseCommand):
    help = "Imports transcriptions for a Vetus Latin witness from the Birmingham TEI repository."

    def add_arguments(self, parser):
        parser.add_argument(
            "siglum", type=str, help="The siglum of this witness."
        )

    def handle(self, *args, **options):
        BibleManuscript.create_from_vetus_latina(options["siglum"])
