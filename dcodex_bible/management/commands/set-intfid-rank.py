from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from dcodex_bible.models import BibleManuscript


class Command(BaseCommand):
    def handle(self, *args, **options):
        for ms in BibleManuscript.objects.all():
            ms.set_rank_from_intf_id()
            print(ms, ms.rank)

        for rank, ms in enumerate(BibleManuscript.objects.all(), 1):
            ms.rank = rank
            ms.save(update_fields=['rank'])
