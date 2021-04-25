from django.db import models
from django.db.models import Max, Min
from dcodex.models import Manuscript, Verse, VerseTranscriptionBase
import re
import logging
import requests
from lxml import etree
from bs4 import BeautifulSoup

book_names = [None, "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation" ]
book_abbreviations = [None, "Gen", "Ex", "Lev", "Nu", "Deut", "Josh", "Jdg", "Ru", "1Sa", "2Sa", "1Ki", "2Ki", "1Chr", "2Chr", "Ez", "Neh", "Est", "Job", "Ps", "Pr", "Ecc", "Song", "Isa", "Jer", "Lam", "Ez", "Da", "Ho", "Jl", "Am", "Ob", "Jon", "Mic", "Nah", "Hab", "Zep", "Hag", "Zec", "Mal", "Mt", "Mk", "Lk", "Jn", "Acts", "Ro", "1Co", "2Co", "Ga", "Eph", "Ph", "Col", "1Th", "2Th", "1Tim", "2Tim", "Titus", "Phil", "Heb", "Jas", "1Pe", "2Pe", "1Jn", "2Jn", "3Jn", "Jud", "Rev"]



def strip_namespace( el ):
	if hasattr(el, 'tag') and '}' in el.tag:
		el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
	for x in el:
		strip_namespace( x )

