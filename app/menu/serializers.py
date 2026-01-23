"""
Serializers for menu API endpoints.
"""
from rest_framework import serializers
from .models import Category, Dish, DailyMenu, DailyMenuDish, Complex, ComplexDish


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    class Meta:
        model = Category
        fields = ['id', 'name_lt', 'name_en', 'order']


class DishSerializer(serializers.ModelSerializer):
    """Serializer for Dish model."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Dish
        fields = [
            'id', 'category', 'category_id',
            'name_lt', 'name_en',
            'ingredients_lt', 'ingredients_en',
            'price', 'half_price', 'image', 'active'
        ]


class DailyMenuDishSerializer(serializers.ModelSerializer):
    """Serializer for DailyMenuDish with nested dish information."""
    dish = DishSerializer(read_only=True)
    dish_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = DailyMenuDish
        fields = [
            'id', 'dish', 'dish_id',
            'planned_quantity', 'produced_quantity',
            'available', 'sold_out', 'updated_at'
        ]


class DailyMenuSerializer(serializers.ModelSerializer):
    """Serializer for DailyMenu with nested dishes."""
    dishes = DailyMenuDishSerializer(many=True, read_only=True, source='dishes.all')

    class Meta:
        model = DailyMenu
        fields = ['id', 'date', 'published', 'dishes', 'created_at', 'updated_at']


class ComplexDishSerializer(serializers.ModelSerializer):
    """Serializer for ComplexDish."""
    
    class Meta:
        model = ComplexDish
        fields = ['id', 'soup_size', 'main_dish_type', 'order']


class ComplexSerializer(serializers.ModelSerializer):
    """Serializer for Complex with nested dish options."""
    dish_options = ComplexDishSerializer(many=True, read_only=True, source='dish_options.all')
    
    class Meta:
        model = Complex
        fields = ['id', 'name_lt', 'name_en', 'price', 'order', 'active', 'dish_options']


class LunchMenuResponseSerializer(serializers.Serializer):
    """
    Custom serializer for lunch menu API responses.
    Groups dishes by category for easier frontend consumption.
    """
    date = serializers.DateField()
    published = serializers.BooleanField()
    categories = serializers.SerializerMethodField()
    complexes = serializers.SerializerMethodField()

    def to_representation(self, instance):
        """Explicitly read date and published from the DailyMenu instance."""
        return {
            'date': instance.date,
            'published': instance.published,  # STRICT: Read directly from model
            'categories': self.get_categories(instance),
            'complexes': self.get_complexes(),
        }
    
    def get_complexes(self):
        """Get all active complexes with matched dishes from daily menu."""
        obj = self.instance  # The DailyMenu instance
        complexes = Complex.objects.filter(active=True).prefetch_related('dish_options').order_by('order')
        
        # Get available dishes from this daily menu
        daily_menu_dishes = obj.dishes.filter(available=True, sold_out=False).select_related('dish__category')
        
        # Find soups (dishes with half_price, typically soups)
        soups = [md.dish for md in daily_menu_dishes if md.dish.half_price is not None]
        
        # Find main course dishes (from "main course" category)
        # Try to identify by category name
        main_course_dishes = []
        main_light_dishes = []
        
        for menu_dish in daily_menu_dishes:
            category_name_en = menu_dish.dish.category.name_en.lower()
            category_name_lt = menu_dish.dish.category.name_lt.lower()
            
            # Check if it's a main light course category
            is_main_light = ('light' in category_name_en or 'lengvas' in category_name_lt) and ('main' in category_name_en or 'pagrindinis' in category_name_lt)
            # Check if it's a main course category (but not light)
            is_main_course = ('main' in category_name_en or 'pagrindinis' in category_name_lt) and not is_main_light
            
            if is_main_light:
                main_light_dishes.append(menu_dish.dish)
            elif is_main_course:
                main_course_dishes.append(menu_dish.dish)
        
        complexes_list = []
        request = self.context.get('request')
        
        for complex_obj in complexes:
            dish_options_list = []
            
            for complex_dish in complex_obj.dish_options.all():
                # Skip if soup_size is 'none' - no soup needed
                if complex_dish.soup_size == 'none':
                    soups_to_use = [None]  # Use None to indicate no soup
                else:
                    # Only create combinations if we have soups available
                    if not soups:
                        continue
                    soups_to_use = soups
                
                # Determine which main dishes to use based on main_dish_type
                if complex_dish.main_dish_type == 'main':
                    main_dishes_to_use = main_course_dishes
                elif complex_dish.main_dish_type == 'main_light':
                    main_dishes_to_use = main_light_dishes
                elif complex_dish.main_dish_type == 'pizza':
                    # Find pizza dishes (from "pizza" category)
                    main_dishes_to_use = []
                    for menu_dish in daily_menu_dishes:
                        category_name_en = menu_dish.dish.category.name_en.lower()
                        category_name_lt = menu_dish.dish.category.name_lt.lower()
                        if 'pizza' in category_name_en or 'pica' in category_name_lt:
                            main_dishes_to_use.append(menu_dish.dish)
                else:
                    main_dishes_to_use = []
                
                # Only create combinations if we have main dishes available
                if not main_dishes_to_use:
                    continue
                
                # Create a combination for each soup (or None) with each main dish
                for soup in soups_to_use:
                    for main_dish in main_dishes_to_use:
                        # Only add if main_dish has names (soup can be None)
                        if not (main_dish.name_lt and main_dish.name_en):
                            continue
                        
                        # If soup is provided, check it has names
                        if soup and not (soup.name_lt and soup.name_en):
                            continue
                        
                        # Build image URLs
                        soup_image_url = None
                        main_dish_image_url = None
                        
                        if soup and soup.image:
                            if request:
                                soup_image_url = request.build_absolute_uri(soup.image.url)
                            else:
                                soup_image_url = soup.image.url
                        
                        if main_dish.image:
                            if request:
                                main_dish_image_url = request.build_absolute_uri(main_dish.image.url)
                            else:
                                main_dish_image_url = main_dish.image.url
                        
                        dish_options_list.append({
                            'id': complex_dish.id,
                            'soup': {
                                'id': soup.id if soup else None,
                                'name_lt': soup.name_lt if soup else '',
                                'name_en': soup.name_en if soup else '',
                                'image': soup_image_url,
                            } if soup else None,
                            'soup_size': complex_dish.soup_size,
                            'main_dish': {
                                'id': main_dish.id,
                                'name_lt': main_dish.name_lt,
                                'name_en': main_dish.name_en,
                                'image': main_dish_image_url,
                            },
                            'main_dish_type': complex_dish.main_dish_type,
                            'include_drink': complex_dish.include_drink,
                            'order': complex_dish.order,
                        })
            
            if dish_options_list:  # Only include complexes with at least one matched option
                complexes_list.append({
                    'id': complex_obj.id,
                    'name_lt': complex_obj.name_lt,
                    'name_en': complex_obj.name_en,
                    'price': str(complex_obj.price),
                    'order': complex_obj.order,
                    'dish_options': dish_options_list,
                })
        
        return complexes_list

    def get_categories(self, obj):
        """Group dishes by category, merging main light dishes into main dish category."""
        daily_menu_dishes = obj.dishes.filter(available=True, sold_out=False).select_related('dish__category')
        
        # Group by category
        categories_dict = {}
        main_dish_category_id = None
        main_light_category_id = None
        
        for menu_dish in daily_menu_dishes:
            category = menu_dish.dish.category
            category_name_en = category.name_en.lower()
            category_name_lt = category.name_lt.lower()
            
            # Check if it's a main light course category
            is_main_light = ('light' in category_name_en or 'lengvas' in category_name_lt) and ('main' in category_name_en or 'pagrindinis' in category_name_lt)
            # Check if it's a main course category (but not light)
            is_main_course = ('main' in category_name_en or 'pagrindinis' in category_name_lt) and not is_main_light
            
            if is_main_light:
                # Store main light category ID for merging later
                main_light_category_id = category.id
                # Don't add to categories_dict yet - will merge into main dish category
                continue
            elif is_main_course:
                # Store main dish category ID
                main_dish_category_id = category.id
            
            if category.id not in categories_dict:
                categories_dict[category.id] = {
                    'id': category.id,
                    'name_lt': category.name_lt,
                    'name_en': category.name_en,
                    'order': category.order,
                    'dishes': []
                }
            
            # Add dish information
            image_url = None
            if menu_dish.dish.image:
                request = self.context.get('request')
                if request:
                    image_url = request.build_absolute_uri(menu_dish.dish.image.url)
                else:
                    image_url = menu_dish.dish.image.url
            
            dish_data = {
                'id': menu_dish.dish.id,
                'name_lt': menu_dish.dish.name_lt,
                'name_en': menu_dish.dish.name_en,
                'ingredients_lt': menu_dish.dish.ingredients_lt,
                'ingredients_en': menu_dish.dish.ingredients_en,
                'price': str(menu_dish.dish.price),
                'half_price': str(menu_dish.dish.half_price) if menu_dish.dish.half_price else None,
                'image': image_url,
                'available': menu_dish.available,
                'sold_out': menu_dish.sold_out,
            }
            categories_dict[category.id]['dishes'].append(dish_data)
        
        # Merge main light dishes into main dish category
        if main_light_category_id and main_dish_category_id and main_dish_category_id in categories_dict:
            # Get all main light dishes
            main_light_dishes = []
            for menu_dish in daily_menu_dishes:
                if menu_dish.dish.category.id == main_light_category_id:
                    image_url = None
                    if menu_dish.dish.image:
                        request = self.context.get('request')
                        if request:
                            image_url = request.build_absolute_uri(menu_dish.dish.image.url)
                        else:
                            image_url = menu_dish.dish.image.url
                    
                    dish_data = {
                        'id': menu_dish.dish.id,
                        'name_lt': menu_dish.dish.name_lt,
                        'name_en': menu_dish.dish.name_en,
                        'ingredients_lt': menu_dish.dish.ingredients_lt,
                        'ingredients_en': menu_dish.dish.ingredients_en,
                        'price': str(menu_dish.dish.price),
                        'half_price': str(menu_dish.dish.half_price) if menu_dish.dish.half_price else None,
                        'image': image_url,
                        'available': menu_dish.available,
                        'sold_out': menu_dish.sold_out,
                    }
                    main_light_dishes.append(dish_data)
            
            # Add main light dishes to main dish category
            categories_dict[main_dish_category_id]['dishes'].extend(main_light_dishes)
        
        # Remove main light category from the list if it exists
        if main_light_category_id and main_light_category_id in categories_dict:
            del categories_dict[main_light_category_id]
        
        # Sort categories by order, then by name
        categories_list = sorted(
            categories_dict.values(),
            key=lambda x: (x['order'], x['name_en'])
        )
        
        # Sort dishes within each category
        for category in categories_list:
            category['dishes'].sort(key=lambda x: x['name_en'])
        
        return categories_list

