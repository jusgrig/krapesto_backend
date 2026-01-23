"""
URL configuration for user menu interface.
"""
from django.urls import path
from . import user_views

app_name = 'user_menu'

urlpatterns = [
    # Language switching
    path('set-language/<str:language>/', user_views.set_language, name='set_language'),
    
    # Dashboard
    path('', user_views.user_menu_dashboard, name='dashboard'),
    
    # Dishes
    path('dishes/', user_views.dish_list, name='dish_list'),
    path('dishes/create/', user_views.dish_create, name='dish_create'),
    path('dishes/<int:pk>/edit/', user_views.dish_edit, name='dish_edit'),
    path('dishes/<int:pk>/delete/', user_views.dish_delete, name='dish_delete'),
    
    # Daily Menus
    path('menus/', user_views.daily_menu_list, name='daily_menu_list'),
    path('menus/create/', user_views.daily_menu_create, name='daily_menu_create'),
    path('menus/<int:pk>/edit/', user_views.daily_menu_edit, name='daily_menu_edit'),
    path('menus/<int:pk>/preview/', user_views.daily_menu_preview, name='daily_menu_preview'),
    
    # Categories
    path('categories/', user_views.category_list, name='category_list'),
    path('categories/create/', user_views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', user_views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', user_views.category_delete, name='category_delete'),
    
    # Complexes
    path('complexes/', user_views.complex_list, name='complex_list'),
    path('complexes/create/', user_views.complex_create, name='complex_create'),
    path('complexes/<int:pk>/edit/', user_views.complex_edit, name='complex_edit'),
    path('complexes/<int:pk>/delete/', user_views.complex_delete, name='complex_delete'),
    path('complexes/<int:pk>/update-options/', user_views.complex_update_dish_options, name='complex_update_dish_options'),
    path('complexes/<int:complex_pk>/dishes/', user_views.complex_dish_list, name='complex_dish_list'),
    path('complexes/<int:complex_pk>/dishes/create/', user_views.complex_dish_create, name='complex_dish_create'),
    path('complexes/dishes/<int:pk>/delete/', user_views.complex_dish_delete, name='complex_dish_delete'),
    
    # API endpoints
    path('api/subcategories/', user_views.get_subcategories, name='get_subcategories'),
]

