from django.db import models
from django.db.models import Max, Min
from dcodex.models import Manuscript, Verse, VerseTranscriptionBase
import re
import logging

book_names = [None, "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation" ]
book_abbreviations = [None, "Gen", "Ex", "Lev", "Nu", "Deut", "Josh", "Jdg", "Ru", "1Sa", "2Sa", "1Ki", "2Ki", "1Chr", "2Chr", "Ez", "Neh", "Est", "Job", "Ps", "Pr", "Ecc", "Song", "Isa", "Jer", "Lam", "Ez", "Da", "Ho", "Jl", "Am", "Ob", "Jon", "Mic", "Nah", "Hab", "Zep", "Hag", "Zec", "Mal", "Mt", "Mk", "Lk", "Jn", "Acts", "Ro", "1Co", "2Co", "Ga", "Eph", "Ph", "Col", "1Th", "2Th", "1Tim", "2Tim", "Titus", "Phil", "Heb", "Jas", "1Pe", "2Pe", "1Jn", "2Jn", "3Jn", "Jud", "Rev"]

def get_book_id(name):
    if name in book_names:
        return book_names.index( name )
    if name in book_abbreviations:
        return book_abbreviations.index( name )
    return None


def read_int( string ):
    return int(re.sub("[^0-9]", "", string))

def components_from_verse_ref( verse_ref ):
    verse_ref = verse_ref.strip()
    
    # Get Verse From End
    components = verse_ref.split(":")
    if len(components) == 1:
        return None, None, read_int(verse_ref)
    
    verse = read_int( components[1])
    
    matches = re.match( "(.*?)\s*(\d+)", components[0] )
    if matches:
        book_name = matches.group(1)
        if len(book_name) == 0:
            book_id = None
        else:
            book_id = get_book_id( book_name )
        chapter = read_int(matches.group(2))

        return book_id, chapter, verse
    
    raise Exception('Cannot interpret verse %s' % (verse_ref))
    

class BibleManuscript(Manuscript):
    @classmethod
    def verse_class(cls):
        return BibleVerse
    def verse_search_template(self):
        return "dcodex_bible/verse_search.html"
    def location_popup_template(self):
        return 'dcodex_bible/location_popup.html'

    def verse_from_mass_difference( self, reference_verse, additional_mass ):
        return self.verse_class().verse_from_mass( reference_verse.cumulative_mass() + additional_mass )

class BibleVerse(Verse):
    book = models.IntegerField()
    chapter = models.IntegerField()
    verse = models.IntegerField()
    word_count = models.IntegerField(default=0)
    char_count = models.IntegerField(default=0)
    char_aggregate = models.IntegerField(default=0)
    word_aggregate = models.IntegerField(default=0)
    
    @classmethod
    def book_names( cls ):
        return book_names
    @classmethod
    def book_abbreviations( cls ):
        return book_abbreviations

    @classmethod
    def verse_from_mass( cls, mass ):
        return cls.objects.filter( char_aggregate__lte=mass ).order_by('-char_aggregate').first()

    # Override
    def cumulative_mass(self):
        return self.char_aggregate

    # Override
    @classmethod
    def get_from_dict( cls, dictionary ):
        """
        This function expects a dictionary with the keys 'book_id', 'chapter', and 'verse' and uses these values to find the corresponding Bible verse.
        """
    
        return cls.get_from_values(
            dictionary.get('book_id', 1), 
            dictionary.get('chapter', 1), 
            dictionary.get('verse', 1) )

    # Override
    def tei_id( self ):
        """ 
        Method to get an id that can be used to reference this verse in TEI.

        Verses are encpasulated in a <ab> tag.
        The id returned by this function is given as the n attribute in this tag.
        e.g. <ab n='B04K1V35'>...

        By default, this is the string representation of this verse.
        """
        if self.book < 40:
            prefix = "A%02d" % self.book # Is this correct?
        else:
            prefix = "B%02d" % (self.book-39)

        return f"{prefix}K{self.chapter}V{self.verse}"

    @classmethod
    def get_verses_from_string( cls, passage_string ):
        """ 
        Returns a list of Bible Verse objects by interpreting the passages_string.
        
        The passages_string can has multiple references separated with a semi-colon.
        e.g. 
        'Mt 1:1–18'
        'John 1:1–21:25'
        'Lk 24:1-10; Mk 16:1–8'        
        """
        book = None
        chapter = None
        
        verses = []
        
        passage_string = passage_string.replace( "-", "–" )
        
        passages_between_semis = passage_string.split(";")
        for passage_between_semis in passages_between_semis:
            passages_between_commas = passage_between_semis.split(",")
            for passage_between_commas in passages_between_commas:
                verse_ends = passage_between_commas.split("–")
                if len(verse_ends) > 2:
                    raise Exception('Cannot interpret %s in passage %s' % (passage_between_commas, passage_string))
                start_verse_ref = verse_ends[0].strip()
                end_verse_ref = verse_ends[1].strip() if len(verse_ends) > 1 else start_verse_ref
                
                start_verse_book_id, start_verse_chapter, start_verse_verse = components_from_verse_ref( start_verse_ref )
                if start_verse_book_id is None:
                    start_verse_book_id = book
                if start_verse_chapter is None:
                    start_verse_chapter = chapter

                start_verse = cls.get_from_values( start_verse_book_id, start_verse_chapter, start_verse_verse )
                
                end_verse_book_id, end_verse_chapter, end_verse_verse = components_from_verse_ref( end_verse_ref )                
                
                if end_verse_book_id is None:
                    end_verse_book_id = start_verse_book_id
                if end_verse_chapter is None:
                    end_verse_chapter = start_verse_chapter
                
