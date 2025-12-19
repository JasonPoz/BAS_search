from django.contrib import admin
from .models import DroneTerm, Language, SearchHistory, Favorite


@admin.register(DroneTerm)
class DroneTermAdmin(admin.ModelAdmin):
    list_display = ('term_eng', 'term_rus', 'abbr_eng', 'abbr_rus', 'category')
    search_fields = ('term_eng', 'term_rus', 'abbr_eng', 'abbr_rus', 'definition_eng', 'definition_rus')
    list_filter = ('category', 'language')
    ordering = ('term_eng',)
    list_per_page = 20


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'term', 'searched_at')
    search_fields = ('query',)
    list_filter = ('searched_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'term', 'added_at')
    list_filter = ('added_at',)
