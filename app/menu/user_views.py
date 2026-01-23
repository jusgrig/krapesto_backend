"""
User menu interface views for managing dishes and daily menus.
This is the user-facing interface (not admin panel) for menu management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django import forms
from datetime import date, timedelta
from .models import Category, Subcategory, Dish, DailyMenu, DailyMenuDish, DailyMenuComplex, Complex, ComplexDish
from .forms import CategoryForm, SubcategoryForm, DishForm, DailyMenuForm, ComplexForm, ComplexDishForm


def get_user_language(request):
    """Get current language from session, default to 'en'."""
    if hasattr(request, 'session'):
        return request.session.get('user_menu_language', 'en')
    return 'en'


@login_required
def set_language(request, language):
    """Set language preference in session."""
    if language in ['en', 'lt']:
        request.session['user_menu_language'] = language
        messages.success(request, f'Language changed to {language.upper()}')
    else:
        messages.error(request, 'Invalid language selection')
    
    # Redirect back to previous page or dashboard
    referer = request.META.get('HTTP_REFERER', '/user-menu/')
    return redirect(referer)


@login_required
def user_menu_dashboard(request):
    """Main dashboard for user menu management."""
    language = get_user_language(request)
    today = date.today()
    week_start = today
    week_end = today + timedelta(days=6)
    
    # Get menus for the week
    daily_menus = DailyMenu.objects.filter(
        date__gte=week_start,
        date__lte=week_end
    ).order_by('date')
    
    # Get all dishes
    dishes = Dish.objects.filter(active=True).select_related('category').order_by('category__order', 'name_en')
    
    # Get categories
    categories = Category.objects.all().order_by('order')
    
    context = {
        'daily_menus': daily_menus,
        'dishes': dishes,
        'categories': categories,
        'week_start': week_start,
        'week_end': week_end,
        'language': language,
    }
    
    return render(request, 'menu/user_dashboard.html', context)


@login_required
def dish_list(request):
    """List all dishes with filtering by category, name, and status."""
    language = get_user_language(request)
    dishes = Dish.objects.select_related('category').order_by('category__order', 'name_en')
    categories = Category.objects.all().order_by('order')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    selected_category = None
    if category_id:
        try:
            selected_category = Category.objects.get(pk=category_id)
            dishes = dishes.filter(category=selected_category)
        except Category.DoesNotExist:
            pass
    
    # Filter by name (search in both name_lt and name_en)
    search_name = request.GET.get('name', '').strip()
    if search_name:
        dishes = dishes.filter(
            Q(name_lt__icontains=search_name) | Q(name_en__icontains=search_name)
        )
    
    # Filter by status (active/inactive)
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        dishes = dishes.filter(active=True)
    elif status_filter == 'inactive':
        dishes = dishes.filter(active=False)
    # If status_filter is empty or 'all', show all dishes
    
    context = {
        'dishes': dishes,
        'categories': categories,
        'selected_category': selected_category,
        'search_name': search_name,
        'selected_status': status_filter,
        'user_menu_language': language,
    }
    return render(request, 'menu/dish_list.html', context)


@login_required
def dish_create(request):
    """Create a new dish."""
    language = get_user_language(request)
    
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dish created successfully!' if language == 'en' else 'Patiekalas sėkmingai sukurtas!')
            return redirect('user_menu:dish_list')
    else:
        form = DishForm()
    
    # Customize category choices to show names in selected language
    if language == 'lt':
        form.fields['category'].label_from_instance = lambda obj: obj.name_lt or obj.name_en
    else:
        form.fields['category'].label_from_instance = lambda obj: obj.name_en or obj.name_lt
    
    title = 'Create Dish' if language == 'en' else 'Sukurti patiekalą'
    return render(request, 'menu/dish_form.html', {'form': form, 'title': title, 'user_menu_language': language})


@login_required
def dish_edit(request, pk):
    """Edit an existing dish."""
    language = get_user_language(request)
    dish = get_object_or_404(Dish, pk=pk)
    
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dish updated successfully!' if language == 'en' else 'Patiekalas sėkmingai atnaujintas!')
            return redirect('user_menu:dish_list')
    else:
        form = DishForm(instance=dish)
    
    # Customize category choices to show names in selected language
    if language == 'lt':
        form.fields['category'].label_from_instance = lambda obj: obj.name_lt or obj.name_en
    else:
        form.fields['category'].label_from_instance = lambda obj: obj.name_en or obj.name_lt
    
    title = 'Edit Dish' if language == 'en' else 'Redaguoti patiekalą'
    return render(request, 'menu/dish_form.html', {'form': form, 'title': title, 'dish': dish, 'user_menu_language': language})


@login_required
def dish_delete(request, pk):
    """Delete a dish (soft delete by setting active=False)."""
    language = get_user_language(request)
    dish = get_object_or_404(Dish, pk=pk)
    
    if request.method == 'POST':
        dish.active = False
        dish.save()
        messages.success(request, 'Patiekalas deaktyvuotas sėkmingai!' if language == 'lt' else 'Dish deactivated successfully!')
        return redirect('user_menu:dish_list')
    
    return render(request, 'menu/dish_confirm_delete.html', {'dish': dish})


@login_required
def daily_menu_list(request):
    """List all daily menus."""
    menus = DailyMenu.objects.all().order_by('-date')
    return render(request, 'menu/daily_menu_list.html', {'menus': menus})


@login_required
def daily_menu_create(request):
    """Create a new daily menu."""
    language = get_user_language(request)
    
    if request.method == 'POST':
        form = DailyMenuForm(request.POST)
        if form.is_valid():
            daily_menu = form.save()
            messages.success(request, f'Dienos meniu {daily_menu.date} sukurtas sėkmingai!' if language == 'lt' else f'Daily menu for {daily_menu.date} created successfully!')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
    else:
        form = DailyMenuForm()
    
    title = 'Sukurti dienos meniu' if language == 'lt' else 'Create Daily Menu'
    return render(request, 'menu/daily_menu_form.html', {'form': form, 'title': title, 'daily_menu': None})


@login_required
def daily_menu_edit(request, pk):
    """Edit a daily menu and manage its dishes and complexes."""
    language = get_user_language(request)
    daily_menu = get_object_or_404(DailyMenu, pk=pk)
    menu_dishes = daily_menu.dishes.select_related('dish__category').order_by('dish__category__order', 'dish__name_en')
    menu_complexes = daily_menu.complexes.select_related('complex').order_by('complex__order', 'complex__name_en')
    
    # Get all active dishes not yet in this menu
    existing_dish_ids = menu_dishes.values_list('dish_id', flat=True)
    available_dishes = Dish.objects.filter(active=True).exclude(id__in=existing_dish_ids).select_related('category').order_by('category__order', 'name_en')
    
    # Get all active complexes not yet in this menu
    existing_complex_ids = menu_complexes.values_list('complex_id', flat=True)
    available_complexes = Complex.objects.filter(active=True).exclude(id__in=existing_complex_ids).order_by('order', 'name_en')
    
    if request.method == 'POST':
        # Handle published checkbox toggle
        if 'toggle_published' in request.POST:
            # Checkbox was clicked - toggle the published status
            daily_menu.published = 'published' in request.POST
            daily_menu.save()
            if daily_menu.published:
                messages.success(request, 'Meniu paskelbtas!' if language == 'lt' else 'Menu published!')
            else:
                messages.success(request, 'Meniu nupublikuotas!' if language == 'lt' else 'Menu unpublished!')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
        
        # Handle adding dish to menu
        dish_id = request.POST.get('add_dish')
        if dish_id:
            dish = get_object_or_404(Dish, pk=dish_id, active=True)
            DailyMenuDish.objects.get_or_create(
                daily_menu=daily_menu,
                dish=dish,
                defaults={'available': True}
            )
            dish_name = dish.name_lt if language == 'lt' else dish.name_en
            messages.success(request, f'{dish_name} {"pridėtas į meniu!" if language == "lt" else "added to menu!"}')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
        
        # Handle removing dish from menu
        remove_dish_id = request.POST.get('remove_dish')
        if remove_dish_id:
            menu_dish = get_object_or_404(DailyMenuDish, pk=remove_dish_id, daily_menu=daily_menu)
            menu_dish.delete()
            messages.success(request, 'Patiekalas pašalintas iš meniu!' if language == 'lt' else 'Dish removed from menu!')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
        
        # Handle adding complex to menu
        complex_id = request.POST.get('add_complex')
        if complex_id:
            complex_obj = get_object_or_404(Complex, pk=complex_id, active=True)
            DailyMenuComplex.objects.get_or_create(
                daily_menu=daily_menu,
                complex=complex_obj,
                defaults={'available': True}
            )
            complex_name = complex_obj.name_lt if language == 'lt' else complex_obj.name_en
            messages.success(request, f'{complex_name} {"pridėtas į meniu!" if language == "lt" else "added to menu!"}')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
        
        # Handle removing complex from menu
        remove_complex_id = request.POST.get('remove_complex')
        if remove_complex_id:
            menu_complex = get_object_or_404(DailyMenuComplex, pk=remove_complex_id, daily_menu=daily_menu)
            menu_complex.delete()
            messages.success(request, 'Kompleksas pašalintas iš meniu!' if language == 'lt' else 'Complex removed from menu!')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
        
        # Handle updating menu dish details
        update_dish_id = request.POST.get('update_dish')
        if update_dish_id:
            menu_dish = get_object_or_404(DailyMenuDish, pk=update_dish_id, daily_menu=daily_menu)
            menu_dish.planned_quantity = request.POST.get(f'planned_qty_{update_dish_id}') or None
            menu_dish.produced_quantity = int(request.POST.get(f'produced_qty_{update_dish_id}', 0) or 0)
            menu_dish.available = request.POST.get(f'available_{update_dish_id}') == 'on'
            menu_dish.sold_out = request.POST.get(f'sold_out_{update_dish_id}') == 'on'
            menu_dish.save()
            messages.success(request, 'Meniu patiekalas atnaujintas!' if language == 'lt' else 'Menu dish updated!')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
        
        # Handle updating menu complex details
        update_complex_id = request.POST.get('update_complex')
        if update_complex_id:
            menu_complex = get_object_or_404(DailyMenuComplex, pk=update_complex_id, daily_menu=daily_menu)
            menu_complex.available = request.POST.get(f'available_complex_{update_complex_id}') == 'on'
            menu_complex.sold_out = request.POST.get(f'sold_out_complex_{update_complex_id}') == 'on'
            menu_complex.save()
            messages.success(request, 'Meniu kompleksas atnaujintas!' if language == 'lt' else 'Menu complex updated!')
            return redirect('user_menu:daily_menu_edit', pk=daily_menu.pk)
    
    # Get all categories for filtering
    categories = Category.objects.all().order_by('order')
    
    # Get all active dishes (including those already in menu) for display
    all_dishes = Dish.objects.filter(active=True).select_related('category').order_by('category__order', 'name_en')
    
    # Get IDs of dishes already in menu for template
    menu_dish_ids = list(menu_dishes.values_list('dish_id', flat=True))
    
    # Get IDs of complexes already in menu for template
    menu_complex_ids = list(menu_complexes.values_list('complex_id', flat=True))
    
    context = {
        'daily_menu': daily_menu,
        'menu_dishes': menu_dishes,
        'menu_complexes': menu_complexes,
        'available_dishes': available_dishes,  # Dishes not yet in menu
        'available_complexes': available_complexes,  # Complexes not yet in menu
        'all_dishes': all_dishes,  # All dishes for display
        'categories': categories,  # For category filter
        'menu_dish_ids': menu_dish_ids,  # IDs of dishes already in menu
        'menu_complex_ids': menu_complex_ids,  # IDs of complexes already in menu
        'language': language,
        'user_menu_language': language,
    }
    
    return render(request, 'menu/daily_menu_edit.html', context)


@login_required
def daily_menu_preview(request, pk):
    """Preview how the daily menu will appear to customers."""
    language = get_user_language(request)
    daily_menu = get_object_or_404(DailyMenu, pk=pk)
    
    # Get only available dishes (not sold out) grouped by category
    menu_dishes = daily_menu.dishes.filter(
        available=True,
        sold_out=False
    ).select_related('dish__category').order_by('dish__category__order', 'dish__name_en')
    
    # Get only available complexes (not sold out) with their dish options
    menu_complexes = daily_menu.complexes.filter(
        available=True,
        sold_out=False
    ).select_related('complex').prefetch_related('complex__dish_options').order_by('complex__order', 'complex__name_en')
    
    # Find soups from the daily menu (dishes in soup category)
    soups = []
    for menu_dish in menu_dishes:
        category_name_en = menu_dish.dish.category.name_en.lower()
        category_name_lt = menu_dish.dish.category.name_lt.lower()
        if 'soup' in category_name_en or 'sriuba' in category_name_lt:
            soups.append(menu_dish.dish)
    
    # Find main course dishes and main light dishes
    main_course_dishes = []
    main_light_dishes = []
    pizza_dishes = []
    
    for menu_dish in menu_dishes:
        category_name_en = menu_dish.dish.category.name_en.lower()
        category_name_lt = menu_dish.dish.category.name_lt.lower()
        
        # Check if it's a main light course category
        is_main_light = ('light' in category_name_en or 'lengvas' in category_name_lt) and ('main' in category_name_en or 'pagrindinis' in category_name_lt)
        # Check if it's a main course category (but not light)
        is_main_course = ('main' in category_name_en or 'pagrindinis' in category_name_lt) and not is_main_light
        # Check if it's pizza
        is_pizza = 'pizza' in category_name_en or 'pica' in category_name_lt
        
        if is_main_light:
            main_light_dishes.append(menu_dish.dish)
        elif is_main_course:
            main_course_dishes.append(menu_dish.dish)
        elif is_pizza:
            pizza_dishes.append(menu_dish.dish)
    
    # Prepare complex display data
    complex_display_data = []
    for menu_complex in menu_complexes:
        complex_obj = menu_complex.complex
        dish_options = complex_obj.dish_options.all().order_by('order')
        
        # For each dish option, create a display entry
        for dish_option in dish_options:
            # Get soup name (first soup if available)
            soup_name = ''
            soup_size_display = ''
            if dish_option.soup_size != 'none' and soups:
                soup_dish = soups[0] if soups else None
                if soup_dish:
                    soup_name = soup_dish.name_lt if language == 'lt' else soup_dish.name_en
                    # Format soup size: half = ½ porcijos/size, full = empty
                    if dish_option.soup_size == 'half':
                        soup_size_display = ' ½ porcijos' if language == 'lt' else ' ½ size'
                    elif dish_option.soup_size == 'full':
                        soup_size_display = ''
            
            # Get main dish name based on type
            main_dish_name = ''
            main_dishes_to_use = []
            
            if dish_option.main_dish_type == 'main':
                main_dishes_to_use = main_course_dishes
            elif dish_option.main_dish_type == 'main_light':
                main_dishes_to_use = main_light_dishes
            elif dish_option.main_dish_type == 'pizza':
                main_dishes_to_use = pizza_dishes
            
            if main_dishes_to_use:
                main_dish = main_dishes_to_use[0]
                main_dish_name = main_dish.name_lt if language == 'lt' else main_dish.name_en
            
            # Format: "Soup Name ½ porcijos ir Main Dish Name" (LT) or "Soup Name ½ size and Main Dish Name" (EN)
            # Or "Soup Name ir Main Dish Name" (LT) or "Soup Name and Main Dish Name" (EN) for full size
            connector = ' ir ' if language == 'lt' else ' and '
            
            if soup_name and main_dish_name:
                if soup_size_display:
                    display_name = f"{soup_name}{soup_size_display}{connector}{main_dish_name}"
                else:
                    display_name = f"{soup_name}{connector}{main_dish_name}"
            elif soup_name:
                display_name = soup_name
            elif main_dish_name:
                display_name = main_dish_name
            else:
                # Fallback to complex name if no dishes found
                display_name = complex_obj.name_lt if language == 'lt' else complex_obj.name_en
            
            complex_display_data.append({
                'menu_complex': menu_complex,
                'display_name': display_name,
                'price': complex_obj.price,
            })
    
    # Group dishes by category, merging main light dishes into main dish category
    dishes_by_category = {}
    main_dish_category = None
    main_light_category = None
    
    for menu_dish in menu_dishes:
        category = menu_dish.dish.category
        category_name_en = category.name_en.lower()
        category_name_lt = category.name_lt.lower()
        
        # Check if it's a main light course category
        is_main_light = ('light' in category_name_en or 'lengvas' in category_name_lt) and ('main' in category_name_en or 'pagrindinis' in category_name_lt)
        # Check if it's a main course category (but not light)
        is_main_course = ('main' in category_name_en or 'pagrindinis' in category_name_lt) and not is_main_light
        
        if is_main_light:
            # Store main light category for merging later
            main_light_category = category
            # Don't add to dishes_by_category yet - will merge into main dish category
            continue
        elif is_main_course:
            # Store main dish category
            main_dish_category = category
        
        if category not in dishes_by_category:
            dishes_by_category[category] = []
        dishes_by_category[category].append(menu_dish)
    
    # Merge main light dishes into main dish category
    if main_light_category and main_dish_category:
        # Get all main light dishes
        main_light_dishes = [
            menu_dish for menu_dish in menu_dishes
            if menu_dish.dish.category == main_light_category
        ]
        
        # Add them to main dish category
        if main_dish_category not in dishes_by_category:
            dishes_by_category[main_dish_category] = []
        dishes_by_category[main_dish_category].extend(main_light_dishes)
        
        # Sort dishes in main dish category
        dishes_by_category[main_dish_category].sort(
            key=lambda md: md.dish.name_en
        )
    
    context = {
        'daily_menu': daily_menu,
        'dishes_by_category': dishes_by_category,
        'complex_display_data': complex_display_data,
        'language': language,
        'user_menu_language': language,
    }
    
    return render(request, 'menu/daily_menu_preview.html', context)


@login_required
def category_list(request):
    """List all categories with their subcategories."""
    language = get_user_language(request)
    categories = Category.objects.prefetch_related('subcategories').all().order_by('order')
    return render(request, 'menu/category_list.html', {
        'categories': categories,
        'user_menu_language': language,
    })


@login_required
def category_create(request):
    """Create a new category."""
    language = get_user_language(request)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategorija sukurta sėkmingai!' if language == 'lt' else 'Category created successfully!')
            return redirect('user_menu:category_list')
    else:
        form = CategoryForm()
    
    title = 'Sukurti kategoriją' if language == 'lt' else 'Create Category'
    return render(request, 'menu/category_form.html', {'form': form, 'title': title})


@login_required
def category_edit(request, pk):
    """Edit an existing category."""
    language = get_user_language(request)
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategorija atnaujinta sėkmingai!' if language == 'lt' else 'Category updated successfully!')
            return redirect('user_menu:category_list')
    else:
        form = CategoryForm(instance=category)
    
    title = 'Redaguoti kategoriją' if language == 'lt' else 'Edit Category'
    return render(request, 'menu/category_form.html', {'form': form, 'title': title, 'category': category})


@login_required
def category_delete(request, pk):
    """Delete a category."""
    language = get_user_language(request)
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        # Check if category has dishes
        if category.dishes.exists():
            cat_name = category.name_lt if language == 'lt' else category.name_en
            dish_count = category.dishes.count()
            if language == 'lt':
                dish_word = 'patiekalą' if dish_count == 1 else 'patiekalus'
                messages.error(request, f'Negalima ištrinti kategorijos "{cat_name}", nes ji turi {dish_count} {dish_word}. Pirmiausia pašalinkite arba perpriskirkite patiekalus.')
            else:
                messages.error(request, f'Cannot delete category "{cat_name}" because it has {dish_count} dish(es). Please remove or reassign dishes first.')
            return redirect('user_menu:category_list')
        
        category.delete()
        messages.success(request, 'Kategorija ištrinta sėkmingai!' if language == 'lt' else 'Category deleted successfully!')
        return redirect('user_menu:category_list')
    
    return render(request, 'menu/category_confirm_delete.html', {'category': category})


@login_required
def subcategory_create(request, category_pk):
    """Create a new subcategory for a category."""
    language = get_user_language(request)
    category = get_object_or_404(Category, pk=category_pk)
    
    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            subcategory = form.save(commit=False)
            subcategory.category = category
            subcategory.save()
            messages.success(request, 'Subkategorija sukurta sėkmingai!' if language == 'lt' else 'Subcategory created successfully!')
            return redirect('user_menu:category_list')
    else:
        form = SubcategoryForm(initial={'category': category})
        form.fields['category'].widget = forms.HiddenInput()
    
    title = f'{"Sukurti subkategoriją" if language == "lt" else "Create Subcategory"} - {category.name_lt if language == "lt" else category.name_en}'
    return render(request, 'menu/subcategory_form.html', {
        'form': form,
        'title': title,
        'category': category,
        'user_menu_language': language,
    })


@login_required
def subcategory_edit(request, pk):
    """Edit an existing subcategory."""
    language = get_user_language(request)
    subcategory = get_object_or_404(Subcategory, pk=pk)
    
    if request.method == 'POST':
        form = SubcategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subkategorija atnaujinta sėkmingai!' if language == 'lt' else 'Subcategory updated successfully!')
            return redirect('user_menu:category_list')
    else:
        form = SubcategoryForm(instance=subcategory)
    
    title = f'{"Redaguoti subkategoriją" if language == "lt" else "Edit Subcategory"} - {subcategory.name_lt if language == "lt" else subcategory.name_en}'
    return render(request, 'menu/subcategory_form.html', {
        'form': form,
        'title': title,
        'category': subcategory.category,
        'user_menu_language': language,
    })


@login_required
def subcategory_delete(request, pk):
    """Delete a subcategory."""
    language = get_user_language(request)
    subcategory = get_object_or_404(Subcategory, pk=pk)
    
    if request.method == 'POST':
        # Check if subcategory has dishes
        if subcategory.dishes.exists():
            subcat_name = subcategory.name_lt if language == 'lt' else subcategory.name_en
            dish_count = subcategory.dishes.count()
            if language == 'lt':
                dish_word = 'patiekalą' if dish_count == 1 else 'patiekalus'
                messages.error(request, f'Negalima ištrinti subkategorijos "{subcat_name}", nes ji turi {dish_count} {dish_word}.')
            else:
                dish_word = 'dish' if dish_count == 1 else 'dishes'
                messages.error(request, f'Cannot delete subcategory "{subcat_name}" because it has {dish_count} {dish_word}.')
            return redirect('user_menu:category_list')
        
        subcategory.delete()
        messages.success(request, 'Subkategorija ištrinta sėkmingai!' if language == 'lt' else 'Subcategory deleted successfully!')
        return redirect('user_menu:category_list')
    
    return render(request, 'menu/subcategory_confirm_delete.html', {
        'subcategory': subcategory,
        'user_menu_language': language,
    })


@login_required
def complex_list(request):
    """List all complexes."""
    language = get_user_language(request)
    complexes = Complex.objects.prefetch_related('dish_options').all().order_by('order', 'name_en')
    
    context = {
        'complexes': complexes,
        'user_menu_language': language,
    }
    return render(request, 'menu/complex_list.html', context)


@login_required
def complex_create(request):
    """Create a new complex."""
    language = get_user_language(request)
    
    if request.method == 'POST':
        form = ComplexForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Complex created successfully!' if language == 'en' else 'Kompleksas sėkmingai sukurtas!')
            return redirect('user_menu:complex_list')
    else:
        form = ComplexForm()
    
    title = 'Create Complex' if language == 'en' else 'Sukurti kompleksą'
    return render(request, 'menu/complex_form.html', {'form': form, 'title': title, 'user_menu_language': language})


@login_required
def complex_edit(request, pk):
    """Edit an existing complex."""
    language = get_user_language(request)
    complex_obj = get_object_or_404(Complex, pk=pk)
    
    if request.method == 'POST':
        form = ComplexForm(request.POST, instance=complex_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Complex updated successfully!' if language == 'en' else 'Kompleksas sėkmingai atnaujintas!')
            return redirect('user_menu:complex_list')
    else:
        form = ComplexForm(instance=complex_obj)
    
    title = 'Edit Complex' if language == 'en' else 'Redaguoti kompleksą'
    return render(request, 'menu/complex_form.html', {'form': form, 'title': title, 'complex': complex_obj, 'user_menu_language': language})


@login_required
def complex_delete(request, pk):
    """Delete a complex (soft delete by setting active=False)."""
    language = get_user_language(request)
    complex_obj = get_object_or_404(Complex, pk=pk)
    
    if request.method == 'POST':
        complex_obj.active = False
        complex_obj.save()
        messages.success(request, 'Complex deactivated successfully!' if language == 'en' else 'Kompleksas sėkmingai deaktyvuotas!')
        return redirect('user_menu:complex_list')
    
    return render(request, 'menu/complex_confirm_delete.html', {
        'complex': complex_obj,
        'user_menu_language': language,
    })


@login_required
def complex_dish_list(request, complex_pk):
    """List dish options for a complex."""
    language = get_user_language(request)
    complex_obj = get_object_or_404(Complex, pk=complex_pk)
    complex_dishes = ComplexDish.objects.filter(complex=complex_obj).order_by('order')
    
    context = {
        'complex': complex_obj,
        'complex_dishes': complex_dishes,
        'user_menu_language': language,
    }
    return render(request, 'menu/complex_dish_list.html', context)


@login_required
def complex_dish_create(request, complex_pk):
    """Add a dish option to a complex."""
    language = get_user_language(request)
    complex_obj = get_object_or_404(Complex, pk=complex_pk)
    
    if request.method == 'POST':
        form = ComplexDishForm(request.POST)
        if form.is_valid():
            complex_dish = form.save(commit=False)
            complex_dish.complex = complex_obj
            complex_dish.save()
            messages.success(request, 'Dish option added successfully!' if language == 'en' else 'Patiekalo parinktis sėkmingai pridėta!')
            return redirect('user_menu:complex_dish_list', complex_pk=complex_pk)
    else:
        form = ComplexDishForm(initial={'complex': complex_obj})
        form.fields['complex'].widget = forms.HiddenInput()
    
    title = 'Add Dish Option' if language == 'en' else 'Pridėti patiekalo parinktį'
    return render(request, 'menu/complex_dish_form.html', {
        'form': form,
        'title': title,
        'complex': complex_obj,
        'user_menu_language': language,
    })


@login_required
def complex_dish_delete(request, pk):
    """Delete a dish option from a complex."""
    language = get_user_language(request)
    complex_dish = get_object_or_404(ComplexDish, pk=pk)
    complex_pk = complex_dish.complex.pk
    
    if request.method == 'POST':
        complex_dish.delete()
        messages.success(request, 'Dish option deleted successfully!' if language == 'en' else 'Patiekalo parinktis sėkmingai pašalinta!')
        return redirect('user_menu:complex_dish_list', complex_pk=complex_pk)
    
    return render(request, 'menu/complex_dish_confirm_delete.html', {
        'complex_dish': complex_dish,
        'user_menu_language': language,
    })


@login_required
@require_http_methods(["POST"])
def complex_update_dish_options(request, pk):
    """Update complex dish options via AJAX."""
    language = get_user_language(request)
    complex_obj = get_object_or_404(Complex, pk=pk)
    
    # Get soup sizes, dish types, and drinks from POST data
    soup_sizes = request.POST.getlist('soup_sizes[]')
    dish_types = request.POST.getlist('dish_types[]')
    include_drinks = request.POST.getlist('include_drinks[]')
    
    # Delete existing options
    complex_obj.dish_options.all().delete()
    
    # Create new options based on combinations
    order = 0
    for soup_size in soup_sizes:
        for dish_type in dish_types:
            for include_drink_str in include_drinks:
                include_drink = include_drink_str.lower() == 'true'
                ComplexDish.objects.create(
                    complex=complex_obj,
                    soup_size=soup_size,
                    main_dish_type=dish_type,
                    include_drink=include_drink,
                    order=order
                )
                order += 1
    
    return JsonResponse({
        'success': True,
        'message': 'Complex options updated successfully!' if language == 'en' else 'Komplekso parinktys sėkmingai atnaujintos!'
    })


@login_required
def get_subcategories(request):
    """API endpoint to fetch subcategories for a given category."""
    category_id = request.GET.get('category_id')
    
    if not category_id:
        return JsonResponse({'subcategories': []})
    
    try:
        subcategories = Subcategory.objects.filter(category_id=category_id).order_by('order', 'name_en')
        subcategories_data = [
            {
                'id': subcat.id,
                'name_en': subcat.name_en,
                'name_lt': subcat.name_lt,
            }
            for subcat in subcategories
        ]
        return JsonResponse({'subcategories': subcategories_data})
    except (ValueError, Category.DoesNotExist):
        return JsonResponse({'subcategories': []})

