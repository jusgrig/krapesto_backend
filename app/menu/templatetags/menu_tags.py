"""
Template tags for menu interface.
"""
from django import template

register = template.Library()


@register.filter
def get_name(obj, language):
    """Get name based on language preference."""
    if language == "lt":
        return getattr(obj, "name_lt", "") or getattr(obj, "name_en", "")
    return getattr(obj, "name_en", "") or getattr(obj, "name_lt", "")


@register.filter
def get_ingredients(obj, language):
    """Get ingredients based on language preference."""
    if language == "lt":
        return getattr(obj, "ingredients_lt", "") or getattr(obj, "ingredients_en", "")
    return getattr(obj, "ingredients_en", "") or getattr(obj, "ingredients_lt", "")


@register.filter
def get_ingredients_strict(obj, language):
    """Get ingredients based on language preference without fallback."""
    if language == "lt":
        return getattr(obj, "ingredients_lt", "") or ""
    return getattr(obj, "ingredients_en", "") or ""
