from ._import_bible import ImportBibleCommand


class Command(ImportBibleCommand):
    filename = "SBLGNT.csv"
    name = "SBL Greek New Testament"
    siglum = "SBLGNT"
