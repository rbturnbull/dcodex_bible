from django.test import TestCase

from dcodex_bible.models import *

class BibleVerseTests(TestCase):
    def setUp(self):
        self.romans1_1, _ = BibleVerse.objects.update_or_create( book=book_names.index('Romans'), chapter=1, verse=1, rank=1 )
        self.second_corinthians10_15, _ = BibleVerse.objects.update_or_create( book=book_names.index('2 Corinthians'), chapter=10, verse=15, rank=2 )

    def test_get_from_string(self):
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Romans 1:1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Ro 1:1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Ro1_1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Rom1.1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Romans 1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Ro" ).id )

        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2 Corinthians 10:15" ).id )
        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2 Cor 10:15" ).id )
        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2Cor10:15" ).id )
        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2Corinth10-15" ).id )




