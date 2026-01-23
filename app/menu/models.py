"""
Menu models for Krapesto restaurant.

This module contains models for managing menu categories, dishes, and daily menus.
Designed to support future expansion with inventory, kitchen, and bar modules.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    """
    Menu category (e.g., "Main Courses", "Desserts", "Beverages").
    
    Categories are ordered by the 'order' field for consistent display.
    """
    name_lt = models.CharField(max_length=100, verbose_name="Name (Lithuanian)")
    name_en = models.CharField(max_length=100, verbose_name="Name (English)")
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name_en']

    def __str__(self):
        return f"{self.name_en} ({self.name_lt})"


class Subcategory(models.Model):
    """
    Subcategory for categories (e.g., "Beer", "Wine", "Lemonade" under "Drinks").
    
    Subcategories are used to further classify dishes within a category.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name="Category",
        help_text="Parent category for this subcategory"
    )
    name_lt = models.CharField(max_length=100, verbose_name="Name (Lithuanian)")
    name_en = models.CharField(max_length=100, verbose_name="Name (English)")
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        ordering = ['category', 'order', 'name_en']

    def __str__(self):
        return f"{self.name_en} ({self.name_lt}) - {self.category.name_en}"


class Dish(models.Model):
    """
    A dish/item that can be added to daily menus.
    
    Dishes are reusable across multiple daily menus.
    The 'active' field allows soft-deletion without removing historical data.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='dishes',
        verbose_name="Category"
    )
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dishes',
        verbose_name="Subcategory",
        help_text="Optional subcategory (e.g., Beer, Wine, Lemonade for Drinks)"
    )
    name_lt = models.CharField(max_length=200, verbose_name="Name (Lithuanian)")
    name_en = models.CharField(max_length=200, verbose_name="Name (English)")
    ingredients_lt = models.TextField(
        blank=True,
        verbose_name="Ingredients (Lithuanian)",
        help_text="List of ingredients in Lithuanian"
    )
    ingredients_en = models.TextField(
        blank=True,
        verbose_name="Ingredients (English)",
        help_text="List of ingredients in English"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Price (Full Size)",
        help_text="Price in EUR for full size"
    )
    half_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name="Price (Half Size)",
        help_text="Price in EUR for half size (optional, mainly for soups)"
    )
    image = models.ImageField(
        upload_to='dishes/',
        blank=True,
        null=True,
        verbose_name="Image",
        help_text="Upload dish image"
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this dish is currently available for menu planning"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dish"
        verbose_name_plural = "Dishes"
        ordering = ['category__order', 'category', 'name_en']

    def __str__(self):
        return f"{self.name_en} - €{self.price}"


class DailyMenu(models.Model):
    """
    Represents a daily menu for a specific date.
    
    Only published menus should be visible to customers.
    This allows menu planning in advance.
    """
    date = models.DateField(
        unique=True,
        verbose_name="Date",
        help_text="Date for this daily menu (YYYY-MM-DD)"
    )
    published = models.BooleanField(
        default=False,
        verbose_name="Published",
        help_text="Whether this menu is visible to customers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Daily Menu"
        verbose_name_plural = "Daily Menus"
        ordering = ['-date']

    def __str__(self):
        status = "Published" if self.published else "Draft"
        return f"Menu for {self.date} ({status})"


class DailyMenuDish(models.Model):
    """
    Junction model linking dishes to daily menus.
    
    Tracks production and availability for each dish on a specific day.
    This supports future kitchen/inventory integration.
    """
    daily_menu = models.ForeignKey(
        DailyMenu,
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name="Daily Menu"
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.PROTECT,
        related_name='daily_menu_entries',
        verbose_name="Dish"
    )
    planned_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Planned Quantity",
        help_text="Quantity planned for production (nullable for flexibility)"
    )
    produced_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Produced Quantity",
        help_text="Actual quantity produced"
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Available",
        help_text="Whether this dish is currently available for ordering"
    )
    sold_out = models.BooleanField(
        default=False,
        verbose_name="Sold Out",
        help_text="Whether this dish has been sold out"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Daily Menu Dish"
        verbose_name_plural = "Daily Menu Dishes"
        ordering = ['dish__category__order', 'dish__category', 'dish__name_en']
        unique_together = ['daily_menu', 'dish']  # Prevent duplicate dishes in same menu

    def __str__(self):
        return f"{self.dish.name_en} - {self.daily_menu.date}"


class DailyMenuComplex(models.Model):
    """
    Junction model linking complexes to daily menus.
    
    Tracks availability for each complex on a specific day.
    """
    daily_menu = models.ForeignKey(
        DailyMenu,
        on_delete=models.CASCADE,
        related_name='complexes',
        verbose_name="Daily Menu"
    )
    complex = models.ForeignKey(
        'Complex',
        on_delete=models.CASCADE,
        related_name='daily_menus',
        verbose_name="Complex"
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Available",
        help_text="Whether this complex is currently available for ordering"
    )
    sold_out = models.BooleanField(
        default=False,
        verbose_name="Sold Out",
        help_text="Whether this complex has been sold out"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Daily Menu Complex"
        verbose_name_plural = "Daily Menu Complexes"
        ordering = ['complex__order', 'complex__name_en']
        unique_together = ['daily_menu', 'complex']  # Prevent duplicate complexes in same menu

    def __str__(self):
        return f"{self.complex.name_en} - {self.daily_menu.date}"


class Complex(models.Model):
    """
    Represents a meal complex/kompleksas (combo meal).
    
    A complex consists of a soup (with size option) and a main dish at a combined price.
    """
    name_lt = models.CharField(max_length=200, verbose_name="Name (Lithuanian)", help_text="e.g., Kompleksas 1")
    name_en = models.CharField(max_length=200, verbose_name="Name (English)", help_text="e.g., Complex 1")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Price",
        help_text="Total price for the complex in EUR"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display (lower numbers appear first)"
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this complex is currently available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Complex"
        verbose_name_plural = "Complexes"
        ordering = ['order', 'name_en']

    def __str__(self):
        return f"{self.name_en} - €{self.price}"


class ComplexDish(models.Model):
    """
    Links dish options to complexes.
    
    Each complex can have multiple dish options (soup size + main dish type combinations).
    """
    SOUP_SIZE_CHOICES = [
        ('none', 'None'),
        ('half', 'Half'),
        ('full', 'Full'),
    ]
    
    MAIN_DISH_TYPE_CHOICES = [
        ('main', 'Main Dish'),
        ('main_light', 'Main Light Dish'),
        ('pizza', 'Pizza'),
    ]

    complex = models.ForeignKey(
        Complex,
        on_delete=models.CASCADE,
        related_name='dish_options',
        verbose_name="Complex"
    )
    soup_size = models.CharField(
        max_length=10,
        choices=SOUP_SIZE_CHOICES,
        default='half',
        verbose_name="Soup Size",
        help_text="Size of the soup (half or full)"
    )
    main_dish_type = models.CharField(
        max_length=20,
        choices=MAIN_DISH_TYPE_CHOICES,
        default='main',
        verbose_name="Main Dish Type",
        help_text="Type of main dish (main dish or main light dish)"
    )
    include_drink = models.BooleanField(
        default=False,
        verbose_name="Include Drink",
        help_text="Whether to include a drink from the Drinks category"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display within the complex"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Complex Dish Option"
        verbose_name_plural = "Complex Dish Options"
        ordering = ['complex__order', 'complex', 'order']
        unique_together = ['complex', 'soup_size', 'main_dish_type', 'include_drink']  # Prevent duplicates

    def __str__(self):
        soup_size_display = dict(self.SOUP_SIZE_CHOICES)[self.soup_size]
        main_dish_display = dict(self.MAIN_DISH_TYPE_CHOICES)[self.main_dish_type]
        return f"{self.complex.name_en}: {soup_size_display} soup + {main_dish_display}"

