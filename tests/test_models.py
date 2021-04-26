from django.test import TestCase

from dcodex_bible.models import *

def make_verse( book_name, chapter, verse ):
    rank = BibleVerse.objects.all().count()+1
    verse, _ = BibleVerse.objects.update_or_create( book=book_names.index(book_name), chapter=chapter, verse=verse, defaults=dict(rank=rank) )
    return verse


class BibleVerseTests(TestCase):
    def setUp(self):
        self.romans1_1 = make_verse('Romans', chapter=1, verse=1 )
        self.first_corinthians1_17 = make_verse('1 Corinthians', chapter=1, verse=17 )
        
        self.first_corinthians2_passage = []
        for verse in range(9,20):
            self.first_corinthians2_passage.append(make_verse('1 Corinthians', chapter=2, verse=verse ))
            
        self.second_corinthians10_15 = make_verse('2 Corinthians', chapter=10, verse=15 )
        self.third_john1_1 = make_verse('3 John', chapter=1, verse=1 )

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
        self.assertEqual( (46,2,9), components_from_verse_ref("1 Co 2:9"))

    def test_get_verses_from_string(self):
        self.assertEqual( [self.first_corinthians1_17.id], [x.id for x in BibleVerse.get_verses_from_string("1 Corinthians 1:17")])
        self.assertEqual( [self.first_corinthians1_17.id]+[x.id for x in self.first_corinthians2_passage], [x.id for x in BibleVerse.get_verses_from_string("1 Co 1:17; 2:9–19")])


