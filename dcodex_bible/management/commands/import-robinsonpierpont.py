from ._import_bible import ImportBibleCommand


class Command(ImportBibleCommand):
    filename = "RobinsonPierpont.csv"
    name = "Byzantine Text (Robinson-Pierpont)"
    siglum = "Byz"
