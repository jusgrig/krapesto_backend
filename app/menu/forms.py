"""
Forms for menu management in user interface.
"""
from django import forms
from .models import Category, Subcategory, Dish, DailyMenu, DailyMenuDish, Complex, ComplexDish


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories."""
    class Meta:
        model = Category
        fields = ['name_en', 'name_lt', 'order']
        widgets = {
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name in English'}),
            'name_lt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name in Lithuanian'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class SubcategoryForm(forms.ModelForm):
    """Form for creating/editing subcategories."""
    class Meta:
        model = Subcategory
        fields = ['category', 'name_en', 'name_lt', 'order']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subcategory name in English'}),
            'name_lt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subcategory name in Lithuanian'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class DishForm(forms.ModelForm):
    """Form for creating/editing dishes."""
    class Meta:
        model = Dish
        fields = ['category', 'subcategory', 'name_en', 'name_lt', 'ingredients_en', 'ingredients_lt', 'price', 'half_price', 'image', 'active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'subcategory': forms.Select(attrs={'class': 'form-control', 'id': 'id_subcategory'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dish name in English'}),
            'name_lt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dish name in Lithuanian'}),
            'ingredients_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingredients in English'}),
            'ingredients_lt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingredients in Lithuanian'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Full size price'}),
            'half_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Half size price (optional, for soups)'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set subcategory queryset based on selected category
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id).order_by('order', 'name_en')
            except (ValueError, TypeError):
                self.fields['subcategory'].queryset = Subcategory.objects.none()
        elif self.instance.pk:
            # If editing existing dish, show subcategories for its category
            self.fields['subcategory'].queryset = Subcategory.objects.filter(category=self.instance.category).order_by('order', 'name_en')
        else:
            # Initial load - no subcategories shown
            self.fields['subcategory'].queryset = Subcategory.objects.none()
        
        # Make subcategory optional
        self.fields['subcategory'].required = False


class DailyMenuForm(forms.ModelForm):
    """Form for creating/editing daily menus."""
    class Meta:
        model = DailyMenu
        fields = ['date', 'published']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ComplexForm(forms.ModelForm):
    """Form for creating/editing complexes."""
    class Meta:
        model = Complex
        fields = ['name_en', 'name_lt', 'price', 'order', 'active']
        widgets = {
            'name_en': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complex name in English (e.g., Complex 1)'}),
            'name_lt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complex name in Lithuanian (e.g., Kompleksas 1)'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Total price'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ComplexDishForm(forms.ModelForm):
    """Form for adding dish options to complexes."""
    class Meta:
        model = ComplexDish
        fields = ['complex', 'soup_size', 'main_dish_type', 'include_drink', 'order']
        widgets = {
            'complex': forms.Select(attrs={'class': 'form-control'}),
            'soup_size': forms.Select(attrs={'class': 'form-control'}),
            'main_dish_type': forms.Select(attrs={'class': 'form-control'}),
            'include_drink': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

