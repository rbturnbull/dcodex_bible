from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models import *


@admin.register(BibleVerse)  
class BibleVerseAdmin(admin.ModelAdmin):
    search_fields = ['chapter', 'verse']


admin.site.register(BibleManuscript)