from django.urls import path
from .views import TermSearchView, autocomplete_terms, translate_term, home

app_name = 'dictionary'

urlpatterns = [
    path('', home, name='home'),
    path('search/', TermSearchView.as_view(), name='term_search'),
    path('autocomplete/', autocomplete_terms, name='autocomplete_terms'),
    path('translate/', translate_term, name='translate_term'),
]
