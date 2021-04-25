from django.test import TestCase

from dcodex_bible.models import *

class BibleVerseTests(TestCase):
    def setUp(self):
        self.romans1_1, _ = BibleVerse.objects.update_or_create( book=book_names.index('Romans'), chapter=1, verse=1, rank=1 )
        self.first_corinthians1_17, _ = BibleVerse.objects.update_or_create( book=book_names.index('1 Corinthians'), chapter=1, verse=17, rank=2 )
        self.second_corinthians10_15, _ = BibleVerse.objects.update_or_create( book=book_names.index('2 Corinthians'), chapter=10, verse=15, rank=3 )
        self.third_john1_1, _ = BibleVerse.objects.update_or_create( book=book_names.index('3 John'), chapter=1, verse=1, rank=4 )

    def test_get_from_string(self):
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Romans 1:1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Ro 1:1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Ro1_1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "ro1-1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Rom1.1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Romans 1" ).id )
        self.assertEqual( self.romans1_1.id, BibleVerse.get_from_string( "Ro" ).id )

        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2 Corinthians 10:15" ).id )
        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2 Cor 10:15" ).id )
        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2Cor10:15" ).id )
        self.assertEqual( self.second_corinthians10_15.id, BibleVerse.get_from_string( "2Corinth10-15" ).id )

        self.assertEqual( self.third_john1_1.id, BibleVerse.get_from_string( "3Jn1:1" ).id )

    def test_components_from_verse_ref(self):
        self.assertEqual( (46,1,17), components_from_verse_ref("1 Corinthians 1:17"))

    def test_get_verses_from_string(self):
        self.assertEqual( [2], [x.id for x in BibleVerse.get_verses_from_string("1 Corinthians 1:17")])


