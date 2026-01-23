"""
Django admin configuration for menu models.

NOTE: Menu models are NOT registered in the main admin site.
They are managed through the custom user menu interface at /user-menu/
Only Users and Groups are available in the main admin panel.
"""
from django.contrib import admin
from .models import Category, Dish, DailyMenu, DailyMenuDish

# Menu models are NOT registered here - they are managed via the user menu interface
# This ensures admin (superuser) can only manage Users and Groups
# Regular users manage dishes and menus through /user-menu/

