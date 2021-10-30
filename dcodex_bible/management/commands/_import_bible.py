from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import dcodex_bible
from dcodex_bible.models import BibleManuscript


class ImportBibleCommand(BaseCommand):
    siglum = ""
    name = ""
    filename = ""

    def get_siglum(self):
        assert self.siglum
        return self.siglum

    def get_name(self):
        assert self.name
        return self.name

    def get_filename(self):
        assert self.filename
        return self.filename

    def handle(self, *args, **options):
        dcodex_bible_path = Path(dcodex_bible.__file__).parents[0]
        path = dcodex_bible_path / "data" / self.get_filename()

        # Check to see if already present
        ms = BibleManuscript.objects.filter(siglum=self.siglum).first()
        if ms:
            print(f"You already have a manuscript with siglum {self.siglum}.")
            choice = input(f"Do you wish to overwrite it with {self.name}? (y/N) ")
            if choice.lower() != "y":
                return

        BibleManuscript.create_from_csv(
            siglum=self.get_siglum(), name=self.get_name(), filename=path
        )
