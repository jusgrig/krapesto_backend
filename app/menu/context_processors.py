"""
Context processor for user menu interface.
Provides language preference to all templates.
"""
def user_menu_language(request):
    """Get current language preference from session, default to 'en'."""
    if hasattr(request, 'session'):
        language = request.session.get('user_menu_language', 'en')
    else:
        language = 'en'
    return {
        'user_menu_language': language,
        'is_lt': language == 'lt',
        'is_en': language == 'en',
    }