#                print('xx', end_verse_book_id, end_verse_chapter, end_verse_verse)
                
                end_verse = cls.get_from_values( end_verse_book_id, end_verse_chapter, end_verse_verse )
                
                verses += cls.objects.filter( rank__gte=start_verse.rank, rank__lte=end_verse.rank ).all()
                
                book = end_verse_book_id
                chapter = end_verse_chapter
                                    
        return verses


    # Override
    @classmethod
    def get_from_string( cls, verse_as_string ):
        matches = re.match( "([a-zA-Z]+)\s*(\d*)[-:]*(\d*)", verse_as_string )
        if matches:
            book_name = matches.group(1)
            book = BibleVerse.book_id( book_name )
            
            chapter = matches.group(2)
            if not chapter or len(chapter) == 0:
                chapter = 1
            
            verse = matches.group(3)            
            if not verse or len(verse) == 0:
                verse = 1
                
            return cls.get_from_values(book, chapter, verse)
        else:
            return None
    
    @classmethod
    def book_id( cls, name ):
        return get_book_id( name )

    @classmethod
    def get_from_values( cls, book, chapter, verse ):
        max_chapters = cls.chapters_in_book(book)
        chapter = min( int(chapter), max_chapters )
        max_verses = cls.verses_in_chapter(book, chapter)
        verse = min( int(verse), max_verses )
                                
        return cls.objects.get( book=book, chapter=chapter, verse=verse)
    
    @classmethod
    def chapters_in_book( cls, book ):
        try:
            return cls.objects.filter(book=book).aggregate( Max('chapter') )['chapter__max']
        except:
            return 1

    @classmethod
    def verses_in_chapter( cls, book, chapter ):
        try:
            return cls.objects.filter(book=book, chapter=chapter).aggregate( Max('verse') )['verse__max']
        except:
            return 1
    
    def book_name(self, abbreviation = False):
        if abbreviation:
            names = book_abbreviations
        else:
            names = book_names
        
        if self.book < len(names):
            return names[self.book]
        return None

    def reference(self, abbreviation = False, end_verse=None):
        if end_verse != None:
            if self.book == end_verse.book:
                if self.chapter == end_verse.chapter:
                    return "%s–%d" % (self.reference( abbreviation=abbreviation ), end_verse.verse )
                return "%s–%d:%d" % (self.reference( abbreviation=abbreviation ), end_verse.chapter, end_verse.verse )
            return "%s–%s" % (self.reference( abbreviation=abbreviation ), end_verse.reference( abbreviation=abbreviation ) )
    
        book_name = self.book_name(abbreviation)
        return "%s %d:%d" % (book_name, self.chapter, self.verse)



        
        
class RubricTranscription(VerseTranscriptionBase):
    BEFORE = 'B'
    MIDDLE = 'M'
    AFTER  = 'A'
    LOCATION_CHOICES = [
        (BEFORE, 'Before'),
        (MIDDLE, 'Middle'),
        (AFTER, 'After'),
    ]
    location = models.CharField(
        max_length=1,
        choices=LOCATION_CHOICES,
        default=BEFORE,
    )
        
    def __str__(self):
        return "%s %s" % (self.get_location_display(), super(RubricTranscription, self).__str__() )
            