from ._import_bible import ImportBibleCommand


class Command(ImportBibleCommand):
    filename = "WH.csv"
    name = "Westcott and Hort"
    siglum = "WH"
