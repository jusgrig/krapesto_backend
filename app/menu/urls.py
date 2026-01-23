"""
URL configuration for menu API endpoints.
"""
from django.urls import path
from .views import TodayLunchMenuView, WeekLunchMenuView, DateLunchMenuView

app_name = 'menu'

urlpatterns = [
    path('lunch-menu/today/', TodayLunchMenuView.as_view(), name='today-menu'),
    path('lunch-menu/week/', WeekLunchMenuView.as_view(), name='week-menu'),
    path('lunch-menu/date/<str:date_str>/', DateLunchMenuView.as_view(), name='date-menu'),
    path('user-menu/menus/<int:pk>/', TodayLunchMenuView.as_view(), name='user-menu-detail'),  # Alias for compatibility
]


