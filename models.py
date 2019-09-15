from django.db import models
from django.db.models import Max, Min
from dcodex.models import Manuscript, Verse, VerseTranscriptionBase
import re
import logging

class BibleManuscript(Manuscript):
    @classmethod
    def verse_class(cls):
        return BibleVerse
    def verse_search_template(self):
        return "dcodex_bible/verse_search.html"
    def location_popup_template(self):
        return 'dcodex_bible/location_popup.html'

class BibleVerse(Verse):
    book = models.IntegerField()
    chapter = models.IntegerField()
    verse = models.IntegerField()
    word_count = models.IntegerField()
    char_count = models.IntegerField()
    char_aggregate = models.IntegerField(default=0)
    word_aggregate = models.IntegerField(default=0)
    
    book_names = [None, "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation" ]
    book_abbreviations = [None, "Gen", "Ex", "Lev", "Nu", "Deut", "Josh", "Jdg", "Ru", "1Sa", "2Sa", "1Ki", "2Ki", "1Chr", "2Chr", "Ez", "Neh", "Est", "Job", "Ps", "Pr", "Ecc", "Song", "Isa", "Jer", "Lam", "Ez", "Da", "Ho", "Jl", "Am", "Ob", "Jon", "Mic", "Nah", "Hab", "Zep", "Hag", "Zec", "Mal", "Mt", "Mk", "Lk", "Jn", "Acts", "Ro", "1Co", "2Co", "Ga", "Eph", "Ph", "Col", "1Th", "2Th", "1Tim", "2Tim", "Titus", "Phil", "Heb", "Jas", "1Pe", "2Pe", "1Jn", "2Jn", "3Jn", "Jud", "Rev"]

    # Override
    def cumulative_mass(self):
        return self.char_aggregate

    # Override
    @classmethod
    def get_from_dict( cls, dictionary ):
        return cls.get_from_values(
            dictionary.get('book_id', 1), 
            dictionary.get('chapter', 1), 
            dictionary.get('verse', 1) )

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
        if name in cls.book_names:
            return cls.book_names.index( name )
        if name in cls.book_abbreviations:
            return cls.book_abbreviations.index( name )


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
            names = self.book_abbreviations
        else:
            names = self.book_names
        
        if self.book < len(names):
            return names[self.book]
        return None
    def reference(self, abbreviation = False, end_verse=None):
        if end_verse != None:
            return "%s–%s" % (self.reference( abbreviation=abbreviation ), end_verse.reference( abbreviation=abbreviation ) ) # TODO
    
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
            