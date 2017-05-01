from django.contrib import admin
from .models import Document,WebSiteCrawler,Inverted_Index_Element,Term,BiGramTerm,DistencitTerm,SoundexTerm
# Register your models here.
admin.site.register(Document)
admin.site.register(WebSiteCrawler)
admin.site.register(Inverted_Index_Element)
admin.site.register(Term)

admin.site.register(BiGramTerm)
admin.site.register(SoundexTerm)
admin.site.register(DistencitTerm)
