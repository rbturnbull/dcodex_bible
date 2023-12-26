from ._import_bible import ImportBibleCommand


class Command(ImportBibleCommand):
    filename = "TR.csv"
    name = "Textus Receptus (Elzevir)"
    siglum = "TR"
