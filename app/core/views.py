from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MenuItem

# Create your views here.

def user_menu(request):
    """
    Dashboard view for menu management - renders HTML for browsers, JSON for API requests
    """
    menu_items = MenuItem.objects.all()
    active_dishes_count = menu_items.count()
    
    # Check if this is an API request (Accept header contains application/json)
    if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
        # Return JSON for API requests
        data = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': str(item.price),
                'category': item.category,
            }
            for item in menu_items
        ]
        return JsonResponse(data, safe=False)
    
    # Return HTML dashboard for browser requests
    context = {
        'menu_items': menu_items,
        'active_dishes_count': active_dishes_count,
    }
    return render(request, 'core/dashboard.html', context)
