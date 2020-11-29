from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from dcodex.admin import ManuscriptChildAdmin
from .models import *


@admin.register(BibleVerse)  
class BibleVerseAdmin(admin.ModelAdmin):
    search_fields = ['chapter', 'verse']


@admin.register(BibleManuscript)
class BibleManuscriptAdmin(ManuscriptChildAdmin):
    base_model = BibleManuscript  # Explicitly set here!
