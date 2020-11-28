from django import template
from django.utils.safestring import mark_safe
import logging

register = template.Library()

@register.filter
def latex_body(manuscript):
    tex  = "\n"

    prev_book = None
    prev_chapter = None
    in_chapter = False
    rtl = False

    for transcription in manuscript.transcriptions():
        verse_text = transcription.latex()

        if transcription.verse.book != prev_book:
            if in_chapter:
                tex += "\n\\end{biblechapter}\n"
                in_chapter = False
            if rtl:
                tex += "\\unsetRL\n"
                rtl = False
                
            tex += "\\book{%s}\n" % transcription.verse.book_name( abbreviation=False )
            prev_book = transcription.verse.book
            prev_chapter = None

        if transcription.verse.chapter != prev_chapter:
            if in_chapter:
                tex += "\n\\end{biblechapter}\n"
            if not rtl and manuscript.is_rtl():
                tex += "\\setRL\n"
                rtl = True
            
            tex += "\\begin{biblechapter}[%d]\n" % transcription.verse.chapter
            prev_chapter = transcription.verse.chapter
            in_chapter = True

        verse_number = transcription.verse.verse
        footnote = ""
        tex += "\\verse[%d] %s%s\n" % (verse_number, footnote, verse_text)

    if in_chapter:
        tex += "\n\\end{biblechapter}\n"
    return mark_safe( tex )