def get_book_id(name):
    name = name.title()
    if name in book_names:
        return book_names.index( name )
    if name in book_abbreviations:
        return book_abbreviations.index( name )
    
    for index, book_name in enumerate(book_names[1:]):
        if book_name.startswith(name) or book_name.replace(" ", "").startswith(name):
            return index + 1

    book_abbreviations_alternate = {
        "Phlm": "Philemon",
        "1Kgs": "1 Kings",
        "2Kgs": "2 Kings",
    }
    if name in book_abbreviations_alternate:
        return book_names.index(book_abbreviations_alternate[name])

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
    
    matches = re.match( "(\d*\s*[a-zA-Z]+)\s*(\d+)", components[0] )
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

    def latex(self, baseurl=None):
        """ Returns a LaTeX representation of this manuscript as a string. """
        from django.template import loader
        template = loader.get_template('dcodex_bible/latex_manuscript.latex')
        context = dict(manuscript=self, baseurl=baseurl)
        return template.render(context)

    def import_gregory_aland(self, gregory_aland=None):
        gregory_aland = gregory_aland or self.siglum

        self.import_igntp_iohannes(gregory_aland)
        self.import_intf(gregory_aland)
        
    def import_igntp_iohannes(self, gregory_aland=None):
        gregory_aland = gregory_aland or self.siglum
        if self.siglum == None:
            self.siglum = gregory_aland

        m = re.match( r"GA(\d+)", gregory_aland )
        if m:
            gregory_aland = m.group(1)

        url = f"http://www.itseeweb.bham.ac.uk/iohannes/transcriptions/XML/greek/04_{gregory_aland}.xml"

        self.import_intf_tei_url(url)

    def import_intf(self, gregory_aland=None):
        gregory_aland = gregory_aland or self.siglum
        if self.siglum == None:
            self.siglum = gregory_aland

        m = re.match( r"GA(0?\d+)", gregory_aland )
        if m:
            gregory_aland = m.group(1)

        if len(gregory_aland) == 0:
            print(f"Cannot get GA number.")
            return

        # Get INTF ID
        m = re.match(r"P(\d+)", gregory_aland)
        if m:
            intf_id = 10000 + int(m.group(1))
        m = re.match(r"0(\d+)", gregory_aland)
        if m:
            intf_id = 20000 + int(m.group(1))
        elif gregory_aland.isdigit():
            intf_id = 30000 + int(gregory_aland)
        else:
            print(f"Cannot get INTF ID from {gregory_aland}")
            return

        url = f"http://ntvmr.uni-muenster.de/community/vmr/api/transcript/get/?docID={intf_id}&pageID=1-99999&format=teiraw"
        self.import_intf_tei_url(url)

    def import_intf_tei_url(self, url):
        """ Imports from a TEI document in the format of the INTF and Birmingham. """
        response = requests.get(url)
        tree = etree.fromstring(response.content)
        strip_namespace(tree)

        # Find all verses
        verses = tree.findall('.//ab')
        for verse_element in verses: 
            if 'n' not in verse_element.attrib:
                continue

            tei_verse_ID = verse_element.attrib['n']
            verse = self.verse_class().get_from_tei_id(tei_verse_ID)
            if not verse:
                continue
                # raise Exception(f"Cannot find verse {tei_verse_ID}.")
                        
            verse_text = ""
            delim = ""
            for element in verse_element:
                if element.tag == 'pb':
                    delim = ""
                if element.tag == 'w' and 'part' in element.attrib:
                    delim = ""
                    element.attrib.pop('part')
                xml_string = etree.tostring(element, encoding='UTF-8', method='xml').decode('utf-8')
                xml_string = BeautifulSoup(xml_string, "lxml").text # This is a bit of a hack
                
                verse_text = verse_text + delim + xml_string
                delim = " "
            verse_text = verse_text.replace('\n','')	
            verse_text = re.sub(r"\s+", " ", verse_text)
            verse_text = re.sub(r"<w>(.*?)<\/w>", r"\1", verse_text) # I don't think this is necessary now
            
            print(verse, verse_text)
            self.save_transcription( verse, verse_text )    


    @classmethod
    def create_from_gregory_aland(cls, gregory_aland):
        if gregory_aland and gregory_aland[0].isdigit():
            gregory_aland = f"GA{gregory_aland}"

        manuscript, _ = cls.objects.update_or_create( siglum=gregory_aland )
        if manuscript.name is None:
            manuscript.name = gregory_aland
        
        manuscript.import_gregory_aland()
        


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
    def get_from_tei_id( cls, tei_id):
        """ Finds a BibleVerse object from a TEI ID string. """
        m = re.match(r"B(\d*)K(\d*)V(\d*)",	tei_id)
        verse = None
        if m:
            book = int(m.group(1)) + 39 #number of books in OT
            chapter = int(m.group(2))
            verse_num = int(m.group(3))
            print("book, chapter, verse_num", book, chapter, verse_num)
            return cls.get_from_values(book, chapter, verse_num)
        return None

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
        matches = re.match( "(\d*\s*[a-zA-Z]+)[\s\.]*(\d*)[-:\.]*(\d*)", verse_as_string )
        if matches:
            book_name = matches.group(1)
            book = BibleVerse.book_id( book_name )
            if not book:
                raise Exception(f"Cannot find book '{book_name}'. Taken from '{verse_as_string}.'")
            
            chapter = matches.group(2)
            if not chapter or len(chapter) == 0:
                chapter = 1
            
            verse = matches.group(3)            
            if not verse or len(verse) == 0:
                verse = 1
                
            return cls.get_from_values(book, chapter, verse)
        else:
            raise Exception(f"Cannot find verse: '{verse_as_string}'.")
    
    @classmethod
    def book_id( cls, name ):
        return get_book_id( name )

    @classmethod
    def get_from_values( cls, book, chapter, verse ):
        if not book or not chapter or not verse:
            raise Exception("Cannot find verse:", book, chapter, verse)
            
        max_chapters = cls.chapters_in_book(book)
        if not max_chapters:
            raise Exception("Cannot find verse with book id '{book}'. Have you loaded the Bible Verses fixture?")
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
    
    def book_name(self, abbreviation=False):
        if abbreviation:
            names = book_abbreviations
        else:
            names = book_names
        
        if self.book < len(names):
            return names[self.book]
        return None

    def reference(self, abbreviation=False, end_verse=None):
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
            