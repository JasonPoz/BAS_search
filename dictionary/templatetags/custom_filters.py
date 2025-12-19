from django import template

register = template.Library()

LANG_NAMES = {
    'en': 'Английский',
    'fr': 'Французский',
    'es': 'Испанский',
    'zh': 'Китайский',
}

@register.filter
def language_name(code):
    return LANG_NAMES.get(code, code)
