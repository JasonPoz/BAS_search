from django.urls import path
from .views import (
    TermSearchView,DictionaryView,autocomplete_terms,translate_term,home,
)
from . import views

app_name = 'dictionary'

urlpatterns = [
    path('', home, name='home'),
    path('search/', TermSearchView.as_view(), name='term_search'),
    path('dictionary/', DictionaryView.as_view(), name='dictionary'),
    path('autocomplete/', autocomplete_terms, name='autocomplete_terms'),
    path('translate/', translate_term, name='translate_term'),
    path('history/', views.history_view, name='history'),
]
